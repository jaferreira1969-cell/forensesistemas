from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from collections import Counter, defaultdict
import backend.models as models
from backend.database import get_db
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import cm
from reportlab.lib import colors
import os
import tempfile

router = APIRouter(
    prefix="/intelligence",
    tags=["intelligence"],
)

def analyze_network(db: Session, operacao_id: int):
    """Análise de rede social: hubs, grau de centralidade"""
    # Buscar todas as comunicações
    comms = db.query(
        models.Mensagem.remetente,
        models.Mensagem.destinatario,
        func.count(models.Mensagem.id).label('count')
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.remetente.isnot(None),
        models.Mensagem.destinatario.isnot(None)
    ).group_by(
        models.Mensagem.remetente,
        models.Mensagem.destinatario
    ).all()
    
    # Calcular grau (número de conexões únicas)
    connections = defaultdict(set)
    for rem, dest, count in comms:
        connections[rem].add(dest)
        connections[dest].add(rem)
    
    # Top hubs (telefones com mais conexões)
    hubs = sorted(
        [(tel, len(conns)) for tel, conns in connections.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Buscar informações dos telefones
    hubs_detailed = []
    for telefone, conexoes in hubs:
        tel_obj = db.query(models.Telefone).filter(
            models.Telefone.operacao_id == operacao_id,
            models.Telefone.numero == telefone
        ).first()
        
        hubs_detailed.append({
            "telefone": telefone,
            "identificacao": tel_obj.identificacao if tel_obj else None,
            "categoria": tel_obj.categoria if tel_obj else None,
            "conexoes": conexoes,
            "grau": conexoes / max(len(connections), 1)
        })
    
    return {"hubs": hubs_detailed, "total_nodes": len(connections)}

def analyze_temporal(db: Session, operacao_id: int):
    """Análise de padrões temporais"""
    mensagens = db.query(models.Mensagem).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.data_hora.isnot(None)
    ).all()
    
    if not mensagens:
        return {"error": "Sem mensagens com data/hora"}
    
    # Horários de pico
    hour_counts = Counter([msg.data_hora.hour for msg in mensagens])
    pico_horario = hour_counts.most_common(1)[0] if hour_counts else (0, 0)
    
    # Dias da semana mais ativos
    weekday_counts = Counter([msg.data_hora.strftime('%A') for msg in mensagens])
    dia_mais_ativo = weekday_counts.most_common(1)[0] if weekday_counts else ('', 0)
    
    # Primeiro e último registro
    datas = [msg.data_hora for msg in mensagens]
    periodo = {
        "inicio": min(datas).strftime('%d/%m/%Y %H:%M'),
        "fim": max(datas).strftime('%d/%m/%Y %H:%M')
    }
    
    return {
        "pico_horario": {"hora": pico_horario[0], "mensagens": pico_horario[1]},
        "dia_mais_ativo": {"dia": dia_mais_ativo[0], "mensagens": dia_mais_ativo[1]},
        "periodo": periodo,
        "distribuicao_horaria": dict(hour_counts.most_common(24))
    }

def analyze_geographic(db: Session, operacao_id: int):
    """Inteligência geográfica: IPs, provedores, regiões"""
    ip_usage = db.query(
        models.IP.endereco,
        models.IP.pais,
        models.IP.cidade,
        models.IP.provedor,
        func.count(models.Mensagem.id).label('mensagens')
    ).join(
        models.Mensagem
    ).filter(
        models.Mensagem.operacao_id == operacao_id
    ).group_by(
        models.IP.id
    ).order_by(
        func.count(models.Mensagem.id).desc()
    ).limit(10).all()
    
    # Top provedores
    provedor_counts = defaultdict(int)
    for _, _, _, provedor, count in ip_usage:
        if provedor:
            provedor_counts[provedor] += count
    
    top_provedores = sorted(
        provedor_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return {
        "top_ips": [
            {
                "ip": ip,
                "pais": pais or "Desconhecido",
                "cidade": cidade or "Desconhecido",
                "provedor": provedor or "Desconhecido",
                "mensagens": int(msgs)
            }
            for ip, pais, cidade, provedor, msgs in ip_usage
        ],
        "top_provedores": [
            {"provedor": prov, "mensagens": count}
            for prov, count in top_provedores
        ]
    }

def analyze_top_rankings(db: Session, operacao_id: int):
    """Top rankings: telefones, conexões, tipos"""
    # Top telefones mais ativos
    top_phones = db.query(
        models.Telefone.numero,
        models.Telefone.identificacao,
        models.Telefone.categoria,
        models.Telefone.total_mensagens
    ).filter(
        models.Telefone.operacao_id == operacao_id
    ).order_by(
        models.Telefone.total_mensagens.desc()
    ).limit(10).all()
    
    # Top tipos de mensagem
    tipo_counts = db.query(
        models.Mensagem.tipo_mensagem,
        func.count(models.Mensagem.id)
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.tipo_mensagem.isnot(None)
    ).group_by(
        models.Mensagem.tipo_mensagem
    ).order_by(
        func.count(models.Mensagem.id).desc()
    ).all()
    
    # Top conexões (pares de telefones)
    top_connections = db.query(
        models.Mensagem.remetente,
        models.Mensagem.destinatario,
        func.count(models.Mensagem.id).label('msgs')
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.remetente.isnot(None),
        models.Mensagem.destinatario.isnot(None)
    ).group_by(
        models.Mensagem.remetente,
        models.Mensagem.destinatario
    ).order_by(
        func.count(models.Mensagem.id).desc()
    ).limit(10).all()
    
    return {
        "telefones_ativos": [
            {
                "telefone": num,
                "identificacao": ident or "Não identificado",
                "categoria": cat or "Sem categoria",
                "mensagens": int(total) if total else 0
            }
            for num, ident, cat, total in top_phones
        ],
        "tipos_mensagem": [
            {"tipo": tipo, "quantidade": int(count)}
            for tipo, count in tipo_counts
        ],
        "conexoes_fortes": [
            {
                "origem": rem,
                "destino": dest,
                "mensagens": int(msgs)
            }
            for rem, dest, msgs in top_connections
        ]
    }

def find_unregistered_phones(db: Session, operacao_id: int):
    """Encontrar telefones que aparecem nas mensagens mas não estão cadastrados"""
    # Telefones cadastrados
    registered = {t.numero for t in db.query(models.Telefone).filter(
        models.Telefone.operacao_id == operacao_id
    ).all()}
    
    # Telefones nas mensagens
    in_messages = set()
    msgs = db.query(models.Mensagem).filter(
        models.Mensagem.operacao_id == operacao_id
    ).all()
    
    for msg in msgs:
        if msg.remetente:
            in_messages.add(msg.remetente)
        if msg.destinatario:
            in_messages.add(msg.destinatario)
    
    # Não cadastrados
    unregistered = in_messages - registered
    
    # Contar aparições
    unregistered_counts = Counter()
    for msg in msgs:
        if msg.remetente in unregistered:
            unregistered_counts[msg.remetente] += 1
        if msg.destinatario in unregistered:
            unregistered_counts[msg.destinatario] += 1
    
    return [
        {
            "telefone": tel,
            "aparicoes": count,
            "sugestao": "Adicionar à investigação" if count > 5 else "Contato secundário"
        }
        for tel, count in unregistered_counts.most_common(20)
    ]

def analyze_shared_terminals(db: Session, operacao_id: int):
    """
    Identifica IPs compartilhados entre Alvos e outros telefones.
    Isso indica possível co-localização ou uso do mesmo terminal/wifi.
    """
    # 1. Identificar telefones ALVO
    alvos = db.query(models.Telefone).filter(
        models.Telefone.operacao_id == operacao_id,
        models.Telefone.tipo == 'ALVO'
    ).all()
    
    alvo_numeros = {t.numero for t in alvos}
    
    if not alvo_numeros:
        return []

    # 2. Buscar IPs usados pelos alvos
    ips_alvos = db.query(
        models.Mensagem.ip_id,
        models.Mensagem.remetente
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.remetente.in_(alvo_numeros),
        models.Mensagem.ip_id.isnot(None)
    ).distinct().all()
    
    ip_map = defaultdict(set)
    for ip_id, remetente in ips_alvos:
        ip_map[ip_id].add(remetente)
        
    if not ip_map:
        return []
        
    # 3. Buscar OUTROS telefones que usaram esses mesmos IPs
    shared_usage = db.query(
        models.Mensagem.ip_id,
        models.Mensagem.remetente,
        models.IP.endereco,
        models.IP.provedor
    ).join(
        models.IP
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.ip_id.in_(ip_map.keys()),
        models.Mensagem.remetente.notin_(alvo_numeros), # Excluir o próprio alvo (mas incluir outros alvos se quiser ver cruzamento entre alvos)
        models.Mensagem.remetente.isnot(None)
    ).distinct().all()
    
    # Estruturar resultado
    results = defaultdict(lambda: {"ip": "", "provedor": "", "alvos": set(), "outros": set()})
    
    for ip_id, remetente, endereco, provedor in shared_usage:
        results[ip_id]["ip"] = endereco
        results[ip_id]["provedor"] = provedor or "Desconhecido"
        results[ip_id]["alvos"] = ip_map[ip_id] # Alvos que usaram este IP
        results[ip_id]["outros"].add(remetente)
        
    # Formatar para lista
    final_list = []
    for ip_id, data in results.items():
        if data["outros"]: # Só interessa se tiver compartilhamento
            final_list.append({
                "ip": data["ip"],
                "provedor": data["provedor"],
                "alvos": list(data["alvos"]),
                "outros": list(data["outros"])
            })
            
    return sorted(final_list, key=lambda x: len(x["outros"]), reverse=True)

def analyze_geographic_anomalies(db: Session, operacao_id: int):
    """
    Detecta anomalias geográficas:
    1. IPs em países diferentes da maioria (viagem ou VPN)
    2. Provedores de Hosting/VPS conhecidos
    """
    # 1. Determinar país predominante
    paises = db.query(models.IP.pais, func.count(models.IP.id)).join(models.Mensagem).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.IP.pais.isnot(None)
    ).group_by(models.IP.pais).all()
    
    if not paises:
        return {"anomalies": [], "main_country": "Desconhecido"}
        
    main_country = max(paises, key=lambda x: x[1])[0]
    
    # 2. Buscar IPs fora do país predominante
    foreign_ips = db.query(
        models.IP.endereco,
        models.IP.pais,
        models.IP.cidade,
        models.IP.provedor,
        models.Mensagem.remetente
    ).join(models.Mensagem).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.IP.pais != main_country,
        models.IP.pais.isnot(None)
    ).distinct().all()
    
    anomalies = []
    for ip, pais, cidade, provedor, remetente in foreign_ips:
        anomalies.append({
            "tipo": "Localização Atípica",
            "detalhe": f"IP em {cidade}/{pais} ({main_country} é o padrão)",
            "ip": ip,
            "provedor": provedor,
            "telefone": remetente
        })
        
    # 3. Detectar VPS/Hosting (Lista básica)
    vps_keywords = ['amazon', 'aws', 'google cloud', 'digitalocean', 'microsoft azure', 'oracle', 'hetzner', 'ovh', 'linode']
    
    vps_ips = db.query(
        models.IP.endereco,
        models.IP.provedor,
        models.Mensagem.remetente
    ).join(models.Mensagem).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.IP.provedor.isnot(None)
    ).distinct().all()
    
    for ip, provedor, remetente in vps_ips:
        prov_lower = provedor.lower()
        if any(k in prov_lower for k in vps_keywords):
            anomalies.append({
                "tipo": "Uso de VPS/Datacenter",
                "detalhe": f"Provedor {provedor} geralmente indica VPN ou servidor",
                "ip": ip,
                "provedor": provedor,
                "telefone": remetente
            })
            
    return {"anomalies": anomalies, "main_country": main_country}

