from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session
import models
import pypdf
import re

def extract_file_metadata(content: bytes, is_pdf: bool = False):
    """
    Extrai metadados do cabeçalho do arquivo (Account Identifier e Date Range)
    Retorna: dict com 'alvo_numero', 'periodo_inicio', 'periodo_fim'
    """
    metadata = {
        'alvo_numero': None,
        'periodo_inicio': None,
        'periodo_fim': None
    }
    
    try:
        if is_pdf:
            return metadata
        
        # Decodificar conteúdo
        html_text = content.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 1. Tentar extrair do texto limpo (sem tags)
        clean_text = soup.get_text(separator=' ', strip=True)
        print(f"🔍 Texto limpo (início): {clean_text[:200]}...")
        
        # Regex para Account Identifier (flexível)
        account_match = re.search(r'Account\s+Identifier\s*:?\s*(\+?\d{10,15})', clean_text, re.IGNORECASE)
        if account_match:
            metadata['alvo_numero'] = account_match.group(1) if account_match.group(1).startswith('+') else '+' + account_match.group(1)
            print(f"✅ Alvo extraído (texto limpo): {metadata['alvo_numero']}")
        
        # Regex para Date Range
        date_match = re.search(
            r'Date\s+Range\s*:?\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+UTC\s+to\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            clean_text,
            re.IGNORECASE
        )
        if date_match:
            metadata['periodo_inicio'] = date_match.group(1)
            metadata['periodo_fim'] = date_match.group(2)
            print(f"✅ Período extraído (texto limpo): {metadata['periodo_inicio']} -> {metadata['periodo_fim']}")

        # 2. Fallback: Se falhar, tentar no HTML bruto
        if not metadata['alvo_numero']:
            print("⚠️ Tentando fallback no HTML bruto para Alvo...")
            account_match_raw = re.search(r'Account\s+Identifier[^<]*(\+?\d{10,15})', html_text, re.IGNORECASE)
            if account_match_raw:
                metadata['alvo_numero'] = account_match_raw.group(1)
                print(f"✅ Alvo extraído (HTML bruto): {metadata['alvo_numero']}")

    except Exception as e:
        print(f"❌ Erro ao extrair metadados: {e}")
        import traceback
        traceback.print_exc()
    
    return metadata
