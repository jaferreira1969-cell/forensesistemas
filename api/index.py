from fastapi import FastAPI
from mangum import Mangum
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Importar o app FastAPI existente
# Importar o app FastAPI existente
from main import app

# Configurar root_path para Vercel (já que usamos rewrite /api/...)
app.root_path = "/api"

# Criar handler para Vercel
handler = Mangum(app)
