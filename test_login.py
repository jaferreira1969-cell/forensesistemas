# Script para testar login localmente
import requests

# Testar localmente
# url = "http://localhost:8000/api/auth/login"

# Testar no Vercel
url = "https://forense.vercel.app/api/auth/login"

data = {
    "username": "mario.reis@pcdf.df.gov.br",  # Coloque seu email aqui
    "password": "sua_senha"  # Coloque sua senha aqui
}

try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
