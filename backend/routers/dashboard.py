from functools import lru_cache
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import Dict, Any, List
import models
from database import get_db
import time

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

# Cache para 2 minutos (TTL)
CACHE_TTL = 120

@router.get("/{operacao_id}/stats")
def get_stats(operacao_id: int, db: Session = Depends(get_db)):
    """Estatísticas básicas - Otimizado com uma única query"""
    # Uma única query com subqueries para contar tudo de uma vez
    result = db.execute(text("""
        SELECT 
            (SELECT COUNT(*) FROM telefones WHERE operacao_id = :op_id) as total_telefones,
            (SELECT COUNT(*) FROM mensagens WHERE operacao_id = :op_id) as total_mensagens,
            (SELECT COUNT(DISTINCT ip_id) FROM mensagens WHERE operacao_id = :op_id AND ip_id IS NOT NULL) as total_ips
    """), {"op_id": operacao_id}).first()
    
    return {
        "total_telefones": result[0],
        "total_mensagens": result[1],
        "total_ips": result[2]
    }

@router.get("/{operacao_id}/evolution")
def get_evolution(operacao_id: int, db: Session = Depends(get_db)):
    """Evolução temporal - PostgreSQL date_trunc"""
    results = db.query(
        func.date_trunc('day', models.Mensagem.data_hora).label('data'),
        func.count(models.Mensagem.id)
    ).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.Mensagem.data_hora.isnot(None)
    ).group_by('data').order_by('data').all()
    
    return [{"data": str(r[0].date()), "total": r[1]} for r in results]


