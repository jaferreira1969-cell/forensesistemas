from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from typing import Dict, Any, List
import backend.models as models
from backend.database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/message-types/{operacao_id}")
def get_message_types(operacao_id: int, db: Session = Depends(get_db)):
    """Get distribution of message types"""
    results = (
        db.query(
            models.Mensagem.tipo_mensagem,
            func.count(models.Mensagem.id).label('count')
        )
        .filter(models.Mensagem.operacao_id == operacao_id)
        .group_by(models.Mensagem.tipo_mensagem)
        .all()
    )
    
    return [
        {"tipo": r.tipo_mensagem or "unknown", "count": r.count}
        for r in results
    ]

@router.get("/activity-heatmap/{operacao_id}")
def get_activity_heatmap(operacao_id: int, db: Session = Depends(get_db)):
    """Get hourly activity heatmap - Otimizado"""
    # Usando LIMIT para evitar processar milhares de registros
    results = (
        db.query(
            extract('hour', models.Mensagem.data_hora).label('hour'),
            extract('dow', models.Mensagem.data_hora).label('day'),
            func.count(models.Mensagem.id).label('count')
        )
        .filter(
            models.Mensagem.operacao_id == operacao_id,
            models.Mensagem.data_hora.isnot(None)
        )
        .group_by('hour', 'day')
        .all()
    )
    
    return [
        {"hour": int(r.hour) if r.hour is not None else 0, "day": int(r.day) if r.day is not None else 0, "count": r.count}
        for r in results
    ]

@router.get("/top-interlocutors/{operacao_id}")
def get_top_interlocutors(operacao_id: int, limit: int = 5, db: Session = Depends(get_db)):
    """Get top 5 interlocutors (most active numbers)"""
    # Contar mensagens onde o número é remetente
    sent = db.query(
        models.Mensagem.remetente.label('numero'),
        func.count(models.Mensagem.id).label('count')
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.remetente.isnot(None),
        models.Mensagem.remetente != ''
    ).group_by(models.Mensagem.remetente).subquery()

    # Contar mensagens onde o número é destinatário
    received = db.query(
        models.Mensagem.destinatario.label('numero'),
        func.count(models.Mensagem.id).label('count')
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.destinatario.isnot(None),
        models.Mensagem.destinatario != ''
    ).group_by(models.Mensagem.destinatario).subquery()

    # Unir e somar (simplificado: vamos pegar os top remetentes por enquanto para performance, 
    # ou fazer uma união em memória se o volume for baixo. 
    # Melhor abordagem SQL: Union All e depois Group By)
    
    # Abordagem Union All para pegar todos os envolvidos
    all_interactions = db.query(
        models.Mensagem.remetente.label('numero')
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.remetente.isnot(None),
        models.Mensagem.remetente != ''
    ).union_all(
        db.query(
            models.Mensagem.destinatario.label('numero')
        ).filter(
            models.Mensagem.operacao_id == operacao_id,
            models.Mensagem.destinatario.isnot(None),
            models.Mensagem.destinatario != ''
        )
    ).subquery()

    results = db.query(
        all_interactions.c.numero,
        func.count().label('total')
    ).group_by(all_interactions.c.numero).order_by(desc('total')).limit(limit).all()

    return [
        {"numero": r.numero, "total": r.total}
        for r in results
    ]

@router.get("/peak-hours/{operacao_id}")
def get_peak_hours(operacao_id: int, db: Session = Depends(get_db)):
    """Get message volume by hour of day"""
    results = (
        db.query(
            extract('hour', models.Mensagem.data_hora).label('hour'),
            func.count(models.Mensagem.id).label('count')
        )
        .filter(
            models.Mensagem.operacao_id == operacao_id,
            models.Mensagem.data_hora.isnot(None)
        )
        .group_by('hour')
        .order_by('hour')
        .all()
    )
    
    # Preencher horas vazias
    hours_data = {int(r.hour): r.count for r in results}
    final_data = [{"hour": h, "count": hours_data.get(h, 0)} for h in range(24)]
    
    return final_data
