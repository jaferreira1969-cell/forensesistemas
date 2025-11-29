from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import models
from database import get_db

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
)

@router.get("/{operacao_id}/general")
def get_general_graph(operacao_id: int, db: Session = Depends(get_db)):
    # Construir grafo de comunicações entre telefones
    # Nós: Telefones
    # Arestas: Mensagens trocadas
    
    # Buscar todos os telefones da operação
    telefones = db.query(models.Telefone).filter(models.Telefone.operacao_id == operacao_id).all()
    telefones_dict = {t.numero: t for t in telefones}
    
    # Identificar alvos (SUSPEITO ou tipo ALVO)
    alvos_set = set()
    for t in telefones:
        if t.categoria == 'SUSPEITO' or t.tipo == 'ALVO':
            alvos_set.add(t.numero)
    
    # Calcular total de mensagens por telefone
    mensagens_por_tel = {}
    mensagens_count = db.query(
        models.Mensagem.remetente,
        func.count(models.Mensagem.id)
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.remetente.isnot(None)
    ).group_by(models.Mensagem.remetente).all()
    
    for tel, count in mensagens_count:
        mensagens_por_tel[tel] = mensagens_por_tel.get(tel, 0) + count
    
    mensagens_recebidas = db.query(
        models.Mensagem.destinatario,
        func.count(models.Mensagem.id)
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.destinatario.isnot(None)
    ).group_by(models.Mensagem.destinatario).all()
    
    for tel, count in mensagens_recebidas:
        mensagens_por_tel[tel] = mensagens_por_tel.get(tel, 0) + count
    
    # Buscar comunicações para identificar conexões com alvos
    comms = db.query(
        models.Mensagem.remetente,
        models.Mensagem.destinatario,
        func.count(models.Mensagem.id)
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.remetente.isnot(None),
        models.Mensagem.destinatario.isnot(None)
    ).group_by(
        models.Mensagem.remetente,
        models.Mensagem.destinatario
    ).all()
    
    # Identificar quem está conectado a alvos
    conectados_a_alvos = set()
    for c in comms:
        if c.remetente in alvos_set:
            conectados_a_alvos.add(c.destinatario)
        if c.destinatario in alvos_set:
            conectados_a_alvos.add(c.remetente)
    
    nodes = []
    for t in telefones:
        # Definir cor baseada na categoria de investigação (Paleta Harmoniosa)
        color = "#64748B"  # Slate-500 (Padrão/Sem Categoria) - Neutro
        if t.categoria == 'SUSPEITO':
            color = "#E11D48"  # Rose-600 (Suspeito) - Alerta mas elegante
        elif t.categoria == 'TESTEMUNHA':
            color = "#059669"  # Emerald-600 (Testemunha) - Calmo
        elif t.categoria == 'VITIMA':
            color = "#7C3AED"  # Violet-600 (Vítima) - Distinto
        elif t.categoria == 'OUTRO':
            color = "#D97706"  # Amber-600 (Outro) - Atenção moderada
        elif t.tipo == 'ALVO':
            color = "#E11D48"  # Rose-600 (Alvo legado) - Mesmo que suspeito
        
        total_msgs = mensagens_por_tel.get(t.numero, 0)
        is_target = t.numero in alvos_set
        connected_to_target = t.numero in conectados_a_alvos and not is_target
        
        nodes.append({
            "data": {
                "id": t.numero,
                "label": t.identificacao or t.numero,
                "identificacao": t.identificacao,
                "foto": t.foto,
                "telefone_id": t.id,
                "type": t.tipo,
                "categoria": t.categoria,
                "observacoes": t.observacoes,
                "total_mensagens": total_msgs,
                "is_target": is_target,
                "connected_to_target": connected_to_target,
                "color": color
            }
        })
        
    edges = []
    for c in comms:
        if c.remetente and c.destinatario:
            edges.append({
                "data": {
                    "source": c.remetente,
                    "target": c.destinatario,
                    "weight": c[2]
                }
            })
            
    return {"elements": {"nodes": nodes, "edges": edges}}

