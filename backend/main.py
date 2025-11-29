from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import operations, upload, dashboard, graph, geolocation, messages, dashboard_extended, export, telefones, intelligence, auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Forense de Análise de Chamadas")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens em desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import webbrowser
from threading import Timer

# Include routers
app.include_router(auth.router)
app.include_router(operations.router)
app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(dashboard_extended.router)
app.include_router(graph.router)
app.include_router(geolocation.router)
app.include_router(messages.router)
app.include_router(export.router)
app.include_router(telefones.router)
app.include_router(intelligence.router)

# Configuração para servir o Frontend (React)
# Se estiver rodando como executável, os arquivos estáticos estarão na pasta temporária
if getattr(sys, 'frozen', False):
    static_dir = os.path.join(sys._MEIPASS, "static")
else:
    # Se estiver rodando como script, assume que a pasta 'dist' está em ../frontend/dist
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")

if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    # Rota raiz explícita
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

    # Rota "catch-all" para o React Router (SPA)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Se for uma chamada de API, não interfere (já foi tratada pelos routers acima)
        if full_path.startswith("api"):
            return {"error": "API endpoint not found"}
            
        # Verifica se o arquivo existe na raiz estática (ex: favicon.ico)
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Se não for arquivo, retorna o index.html (SPA)
        return FileResponse(os.path.join(static_dir, "index.html"))
else:
    print(f"AVISO: Pasta estática não encontrada em {static_dir}")

def open_browser():
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    # Abrir navegador após 1.5 segundos (dá tempo do servidor subir)
    Timer(1.5, open_browser).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
