from mangum import Mangum
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Importar o app FastAPI existente
from main import app

# Configurar root_path para Vercel
app.root_path = "/api"

# Criar handler para Vercel com lifespan desabilitado
handler = Mangum(app, lifespan="off")
