@echo off
echo ==========================================
echo      Iniciando Sistema Forense
echo ==========================================

echo.
echo [1/2] Iniciando Backend (Python)...
if exist backend\venv (
    start "Forense Backend" cmd /k "cd backend && venv\Scripts\activate && python main.py"
) else (
    start "Forense Backend" cmd /k "cd backend && python main.py"
)

echo.
echo [2/2] Iniciando Frontend (React)...
start "Forense Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo Sistema iniciado! 
echo O navegador deve abrir em breve.
echo Mantenha as janelas pretas abertas.
echo ==========================================
pause