@router.get("/{operacao_id}/common-ips")
def get_common_ips_graph(operacao_id: int, db: Session = Depends(get_db)):
    # Grafo de Telefones conectados a IPs
    # Nós: Telefones (coloridos por categoria) e IPs (Vermelho)
    # Arestas: Telefone usou IP
    
    # 1. Buscar IPs usados na operação
    ips_usados = db.query(models.IP).join(models.Mensagem).filter(models.Mensagem.operacao_id == operacao_id).distinct().all()
    
    nodes = []
    ip_ids = set()
    
    for ip in ips_usados:
        nodes.append({
            "data": {
                "id": f"ip_{ip.id}",
                "label": ip.endereco,
                "type": "IP",
                "ip_id": ip.id,
                "endereco": ip.endereco,
                "provedor": ip.provedor,
                "pais": ip.pais,
                "cidade": ip.cidade,
                "latitude": ip.latitude,
                "longitude": ip.longitude,
                "color": "#F43F5E"  # Rose-500 (IP)
            }
        })
        ip_ids.add(ip.id)
        
    # 2. Buscar telefones que usaram esses IPs
    conexoes = db.query(
        models.Mensagem.remetente,
        models.Mensagem.ip_id,
        func.count(models.Mensagem.id)
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.ip_id.isnot(None),
        models.Mensagem.remetente.isnot(None)
    ).group_by(
        models.Mensagem.remetente,
        models.Mensagem.ip_id
    ).all()
    
    telefones_nodes = set()
    edges = []
    
    for conn in conexoes:
        tel = conn[0]
        ip_id = conn[1]
        count = conn[2]
        
        if tel not in telefones_nodes:
            # Buscar dados do telefone
            telefone_obj = db.query(models.Telefone).filter(
                models.Telefone.operacao_id == operacao_id,
                models.Telefone.numero == tel
            ).first()
            
            if telefone_obj:
                # Cor baseada na categoria (Paleta Harmoniosa)
                color = "#64748B"  # Slate-500
                if telefone_obj.categoria == 'SUSPEITO':
                    color = "#E11D48"  # Rose-600
                elif telefone_obj.categoria == 'TESTEMUNHA':
                    color = "#059669"  # Emerald-600
                elif telefone_obj.categoria == 'VITIMA':
                    color = "#7C3AED"  # Violet-600
                elif telefone_obj.categoria == 'OUTRO':
                    color = "#D97706"  # Amber-600
                elif telefone_obj.tipo == 'ALVO':
                    color = "#E11D48"  # Rose-600
                
                nodes.append({
                    "data": {
                        "id": tel,
                        "label": telefone_obj.identificacao or tel,
                        "identificacao": telefone_obj.identificacao,
                        "foto": telefone_obj.foto,
                        "telefone_id": telefone_obj.id,
                        "categoria": telefone_obj.categoria,
                        "observacoes": telefone_obj.observacoes,
                        "type": "TELEFONE",
                        "color": color
                    }
                })
            else:
                nodes.append({
                    "data": {
                        "id": tel,
                        "label": tel,
                        "type": "TELEFONE",
                        "color": "#64748B" # Slate-500
                    }
                })
            telefones_nodes.add(tel)
            
        edges.append({
            "data": {
                "source": tel,
                "target": f"ip_{ip_id}",
                "weight": count
            }
        })
        
    return {"elements": {"nodes": nodes, "edges": edges}}