def analyze_period_comparison(db: Session, operacao_id: int):
    """
    Compara comportamento entre dois períodos (primeira metade vs segunda metade da investigação).
    Identifica mudanças de padrão que podem indicar eventos significativos.
    """
    # Buscar todas as mensagens com data
    mensagens = db.query(models.Mensagem).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.data_hora.isnot(None)
    ).order_by(models.Mensagem.data_hora).all()
    
    if not mensagens or len(mensagens) < 10:
        return {"error": "Dados insuficientes para comparação"}
    
    # Encontrar ponto médio temporal
    datas = [msg.data_hora for msg in mensagens]
    data_inicio = min(datas)
    data_fim = max(datas)
    
    # Calcular ponto médio
    delta = data_fim - data_inicio
    data_meio = data_inicio + delta / 2
    
    # Dividir mensagens em dois períodos
    periodo1 = [msg for msg in mensagens if msg.data_hora < data_meio]
    periodo2 = [msg for msg in mensagens if msg.data_hora >= data_meio]
    
    if not periodo1 or not periodo2:
        return {"error": "Não foi possível dividir em dois períodos"}
    
    # Função auxiliar para analisar um período
    def analyze_period(msgs):
        # Contatos únicos
        remetentes = {msg.remetente for msg in msgs if msg.remetente}
        destinatarios = {msg.destinatario for msg in msgs if msg.destinatario}
        contatos_unicos = len(remetentes | destinatarios)
        
        # Mensagens por dia (média)
        dias_span = (max(msg.data_hora for msg in msgs) - min(msg.data_hora for msg in msgs)).days + 1
        msgs_por_dia = len(msgs) / max(dias_span, 1)
        
        # Horários mais ativos (distribuição)
        hours = Counter([msg.data_hora.hour for msg in msgs])
        horarios_pico = hours.most_common(3)
        
        # Tipos de mensagem
        tipos = Counter([msg.tipo_mensagem for msg in msgs if msg.tipo_mensagem])
        
        return {
            "total_mensagens": len(msgs),
            "contatos_unicos": contatos_unicos,
            "msgs_por_dia": round(msgs_por_dia, 1),
            "horarios_pico": [{"hora": h, "msgs": c} for h, c in horarios_pico],
            "tipos_mensagem": dict(tipos.most_common(5))
        }
    
    # Analisar ambos os períodos
    analise_p1 = analyze_period(periodo1)
    analise_p2 = analyze_period(periodo2)
    
    # Calcular variações percentuais
    def calc_variacao(val1, val2):
        if val1 == 0:
            return 100 if val2 > 0 else 0
        return round(((val2 - val1) / val1) * 100, 1)
    
    variacoes = {
        "mensagens": calc_variacao(analise_p1["total_mensagens"], analise_p2["total_mensagens"]),
        "contatos": calc_variacao(analise_p1["contatos_unicos"], analise_p2["contatos_unicos"]),
        "intensidade_diaria": calc_variacao(analise_p1["msgs_por_dia"], analise_p2["msgs_por_dia"])
    }
    
    # Detectar mudanças significativas
    alertas = []
    if abs(variacoes["mensagens"]) > 50:
        direcao = "aumento" if variacoes["mensagens"] > 0 else "redução"
        alertas.append(f"⚠️ {direcao.capitalize()} de {abs(variacoes['mensagens'])}% no volume de mensagens")
    
    if abs(variacoes["contatos"]) > 50:
        direcao = "expansão" if variacoes["contatos"] > 0 else "contração"
        alertas.append(f"⚠️ {direcao.capitalize()} de {abs(variacoes['contatos'])}% na rede de contatos")
    
    if abs(variacoes["intensidade_diaria"]) > 100:
        alertas.append(f"⚠️ Mudança drástica na intensidade diária de comunicação")
    
    return {
        "periodo1": {
            "datas": f"{periodo1[0].data_hora.strftime('%d/%m/%Y')} a {periodo1[-1].data_hora.strftime('%d/%m/%Y')}",
            "analise": analise_p1
        },
        "periodo2": {
            "datas": f"{periodo2[0].data_hora.strftime('%d/%m/%Y')} a {periodo2[-1].data_hora.strftime('%d/%m/%Y')}",
            "analise": analise_p2
        },
        "variacoes": variacoes,
        "alertas": alertas,
        "data_divisao": data_meio.strftime('%d/%m/%Y')
    }

