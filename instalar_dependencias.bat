@echo off
echo ==========================================
echo      Instalador do Sistema Forense
echo ==========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale o Python em https://www.python.org/downloads/
    echo IMPORTANTE: Marque a opcao "Add Python to PATH" na instalacao.
    pause
    exit /b
)

REM Verificar Node.js
call npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado!
    echo Por favor, instale o Node.js em https://nodejs.org/
    pause
    exit /b
)

echo [OK] Python e Node.js detectados.
echo.

echo [1/2] Configurando Backend...
cd backend
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)
call venv\Scripts\activate
echo Instalando dependencias do Python...
pip install -r requirements.txt
cd ..

echo.
echo [2/2] Configurando Frontend...
cd frontend
echo Instalando dependencias do React (isso pode demorar um pouco)...
call npm install
cd ..

echo.
echo ==========================================
echo Instalacao concluida com sucesso!
echo.
echo Para usar o sistema:
echo 1. Clique duas vezes em 'iniciar_sistema.bat'
echo ==========================================
pause
