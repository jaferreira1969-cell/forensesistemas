"""
Script para limpar mensagens com campos vazios do banco de dados.
Remove mensagens onde remetente, destinatário ou data_hora estão vazios/nulos.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from database import SQLALCHEMY_DATABASE_URL, Base
from models import Mensagem

# Criar engine e sessão
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def cleanup_empty_messages():
    db = SessionLocal()
    
    try:
        # Contar total de mensagens antes da limpeza
        total_antes = db.query(Mensagem).count()
        print(f"\nTotal de mensagens antes da limpeza: {total_antes}")
        
        # Buscar mensagens com campos vazios ou nulos
        mensagens_invalidas = db.query(Mensagem).filter(
            or_(
                Mensagem.remetente == None,
                Mensagem.remetente == '',
                Mensagem.destinatario == None,
                Mensagem.destinatario == '',
                Mensagem.data_hora == None,
                Mensagem.ip_id == None
            )
        ).all()
        
        count_invalidas = len(mensagens_invalidas)
        
        if count_invalidas == 0:
            print("Nenhuma mensagem com campos vazios encontrada!")
            return
        
        print(f"\nEncontradas {count_invalidas} mensagens com campos vazios:")
        
        # Contar por tipo de problema
        sem_remetente = 0
        sem_destinatario = 0
        sem_data = 0
        sem_ip = 0
        
        for msg in mensagens_invalidas:
            if not msg.remetente or msg.remetente.strip() == '':
                sem_remetente += 1
            if not msg.destinatario or msg.destinatario.strip() == '':
                sem_destinatario += 1
            if not msg.data_hora:
                sem_data += 1
            if not msg.ip_id:
                sem_ip += 1
        
        print(f"  - Sem remetente: {sem_remetente}")
        print(f"  - Sem destinatário: {sem_destinatario}")
        print(f"  - Sem data/hora: {sem_data}")
        print(f"  - Sem IP: {sem_ip}")
        
        # Deletar as mensagens inválidas
        print(f"\nRemovendo {count_invalidas} mensagens...")
        
        for msg in mensagens_invalidas:
            db.delete(msg)
        
        db.commit()
        
        # Contar total após limpeza
        total_depois = db.query(Mensagem).count()
        
        print(f"\nLimpeza concluida!")
        print(f"Total de mensagens apos limpeza: {total_depois}")
        print(f"Mensagens removidas: {count_invalidas}")
        
    except Exception as e:
        print(f"\nErro durante a limpeza: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("LIMPEZA DE MENSAGENS COM CAMPOS VAZIOS")
    print("=" * 60)
    cleanup_empty_messages()
    print("=" * 60)
