from database import engine, Base
import models

# Create all tables that don't exist
Base.metadata.create_all(bind=engine)

print("Tabela 'arquivos' criada com sucesso (se não existia).")
