from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, String
from typing import List
import backend.models as models
from backend.database import get_db
from services import geolocation

router = APIRouter(
    prefix="/geolocation",
    tags=["geolocation"],
)

@router.post("/{operacao_id}/sync")
def sync_geolocation(operacao_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Iniciar processo em background para não travar a UI
    background_tasks.add_task(geolocation.geolocate_ips, operacao_id, db)
    return {"message": "Sincronização de geolocalização iniciada"}

@router.get("/{operacao_id}")
def get_map_data(
    operacao_id: int, 
    data_inicio: str = None, 
    data_fim: str = None,
    db: Session = Depends(get_db)
):
    """Retornar IPs com coordenadas para plotar no mapa - OTIMIZADO"""
    # Query otimizada que agrega tudo de uma vez
    from sqlalchemy import and_
    from datetime import datetime, timedelta
    
    # Construir filtros
    filters = [
        models.Mensagem.operacao_id == operacao_id,
        models.IP.latitude.isnot(None),
        models.IP.longitude.isnot(None)
    ]
    
    if data_inicio:
        filters.append(models.Mensagem.data_hora >= data_inicio)
    if data_fim:
        # Ajustar data_fim para incluir todo o dia
        # Se a data não tem hora (formato YYYY-MM-DD apenas), adicionar hora de fim do dia
        if len(data_fim) == 10:  # Formato YYYY-MM-DD
            data_fim_adjusted = data_fim + " 23:59:59"
        else:
            data_fim_adjusted = data_fim
        filters.append(models.Mensagem.data_hora <= data_fim_adjusted)
    
    # Query otimizada com string_agg (PostgreSQL)
    from sqlalchemy import text
    
    results = db.query(
        models.IP.id,
        models.IP.endereco,
        models.IP.latitude,
        models.IP.longitude,
        models.IP.cidade,
        models.IP.pais,
        models.IP.provedor,
        func.count(models.Mensagem.id).label('total_mensagens'),
        func.string_agg(func.distinct(models.Mensagem.remetente), text("','")).label('telefones')
    ).join(
        models.Mensagem, models.Mensagem.ip_id == models.IP.id
    ).filter(
        and_(*filters)
    ).group_by(models.IP.id).all()

    # Formatar resultado
    return [
        {
            "id": r.id,
            "endereco": r.endereco,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "cidade": r.cidade,
            "pais": r.pais,
            "provedor": r.provedor,
            "telefones": sorted(r.telefones.split(',')) if r.telefones else [],
            "total_mensagens": r.total_mensagens
        }
        for r in results
    ]



