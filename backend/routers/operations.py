from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import backend.models as models, schemas
from backend.database import get_db

router = APIRouter(
    prefix="/operacoes",
    tags=["operacoes"],
)

@router.post("/", response_model=schemas.Operacao)
def create_operacao(operacao: schemas.OperacaoCreate, db: Session = Depends(get_db)):
    # Verificar duplicidade
    existing = db.query(models.Operacao).filter(models.Operacao.nome == operacao.nome).first()
    if existing:
        raise HTTPException(status_code=400, detail="Já existe uma operação com este nome")

    db_operacao = models.Operacao(nome=operacao.nome, descricao=operacao.descricao)
    db.add(db_operacao)
    db.commit()
    db.refresh(db_operacao)
    return db_operacao

@router.get("/", response_model=List[schemas.Operacao])
def read_operacoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    operacoes = db.query(models.Operacao).offset(skip).limit(limit).all()
    return operacoes

@router.get("/{operacao_id}", response_model=schemas.Operacao)
def read_operacao(operacao_id: int, db: Session = Depends(get_db)):
    operacao = db.query(models.Operacao).filter(models.Operacao.id == operacao_id).first()
    if operacao is None:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    return operacao

@router.delete("/{operacao_id}")
def delete_operacao(operacao_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import text
    
    operacao = db.query(models.Operacao).filter(models.Operacao.id == operacao_id).first()
    if operacao is None:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    
    try:
        # 1. Deletar mensagens em lotes de 1000 para evitar timeout
        while True:
            # Deleta 1000 mensagens desta operação
            result = db.execute(text(f"DELETE FROM mensagens WHERE operacao_id = {operacao_id} AND id IN (SELECT id FROM mensagens WHERE operacao_id = {operacao_id} LIMIT 1000)"))
            db.commit()
            if result.rowcount == 0:
                break
        
        # 2. Deletar outros dados relacionados
        db.execute(text(f"DELETE FROM comunicacoes WHERE operacao_id = {operacao_id}"))
        db.execute(text(f"DELETE FROM arquivos WHERE operacao_id = {operacao_id}"))
        db.execute(text(f"DELETE FROM telefones WHERE operacao_id = {operacao_id}"))
        db.commit()
        
        # 3. Deletar a operação
        db.delete(operacao)
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao deletar operação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar dados: {str(e)}")
        
    return {"ok": True}

@router.put("/{operacao_id}", response_model=schemas.Operacao)
def update_operacao(operacao_id: int, data: schemas.OperacaoCreate, db: Session = Depends(get_db)):
    operacao = db.query(models.Operacao).filter(models.Operacao.id == operacao_id).first()
    if operacao is None:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    
    # Verificar se o novo nome já existe (se for diferente do atual)
    if data.nome != operacao.nome:
        existing = db.query(models.Operacao).filter(models.Operacao.nome == data.nome).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe uma operação com este nome")
    
    operacao.nome = data.nome
    if data.descricao is not None:
        operacao.descricao = data.descricao
    
    db.commit()
    db.refresh(operacao)
    return operacao
