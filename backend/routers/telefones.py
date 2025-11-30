from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import backend.models as models
import schemas
from backend.database import get_db

router = APIRouter(prefix="/telefones", tags=["telefones"])

@router.get("/{operacao_id}", response_model=List[schemas.Telefone])
def get_telefones(operacao_id: int, db: Session = Depends(get_db)):
    """Listar todos os telefones de uma operação"""
    telefones = db.query(models.Telefone).filter(
        models.Telefone.operacao_id == operacao_id
    ).all()
    return telefones

@router.put("/{telefone_id}", response_model=schemas.Telefone)
def update_telefone(
    telefone_id: int,
    data: schemas.TelefoneUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar nome, foto, categoria e/ou observações de um telefone"""
    telefone = db.query(models.Telefone).filter(
        models.Telefone.id == telefone_id
    ).first()
    
    if not telefone:
        raise HTTPException(status_code=404, detail="Telefone não encontrado")
    
    # Atualizar apenas os campos fornecidos
    if data.identificacao is not None:
        telefone.identificacao = data.identificacao
    if data.foto is not None:
        telefone.foto = data.foto
    if data.categoria is not None:
        telefone.categoria = data.categoria
    if data.observacoes is not None:
        telefone.observacoes = data.observacoes
    
    db.commit()
    db.refresh(telefone)
    return telefone

@router.get("/by-numero/{operacao_id}/{numero}", response_model=schemas.Telefone)
def get_telefone_by_numero(operacao_id: int, numero: str, db: Session = Depends(get_db)):
    """Buscar telefone por número em uma operação"""
    telefone = db.query(models.Telefone).filter(
        models.Telefone.operacao_id == operacao_id,
        models.Telefone.numero == numero
    ).first()
    
    if not telefone:
        raise HTTPException(status_code=404, detail="Telefone não encontrado")
    
    return telefone
