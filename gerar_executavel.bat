@echo off
echo ==========================================
echo      Gerador de Executavel (Forense)
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b
)

echo [1/3] Construindo Frontend (React)...
cd frontend
call npm install
call npm run build
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao construir o Frontend.
    pause
    exit /b
)
cd ..

echo.
echo [2/3] Preparando Backend...
cd backend
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)
call venv\Scripts\activate
echo Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [3/3] Gerando Executavel (PyInstaller)...
REM --onefile: arquivo unico
REM --noconsole: nao mostra janela preta (opcional, deixei sem para debug por enquanto)
REM --add-data: inclui a pasta dist do frontend dentro do executavel
REM --name: nome do arquivo final
pyinstaller --noconfirm --onefile --console --name "Forense" --paths=. --add-data "../frontend/dist;static" --hidden-import="uvicorn.logging" --hidden-import="uvicorn.loops" --hidden-import="uvicorn.loops.auto" --hidden-import="uvicorn.protocols" --hidden-import="uvicorn.protocols.http" --hidden-import="uvicorn.protocols.http.auto" --hidden-import="uvicorn.lifespan" --hidden-import="uvicorn.lifespan.on" --hidden-import="database" --hidden-import="models" --hidden-import="schemas" --hidden-import="routers" --hidden-import="services" --hidden-import="sqlite3" --hidden-import="pypdf" main.py

echo.
echo ==========================================
echo Processo concluido!
echo O executavel esta na pasta: backend\dist\Forense.exe
echo.
echo Copie este arquivo 'Forense.exe' para onde quiser.
echo O banco de dados 'forense.db' sera criado na mesma pasta dele.
echo ==========================================
pause