def _process_data_list(data_list: list, operacao_id: int, db: Session):
    processed_count = 0
    skipped_count = 0
    skip_reasons = {
        'sem_tipo': 0,
        'sem_remetente_destinatario': 0,
        'sem_data': 0,
        'sem_alvo': 0,
        'sem_ip': 0,
        'dados_incompletos': 0
    }
    ips_cache = {}
    telefones_cache = {}
    
    # Listas para batch insert
    mensagens_batch = []
    BATCH_SIZE = 500  # Commit a cada 500 mensagens

    for idx, data in enumerate(data_list):
        # Validar campos críticos - TODOS SÃO OBRIGATÓRIOS
        
        # Verificar tipo (obrigatório)
        tipo_msg = data.get('TIPO')
        if not tipo_msg or tipo_msg.strip() == '':
            skip_reasons['sem_tipo'] += 1
            skipped_count += 1
            continue
        
        # Verificar remetente (obrigatório)
        remetente = data.get('REMETENTE')
        if not remetente or remetente.strip() == '':
            skip_reasons['sem_remetente_destinatario'] += 1
            skipped_count += 1
            continue
        
        # Verificar destinatário (obrigatório)
        destinatario = data.get('DESTINATÁRIO')
        if not destinatario or destinatario.strip() == '':
            skip_reasons['sem_remetente_destinatario'] += 1
            skipped_count += 1
            continue
        
        # Verificar data/hora (obrigatório)
        if not data.get('DATA') or data.get('DATA').strip() == '':
            skip_reasons['sem_data'] += 1
            skipped_count += 1
            continue
        
        # Verificar IP (obrigatório)
        if not data.get('IP') or data.get('IP').strip() == '':
            skip_reasons['sem_ip'] += 1
            skipped_count += 1
            continue

        # Processar IP
        ip_id = None
        ip_addr = data.get('IP')
        if ip_addr:
            if ip_addr not in ips_cache:
                existing_ip = db.query(models.IP).filter(models.IP.endereco == ip_addr).first()
                if not existing_ip:
                    new_ip = models.IP(endereco=ip_addr)
                    db.add(new_ip)
                    db.flush()  # Necessário para pegar o ID
                    ips_cache[ip_addr] = new_ip.id
                else:
                    ips_cache[ip_addr] = existing_ip.id
            ip_id = ips_cache[ip_addr]

        # Processar Telefones
        for role in ['ALVO', 'REMETENTE', 'DESTINATÁRIO']:
            num = data.get(role)
            if num:
                if num not in telefones_cache:
                    existing_tel = db.query(models.Telefone).filter(
                        models.Telefone.operacao_id == operacao_id,
                        models.Telefone.numero == num
                    ).first()
                    
                    if not existing_tel:
                        tipo = 'ALVO' if role == 'ALVO' else 'SECUNDARIO'
                        new_tel = models.Telefone(
                            operacao_id=operacao_id,
                            numero=num,
                            tipo=tipo
                        )
                        db.add(new_tel)
                        db.flush()  # Necessário para pegar o ID
                        telefones_cache[num] = new_tel.id
                    else:
                        telefones_cache[num] = existing_tel.id
                        if role == 'ALVO' and existing_tel.tipo != 'ALVO':
                            existing_tel.tipo = 'ALVO'

        # Preparar dados da Mensagem para batch insert
        try:
            dt = None
            if data.get('DATA'):
                # Remover UTC se existir
                date_str = data['DATA'].replace(' UTC', '')
                formats = ['%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']
                for fmt in formats:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        break
                    except:
                        pass
            
            porta = None
            if data.get('PORTA') and str(data['PORTA']).isdigit():
                porta = int(data['PORTA'])

            # Adicionar ao batch em vez de insert individual
            mensagens_batch.append({
                'operacao_id': operacao_id,
                'alvo': data.get('ALVO'),
                'remetente': data.get('REMETENTE'),
                'destinatario': data.get('DESTINATÁRIO'),
                'ip_id': ip_id,
                'porta': porta,
                'data_hora': dt,
                'tipo_mensagem': data.get('TIPO')
            })
            processed_count += 1
            
            # Commit em lotes para melhor performance
            if len(mensagens_batch) >= BATCH_SIZE:
                db.bulk_insert_mappings(models.Mensagem, mensagens_batch)
                db.commit()
                mensagens_batch = []
                print(f"  Processadas {processed_count} mensagens...")
            
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            skip_reasons['dados_incompletos'] += 1
            skipped_count += 1
            continue

    # Inserir mensagens restantes
    if mensagens_batch:
        db.bulk_insert_mappings(models.Mensagem, mensagens_batch)
        db.commit()
    
    # Log do resumo
    print(f"\n=== Resumo da importação ===")
    print(f"Mensagens processadas: {processed_count}")
    print(f"Mensagens ignoradas: {skipped_count}")
    if skipped_count > 0:
        print(f"\nMotivos:")
        if skip_reasons['sem_tipo'] > 0:
            print(f"  - Sem tipo: {skip_reasons['sem_tipo']}")
        if skip_reasons['sem_remetente_destinatario'] > 0:
            print(f"  - Sem remetente/destinatário: {skip_reasons['sem_remetente_destinatario']}")
        if skip_reasons['sem_data'] > 0:
            print(f"  - Sem data/hora: {skip_reasons['sem_data']}")
        if skip_reasons['sem_ip'] > 0:
            print(f"  - Sem IP: {skip_reasons['sem_ip']}")
        if skip_reasons['dados_incompletos'] > 0:
            print(f"  - Dados incompletos/erro: {skip_reasons['dados_incompletos']}")
    
    return processed_count

