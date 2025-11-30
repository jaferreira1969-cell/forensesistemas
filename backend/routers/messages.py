from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
import backend.models as models, schemas
from backend.database import get_db

router = APIRouter(
    prefix="/mensagens",
    tags=["mensagens"],
)

@router.get("/{operacao_id}", response_model=List[schemas.Mensagem])
def read_mensagens(
    operacao_id: int,
    skip: int = 0,
    limit: int = 100,  # Aumentado para 100
    search: Optional[str] = None,
    sort_by: Optional[str] = "data_hora",
    order: Optional[str] = "desc",
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Limitar máximo para 500 para evitar sobrecarregar o Supabase
    limit = min(limit, 500)
    
    # Base query com eager loading otimizado
    query = db.query(models.Mensagem).filter(models.Mensagem.operacao_id == operacao_id)
    
    # Filtro de data
    if data_inicio:
        query = query.filter(models.Mensagem.data_hora >= data_inicio)
    if data_fim:
        # Ajustar data_fim para incluir todo o dia
        if len(data_fim) == 10:  # Formato YYYY-MM-DD
            data_fim_adjusted = data_fim + " 23:59:59"
        else:
            data_fim_adjusted = data_fim
        query = query.filter(models.Mensagem.data_hora <= data_fim_adjusted)
    
    # Só fazer join com IP se realmente precisar (busca por IP)
    needs_ip_join = search and any(c.isdigit() or c == '.' or c == ':' for c in search)
    
    if needs_ip_join:
        # Eager load com join otimizado
        query = query.options(joinedload(models.Mensagem.ip_rel))
        query = query.outerjoin(models.IP)
        search_filter = or_(
            models.Mensagem.alvo.like(f'%{search}%'),
            models.Mensagem.remetente.like(f'%{search}%'),
            models.Mensagem.destinatario.like(f'%{search}%'),
            models.Mensagem.tipo_mensagem.like(f'%{search}%'),
            models.IP.endereco.like(f'%{search}%')
        )
        query = query.filter(search_filter)
    elif search:
        # Busca sem IP (mais rápida)
        query = query.options(joinedload(models.Mensagem.ip_rel))
        search_filter = or_(
            models.Mensagem.alvo.like(f'%{search}%'),
            models.Mensagem.remetente.like(f'%{search}%'),
            models.Mensagem.destinatario.like(f'%{search}%'),
            models.Mensagem.tipo_mensagem.like(f'%{search}%')
        )
        query = query.filter(search_filter)
    else:
        # Sem busca - apenas eager load (mais rápido)
        query = query.options(joinedload(models.Mensagem.ip_rel))
    
    # Sorting logic
    if sort_by:
        sort_column = None
        if sort_by == "ip" and needs_ip_join:
            sort_column = models.IP.endereco
        elif hasattr(models.Mensagem, sort_by):
            sort_column = getattr(models.Mensagem, sort_by)
            
        if sort_column is not None:
            if order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
             # Default sort if invalid column
             query = query.order_by(models.Mensagem.data_hora.desc())
    else:
        query = query.order_by(models.Mensagem.data_hora.desc())
        
    mensagens = query.offset(skip).limit(limit).all()
    return mensagens
