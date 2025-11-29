"""
Script de migração para adicionar campos de metadados à tabela arquivos
Execute este script uma vez para atualizar o banco de dados
"""
import os
from sqlalchemy import create_engine, text

# Pegar URL do banco de dados (Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERRO: Variável DATABASE_URL não encontrada!")
    print("Execute este script com:")
    print('$env:DATABASE_URL="postgresql://..."; python migrate_arquivos_metadata.py')
    exit(1)

print("🔧 Conectando ao banco de dados...")
engine = create_engine(DATABASE_URL)

# SQL para adicionar as colunas
migration_sql = """
-- Adicionar coluna alvo_numero (Account Identifier)
ALTER TABLE arquivos 
ADD COLUMN IF NOT EXISTS alvo_numero VARCHAR(50);

-- Adicionar coluna periodo_inicio
ALTER TABLE arquivos 
ADD COLUMN IF NOT EXISTS periodo_inicio VARCHAR(100);

-- Adicionar coluna periodo_fim
ALTER TABLE arquivos 
ADD COLUMN IF NOT EXISTS periodo_fim VARCHAR(100);
"""

print("📝 Executando migração...")
try:
    with engine.connect() as conn:
        # Executar cada comando SQL
        for statement in migration_sql.strip().split(';'):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()
    
    print("✅ Migração concluída com sucesso!")
    print("\nColunas adicionadas:")
    print("  - alvo_numero (VARCHAR)")
    print("  - periodo_inicio (VARCHAR)")
    print("  - periodo_fim (VARCHAR)")
    
except Exception as e:
    print(f"❌ Erro durante migração: {e}")
    exit(1)

print("\n🎉 Agora você pode importar arquivos e os metadados serão extraídos!")