@router.get("/{operacao_id}/report")
def generate_intelligence_report(operacao_id: int, db: Session = Depends(get_db)):
    """Gera relatório de inteligência completo em PDF"""
    # Buscar operação
    operacao = db.query(models.Operacao).filter(models.Operacao.id == operacao_id).first()
    if not operacao:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    
    # Estatísticas gerais
    stats = {
        "total_telefones": db.query(models.Telefone).filter(models.Telefone.operacao_id == operacao_id).count(),
        "total_mensagens": db.query(models.Mensagem).filter(models.Mensagem.operacao_id == operacao_id).count(),
        "total_ips": db.query(models.IP).join(models.Mensagem).filter(models.Mensagem.operacao_id == operacao_id).distinct().count()
    }
    
    # Executar análises
    network_analysis = analyze_network(db, operacao_id)
    temporal_analysis = analyze_temporal(db, operacao_id)
    geographic_analysis = analyze_geographic(db, operacao_id)
    rankings = analyze_top_rankings(db, operacao_id)
    unregistered = find_unregistered_phones(db, operacao_id)
    shared_terminals = analyze_shared_terminals(db, operacao_id)
    geo_anomalies = analyze_geographic_anomalies(db, operacao_id)
    period_comparison = analyze_period_comparison(db, operacao_id)
    
    # Gerar PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos Customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Título
    story.append(Paragraph(f"RELATÓRIO DE INTELIGÊNCIA", title_style))
    story.append(Paragraph(f"Operação: {operacao.nome}", styles['Heading2']))
    story.append(Paragraph(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 1*cm))
    
    # Sumário Executivo
    story.append(Paragraph("SUMÁRIO EXECUTIVO", styles['Heading2']))
    summary_data = [
        ["Métrica", "Valor"],
        ["Total de Telefones", str(stats['total_telefones'])],
        ["Total de Mensagens", str(stats['total_mensagens'])],
        ["Total de IPs Únicos", str(stats['total_ips'])],
        ["Período Analisado", f"{temporal_analysis.get('periodo', {}).get('inicio', 'N/A')} a {temporal_analysis.get('periodo', {}).get('fim', 'N/A')}"]
    ]
    t = Table(summary_data, colWidths=[10*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # Análise de Rede Social
    story.append(Paragraph("ANÁLISE DE REDE SOCIAL", styles['Heading2']))
    story.append(Paragraph(f"Total de Nós na Rede: {network_analysis['total_nodes']}", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Top 10 Hubs (Telefones Mais Conectados):", styles['Heading3']))
    
    hub_data = [["#", "Telefone", "Identificação", "Categoria", "Conexões"]]
    for i, hub in enumerate(network_analysis['hubs'][:10], 1):
        hub_data.append([
            str(i),
            hub['telefone'],
            Paragraph(hub['identificacao'] or 'N/A', styles['Normal']), # Wrap text
            hub['categoria'] or 'N/A',
            str(hub['conexoes'])
        ])
    
    t = Table(hub_data, colWidths=[1*cm, 3.5*cm, 5*cm, 3*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # Terminais Compartilhados (NOVO)
    if shared_terminals:
        story.append(Paragraph("ANÁLISE DE TERMINAIS COMPARTILHADOS", styles['Heading2']))
        story.append(Paragraph("IPs utilizados por ALVOS que também foram usados por outros telefones. Isso indica forte vínculo, co-localização ou uso do mesmo wifi.", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        shared_data = [["IP / Provedor", "Alvos", "Outros Telefones"]]
        for item in shared_terminals[:10]: # Top 10
            # Formatar listas para caber na célula
            alvos_str = ", ".join(item['alvos'])
            outros_str = ", ".join(item['outros'])
            
            shared_data.append([
                Paragraph(f"{item['ip']}<br/>{item['provedor']}", styles['Normal']),
                Paragraph(alvos_str, styles['Normal']),
                Paragraph(outros_str, styles['Normal'])
            ])
            
        t = Table(shared_data, colWidths=[5*cm, 5*cm, 8*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#b91c1c')), # Red header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(PageBreak())

    # Anomalias Geográficas (NOVO)
    if geo_anomalies['anomalies']:
        story.append(Paragraph("ANOMALIAS GEOGRÁFICAS E DE REDE", styles['Heading2']))
        story.append(Paragraph(f"País predominante na operação: {geo_anomalies['main_country']}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        anom_data = [["Tipo", "Telefone", "Detalhe (IP/Provedor)"]]
        for item in geo_anomalies['anomalies'][:15]:
            anom_data.append([
                item['tipo'],
                item['telefone'],
                Paragraph(f"{item['detalhe']}<br/>IP: {item['ip']}<br/>Prov: {item['provedor']}", styles['Normal'])
            ])
            
        t = Table(anom_data, colWidths=[4*cm, 4*cm, 10*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d97706')), # Amber header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(PageBreak())
    
    # Padrões Temporais
    story.append(Paragraph("PADRÕES TEMPORAIS", styles['Heading2']))
    story.append(Paragraph(f"Horário de Pico: {temporal_analysis['pico_horario']['hora']}:00h ({temporal_analysis['pico_horario']['mensagens']} mensagens)", styles['Normal']))
    story.append(Paragraph(f"Dia Mais Ativo: {temporal_analysis['dia_mais_ativo']['dia']} ({temporal_analysis['dia_mais_ativo']['mensagens']} mensagens)", styles['Normal']))
    story.append(Spacer(1, 1*cm))

    # Comparação de Períodos (NOVO)
    if period_comparison and "error" not in period_comparison:
        story.append(Paragraph("COMPARAÇÃO DE PERÍODOS", styles['Heading2']))
        story.append(Paragraph(f"Análise comparativa dividida em: {period_comparison['data_divisao']}", styles['Normal']))
        story.append(Spacer(1, 0.2*cm))
        
        # Tabela de Comparação
        p1 = period_comparison['periodo1']
        p2 = period_comparison['periodo2']
        vars = period_comparison['variacoes']
        
        comp_data = [
            ["Métrica", "1ª Metade", "2ª Metade", "Variação"],
            ["Período", Paragraph(p1['datas'], styles['Normal']), Paragraph(p2['datas'], styles['Normal']), "-"],
            ["Total Mensagens", str(p1['analise']['total_mensagens']), str(p2['analise']['total_mensagens']), f"{vars['mensagens']}%"],
            ["Contatos Únicos", str(p1['analise']['contatos_unicos']), str(p2['analise']['contatos_unicos']), f"{vars['contatos']}%"],
            ["Msgs/Dia", str(p1['analise']['msgs_por_dia']), str(p2['analise']['msgs_por_dia']), f"{vars['intensidade_diaria']}%"]
        ]
        
        t = Table(comp_data, colWidths=[3.5*cm, 5*cm, 5*cm, 2.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4b5563')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))
        
        # Alertas de Mudança
        if period_comparison['alertas']:
            story.append(Paragraph("⚠️ Mudanças Significativas Detectadas:", styles['Heading3']))
            for alerta in period_comparison['alertas']:
                story.append(Paragraph(alerta, styles['Normal']))
        
        story.append(PageBreak())
    
    # Inteligência Geográfica
    story.append(Paragraph("INTELIGÊNCIA GEOGRÁFICA", styles['Heading2']))
    story.append(Paragraph("Top 5 IPs Mais Usados:", styles['Heading3']))
    
    ip_data = [["#", "IP", "País", "Cidade", "Provedor", "Msgs"]]
    for i, ip in enumerate(geographic_analysis['top_ips'][:5], 1):
        # Usar Paragraph para quebrar linha em IPs longos (IPv6)
        ip_data.append([
            str(i),
            Paragraph(ip['ip'], styles['Normal']), 
            ip['pais'],
            ip['cidade'],
            Paragraph(ip['provedor'], styles['Normal']),
            str(ip['mensagens'])
        ])
    
    t = Table(ip_data, colWidths=[1*cm, 5*cm, 2.5*cm, 2.5*cm, 4*cm, 1.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Top 5 Provedores:", styles['Heading3']))
    prov_data = [["#", "Provedor", "Mensagens"]]
    for i, prov in enumerate(geographic_analysis['top_provedores'], 1):
        prov_data.append([str(i), prov['provedor'], str(prov['mensagens'])])
    
    t = Table(prov_data, colWidths=[2*cm, 10*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # Rankings
    story.append(Paragraph("TOP RANKINGS", styles['Heading2']))
    story.append(Paragraph("Top 10 Telefones Mais Ativos:", styles['Heading3']))
    
    phone_data = [["#", "Telefone", "Identificação", "Categoria", "Mensagens"]]
    for i, phone in enumerate(rankings['telefones_ativos'], 1):
        phone_data.append([
            str(i),
            phone['telefone'],
            Paragraph(phone['identificacao'], styles['Normal']),
            phone['categoria'],
            str(phone['mensagens'])
        ])
    
    t = Table(phone_data, colWidths=[1*cm, 4*cm, 4*cm, 3.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    
    # Entidades Não Cadastradas
    if unregistered:
        story.append(Paragraph("TELEFONES NÃO CADASTRADOS", styles['Heading2']))
        story.append(Paragraph(f"Foram detectados {len(unregistered)} telefones que aparecem nas mensagens mas não estão oficialmente cadastrados na operação.", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        unreg_data = [["Telefone", "Aparições", "Sugestão"]]
        for phone in unregistered[:15]:
            unreg_data.append([
                phone['telefone'],
                str(phone['aparicoes']),
                phone['sugestao']
            ])
        
        t = Table(unreg_data, colWidths=[5*cm, 3*cm, 8*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
    
    # Construir PDF
    doc.build(story)
    
    # Retornar arquivo
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"Relatorio_Inteligencia_{operacao.nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