@router.get("/{operacao_id}/shared-ips")
def get_shared_ips_graph(operacao_id: int, db: Session = Depends(get_db)):
    # Grafo de IPs Compartilhados (usados por 2+ telefones)
    # Útil para identificar infraestrutura compartilhada ou padrões suspeitos
    
    # 1. Buscar IPs com contagem de telefones únicos
    ip_phone_counts = db.query(
        models.Mensagem.ip_id,
        func.count(func.distinct(models.Mensagem.remetente)).label('phone_count')
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.ip_id.isnot(None),
        models.Mensagem.remetente.isnot(None)
    ).group_by(
        models.Mensagem.ip_id
    ).having(
        func.count(func.distinct(models.Mensagem.remetente)) > 1  # Mais de 1 telefone
    ).all()
    
    shared_ip_ids = {ip_id for ip_id, _ in ip_phone_counts}
    
    if not shared_ip_ids:
        return {"elements": {"nodes": [], "edges": []}}
    
    # 2. Buscar detalhes dos IPs compartilhados
    ips_compartilhados = db.query(models.IP).filter(models.IP.id.in_(shared_ip_ids)).all()
    
    nodes = []
    for ip in ips_compartilhados:
        # Calcular o número de telefones conectados a este IP
        phone_count = next((count for ip_id, count in ip_phone_counts if ip_id == ip.id), 0)
        
        nodes.append({
            "data": {
                "id": f"ip_{ip.id}",
                "label": ip.endereco,
                "type": "IP",
                "ip_id": ip.id,
                "endereco": ip.endereco,
                "provedor": ip.provedor,
                "pais": ip.pais,
                "cidade": ip.cidade,
                "latitude": ip.latitude,
                "longitude": ip.longitude,
                "phone_count": phone_count,  # Número de telefones conectados
                "color": "#F43F5E"  # Rose-500 (IP)
            }
        })
    
    # 3. Buscar telefones conectados aos IPs compartilhados
    conexoes = db.query(
        models.Mensagem.remetente,
        models.Mensagem.ip_id,
        func.count(models.Mensagem.id)
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.ip_id.in_(shared_ip_ids),
        models.Mensagem.remetente.isnot(None)
    ).group_by(
        models.Mensagem.remetente,
        models.Mensagem.ip_id
    ).all()
    
    telefones_nodes = set()
    edges = []
    
    for conn in conexoes:
        tel = conn[0]
        ip_id = conn[1]
        count = conn[2]
        
        if tel not in telefones_nodes:
            # Buscar dados do telefone
            telefone_obj = db.query(models.Telefone).filter(
                models.Telefone.operacao_id == operacao_id,
                models.Telefone.numero == tel
            ).first()
            
            if telefone_obj:
                # Cor baseada na categoria
                color = "#64748B"  # Slate-500
                if telefone_obj.categoria == 'SUSPEITO':
                    color = "#E11D48"  # Rose-600
                elif telefone_obj.categoria == 'TESTEMUNHA':
                    color = "#059669"  # Emerald-600
                elif telefone_obj.categoria == 'VITIMA':
                    color = "#7C3AED"  # Violet-600
                elif telefone_obj.categoria == 'OUTRO':
                    color = "#D97706"  # Amber-600
                elif telefone_obj.tipo == 'ALVO':
                    color = "#E11D48"  # Rose-600
                
                nodes.append({
                    "data": {
                        "id": tel,
                        "label": telefone_obj.identificacao or tel,
                        "identificacao": telefone_obj.identificacao,
                        "foto": telefone_obj.foto,
                        "telefone_id": telefone_obj.id,
                        "categoria": telefone_obj.categoria,
                        "observacoes": telefone_obj.observacoes,
                        "type": "TELEFONE",
                        "color": color
                    }
                })
            else:
                nodes.append({
                    "data": {
                        "id": tel,
                        "label": tel,
                        "type": "TELEFONE",
                        "color": "#64748B"
                    }
                })
            telefones_nodes.add(tel)
            
        edges.append({
            "data": {
                "source": tel,
                "target": f"ip_{ip_id}",
                "weight": count
            }
        })
        
    return {"elements": {"nodes": nodes, "edges": edges}}
