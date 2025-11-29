import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Obter URL do ambiente ou pedir
url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL não encontrada no ambiente.")
    url = input("Cole sua connection string do Supabase: ").strip()

if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("\n--- Verificando Conexão ---")
    result = db.execute(text("SELECT 1")).scalar()
    print(f"Conexão com Banco: {'OK' if result == 1 else 'FALHA'}")
    
    print("\n--- Verificando Usuários ---")
    try:
        result = db.execute(text("SELECT id, username, email FROM users"))
        users = result.fetchall()
        if users:
            print(f"Encontrados {len(users)} usuários:")
            for u in users:
                print(f" - ID: {u.id} | User: {u.username} | Email: {u.email}")
        else:
            print("NENHUM USUÁRIO ENCONTRADO NA TABELA 'users'.")
            print("Você precisa criar um usuário primeiro (via /register ou script).")
    except Exception as e:
        print(f"Erro ao ler tabela users: {e}")
        print("A tabela 'users' pode não existir ainda.")

except Exception as e:
    print(f"\nERRO CRÍTICO DE CONEXÃO: {e}")
