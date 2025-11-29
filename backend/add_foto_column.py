import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('forense.db')
cursor = conn.cursor()

try:
    # Verificar se a coluna já existe
    cursor.execute("PRAGMA table_info(telefones)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'foto' not in columns:
        print("Adicionando coluna 'foto' à tabela 'telefones'...")
        cursor.execute("ALTER TABLE telefones ADD COLUMN foto TEXT")
        conn.commit()
        print("Coluna 'foto' adicionada com sucesso!")
    else:
        print("Coluna 'foto' já existe na tabela 'telefones'.")
        
except Exception as e:
    print(f"Erro: {e}")
    conn.rollback()
finally:
    conn.close()