def parse_pdf_and_save(file_content: bytes, operacao_id: int, db: Session):
    pdf_file = BytesIO(file_content)
    reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    # DEBUG: Imprimir início do texto para ver o formato
    print("\n=== INÍCIO DO TEXTO EXTRAÍDO DO PDF ===")
    print(text[:500])
    print("=== FIM DO PREVIEW ===\n")

    data_list = []
    
    # Regex flexível para datas (com ou sem label)
    # Aceita: "Timestamp: ...", "Data: ...", ou apenas a data "09/10/2024 ..."
    date_pattern = re.compile(r'(?:Timestamp|Data|Date|Hora)?[:\s]*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', re.IGNORECASE)
    
    lines = text.split('\n')
    current_msg = {}
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Verificar início de nova mensagem (Data é o principal indicador)
        date_match = date_pattern.search(line)
        if date_match:
            # Se já tem uma mensagem sendo construída e tem campos mínimos, salva
            if current_msg and 'DATA' in current_msg:
                data_list.append(current_msg)
                current_msg = {}
            
            current_msg['DATA'] = date_match.group(1)
            # Continua para processar o resto da linha, caso tenha mais info
        
        if not current_msg: continue
        
        # Extrair outros campos com regex flexível (Inglês e Português)
        
        # IP
        if re.search(r'(Sender Ip|IP|IP Remetente)[:\s]', line, re.IGNORECASE):
            parts = re.split(r'(?:Sender Ip|IP|IP Remetente)[:\s]+', line, flags=re.IGNORECASE)
            if len(parts) > 1: current_msg['IP'] = parts[1].split()[0].strip() # Pega apenas o primeiro token após o label
            
        # Porta
        elif re.search(r'(Sender Port|Porta)[:\s]', line, re.IGNORECASE):
            parts = re.split(r'(?:Sender Port|Porta)[:\s]+', line, flags=re.IGNORECASE)
            if len(parts) > 1: current_msg['PORTA'] = parts[1].strip()

        # Remetente (De/From/Sender) - Cuidado para não confundir com Sender Ip
        elif re.search(r'(Sender|From|De|Remetente)[:\s]', line, re.IGNORECASE) and not re.search(r'(Ip|Port)', line, re.IGNORECASE):
            parts = re.split(r'(?:Sender|From|De|Remetente)[:\s]+', line, flags=re.IGNORECASE)
            if len(parts) > 1: current_msg['REMETENTE'] = parts[1].strip()

        # Destinatário (To/Recipients/Para/Destinatário)
        elif re.search(r'(Recipients|To|Para|Destinat[áa]rio)[:\s]', line, re.IGNORECASE):
            parts = re.split(r'(?:Recipients|To|Para|Destinat[áa]rio)[:\s]+', line, flags=re.IGNORECASE)
            if len(parts) > 1: current_msg['DESTINATÁRIO'] = parts[1].strip()

        # Tipo
        elif re.search(r'(Type|Tipo)[:\s]', line, re.IGNORECASE):
            parts = re.split(r'(?:Type|Tipo)[:\s]+', line, flags=re.IGNORECASE)
            if len(parts) > 1: current_msg['TIPO'] = parts[1].strip()

        # Alvo
        elif re.search(r'(Account Identifier|Alvo|Conta)[:\s]', line, re.IGNORECASE):
            parts = re.split(r'(?:Account Identifier|Alvo|Conta)[:\s]+', line, flags=re.IGNORECASE)
            if len(parts) > 1: current_msg['ALVO'] = parts[1].strip().replace('+', '')

    # Adicionar a última mensagem
    if current_msg and 'DATA' in current_msg:
        data_list.append(current_msg)
        
    if not data_list:
        print("AVISO: Nenhuma mensagem identificada com o padrão de data.")
        # Fallback: Tentar extrair tudo que parece um número de telefone e IP se falhar
        pass

    return _process_data_list(data_list, operacao_id, db)

