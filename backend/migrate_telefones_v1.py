"""
Script de migração para adicionar campos categoria e observacoes na tabela telefones.
Execute uma vez para atualizar o banco de dados existente.
"""
from database import engine, get_db
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Adicionar coluna categoria
        try:
            conn.execute(text("ALTER TABLE telefones ADD COLUMN categoria VARCHAR"))
            print("✓ Coluna 'categoria' adicionada")
        except Exception as e:
            print(f"⚠ Coluna 'categoria' já existe ou erro: {e}")
        
        # Adicionar coluna observacoes
        try:
            conn.execute(text("ALTER TABLE telefones ADD COLUMN observacoes VARCHAR"))
            print("✓ Coluna 'observacoes' adicionada")
        except Exception as e:
            print(f"⚠ Coluna 'observacoes' já existe ou erro: {e}")
        
        conn.commit()
        print("\n✅ Migração concluída!")

if __name__ == "__main__":
    migrate()
