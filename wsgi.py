import sys
import os

# Adicionar o diretório do projeto ao path
project_home = '/home/SEU_USERNAME/forensesistemas'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Adicionar o diretório backend ao path
backend_path = os.path.join(project_home, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Importar a aplicação FastAPI
from main import app

# PythonAnywhere precisa de uma aplicação chamada "application"
application = app
