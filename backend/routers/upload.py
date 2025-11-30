from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import backend.models as models, backend.schemas as schemas
from backend.database import get_db
from services import parser, geolocation

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)

@router.post("/", status_code=201)
async def upload_files(
    operacao_id: int = Form(...),
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    # Verificar se operação existe
    operacao = db.query(models.Operacao).filter(models.Operacao.id == operacao_id).first()
    if not operacao:
        raise HTTPException(status_code=404, detail="Operação não encontrada")

    import hashlib

    total_processed = 0
    skipped_files = []
    
    for file in files:
        is_html = file.filename.lower().endswith(('.html', '.htm'))
        is_pdf = file.filename.lower().endswith('.pdf')
        
        if not is_html and not is_pdf:
            continue # Pular arquivos não suportados
            
        content = await file.read()
        
        # Calcular hash MD5
        file_hash = hashlib.md5(content).hexdigest()
        
        # Verificar duplicidade
        existing_file = db.query(models.Arquivo).filter(
            models.Arquivo.operacao_id == operacao_id,
            models.Arquivo.hash_md5 == file_hash
        ).first()
        
        if existing_file:
            # Arquivo já foi importado anteriormente, pular
            skipped_files.append(file.filename)
            continue
            
        try:
            # Extrair metadados do cabeçalho do arquivo
            print(f"\n🔍 Iniciando extração de metadados do arquivo: {file.filename}")
            metadata = parser.extract_file_metadata(content, is_pdf)
            print(f"📋 Metadados extraídos: {metadata}")
            
            # Salvar registro do arquivo COM metadados
            novo_arquivo = models.Arquivo(
                operacao_id=operacao_id,
                nome=file.filename,
                hash_md5=file_hash,
                alvo_numero=metadata['alvo_numero'],
                periodo_inicio=metadata['periodo_inicio'],
                periodo_fim=metadata['periodo_fim']
            )
            db.add(novo_arquivo)
            
            if is_pdf:
                count = parser.parse_pdf_and_save(content, operacao_id, db)
            else:
                count = parser.parse_html_and_save(content, operacao_id, db)
                
            total_processed += count
            db.commit() # Commit a cada arquivo processado com sucesso
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo {file.filename}: {str(e)}")
    
    # Iniciar geolocalização automática em background
    if background_tasks and total_processed > 0:
        background_tasks.add_task(geolocation.geolocate_ips, operacao_id, db)
            
    msg = f"Processamento concluído. {total_processed} mensagens importadas."
    if skipped_files:
        msg += f" Arquivos ignorados (duplicados): {', '.join(skipped_files)}"
        
    return {"message": msg}

@router.get("/files/{operacao_id}")
def list_imported_files(operacao_id: int, db: Session = Depends(get_db)):
    """Lista todos os arquivos importados de uma operação"""
    arquivos = db.query(models.Arquivo).filter(
        models.Arquivo.operacao_id == operacao_id
    ).order_by(models.Arquivo.data_upload.desc()).all()
    
    return [{
        "id": arq.id,
        "nome": arq.nome,
        "data_upload": arq.data_upload.strftime('%d/%m/%Y %H:%M') if arq.data_upload else None,
        "alvo_numero": arq.alvo_numero,
        "periodo_inicio": arq.periodo_inicio,
        "periodo_fim": arq.periodo_fim
    } for arq in arquivos]
