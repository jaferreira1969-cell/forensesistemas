"""
Script para deletar uma operação e todos os dados relacionados
Executa as exclusões em lotes para evitar timeout do Supabase
"""
import os
import sys
from sqlalchemy import create_engine, text

# Pegar URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERRO: Variável DATABASE_URL não encontrada!")
    exit(1)

if len(sys.argv) < 2:
    print("❌ ERRO: Informe o ID da operação a ser deletada!")
    print("Uso: python delete_operacao.py <operacao_id>")
    exit(1)

operacao_id = int(sys.argv[1])

print(f"🗑️  Deletando operação ID {operacao_id} e todos os dados relacionados...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # 1. Deletar mensagens (em lotes de 1000)
        print("  📧 Deletando mensagens...")
        while True:
            result = conn.execute(text(f"DELETE FROM mensagens WHERE operacao_id = {operacao_id} AND id IN (SELECT id FROM mensagens WHERE operacao_id = {operacao_id} LIMIT 1000)"))
            conn.commit()
            if result.rowcount == 0:
                break
            print(f"    Deletadas {result.rowcount} mensagens")
        
        # 2. Deletar comunicações
        print("  📞 Deletando comunicações...")
        conn.execute(text(f"DELETE FROM comunicacoes WHERE operacao_id = {operacao_id}"))
        conn.commit()
        
        # 3. Deletar arquivos
        print("  📁 Deletando arquivos...")
        conn.execute(text(f"DELETE FROM arquivos WHERE operacao_id = {operacao_id}"))
        conn.commit()
        
        # 4. Deletar telefones
        print("  📱 Deletando telefones...")
        conn.execute(text(f"DELETE FROM telefones WHERE operacao_id = {operacao_id}"))
        conn.commit()
        
        # 5. Deletar operação
        print("  🗑️  Deletando operação...")
        conn.execute(text(f"DELETE FROM operacoes WHERE id = {operacao_id}"))
        conn.commit()
        
    print("✅ Operação deletada com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)