def parse_html_and_save(file_content: bytes, operacao_id: int, db: Session):
    soup = BeautifulSoup(file_content, 'html.parser')
    
    # Encontrar a tabela principal. 
    # Assumindo que é a primeira tabela ou tem uma classe específica. 
    # Vamos tentar pegar a primeira tabela por enquanto.
    # Tentar encontrar tabela primeiro
    table = soup.find('table')
    
    data_list = []

    if table:
        # Lógica para Tabela (mantida mas simplificada para extrair dados primeiro)
        headers = [th.get_text(strip=True).upper() for th in table.find_all('th')]
        col_map = {
            'ALVO': None, 'REMETENTE': None, 'DESTINATÁRIO': None, 
            'IP': None, 'PORTA': None, 'DATA': None, 'TIPO': None
        }
        
        for i, h in enumerate(headers):
            if 'ALVO' in h: col_map['ALVO'] = i
            elif 'REMETENTE' in h: col_map['REMETENTE'] = i
            elif 'DESTINATÁRIO' in h or 'DESTINATARIO' in h: col_map['DESTINATÁRIO'] = i
            elif 'IP' in h and 'TIPO' not in h: col_map['IP'] = i
            elif 'PORTA' in h: col_map['PORTA'] = i
            elif 'DATA' in h or 'HORA' in h: col_map['DATA'] = i
            elif 'TIPO' in h: col_map['TIPO'] = i

        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if not cols: continue
            row_data = {}
            for key, idx in col_map.items():
                if idx is not None and idx < len(cols):
                    row_data[key] = cols[idx].get_text(strip=True)
            data_list.append(row_data)
            
    else:
        # Lógica para estrutura de DIVs (WhatsApp Record)
        divs = soup.find_all('div', class_='t o')
        for div in divs:
            title_div = div.find('div', class_='t i')
            if title_div:
                # Get direct text only to avoid including children content
                direct_text = ''.join([t for t in title_div.find_all(string=True, recursive=False)]).strip()
                
                if direct_text == 'Message':
                    # Conteúdo está em .m > div
                    content_container = div.find('div', class_='m')
                    if not content_container: continue
                    
                    inner_div = content_container.find('div')
                    if not inner_div: continue
                    
                    # Agora iterar sobre os campos dentro da mensagem
                    fields = inner_div.find_all('div', class_='t o', recursive=False)
                    row_data = {}
                    
                    for field in fields:
                        key_div = field.find('div', class_='t i')
                        val_div = field.find('div', class_='m')
                        
                        if key_div and val_div:
                            # Extract key correctly (direct text only)
                            key = ''.join([t for t in key_div.find_all(string=True, recursive=False)]).strip().replace(':', '')
                            val = val_div.get_text(strip=True)
                            
                            if 'Timestamp' in key: row_data['DATA'] = val
                            elif 'Sender Ip' in key: row_data['IP'] = val
                            elif 'Sender Port' in key: row_data['PORTA'] = val
                            elif 'Sender' == key: row_data['REMETENTE'] = val
                            elif 'Recipients' in key: row_data['DESTINATÁRIO'] = val
                            elif 'Type' in key: row_data['TIPO'] = val
                    
                    if row_data:
                        data_list.append(row_data)

        # Tentar encontrar o ALVO globalmente se não estiver nos dados
        account_id = None
        # Procurar "Account Identifier"
        for div in divs:
            title_div = div.find('div', class_='t i')
            if title_div:
                direct_text = ''.join([t for t in title_div.find_all(string=True, recursive=False)]).strip()
                if 'Account Identifier' in direct_text:
                    val_div = div.find('div', class_='m')
                    if val_div:
                        account_id = val_div.get_text(strip=True).replace('+', '')
                        break
        
        if account_id:
            for d in data_list:
                d['ALVO'] = account_id

    if not data_list:
        raise ValueError("Nenhum dado encontrado (Tabela ou Divs de Mensagem).")

    return _process_data_list(data_list, operacao_id, db)
