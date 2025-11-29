@echo off
echo ============================================
echo   Configurando GitHub + Vercel Automatico
echo ============================================
echo.

REM Adicionar Git ao PATH da sessao atual
set PATH=%PATH%;C:\Program Files\Git\cmd

echo [1/7] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Git nao encontrado!
    echo Por favor, abra um NOVO PowerShell e execute novamente.
    pause
    exit /b 1
)
echo OK - Git encontrado
echo.

echo [2/7] Configurando identidade do Git...
git config user.name "jaferreira1969-cell"
git config user.email "jaferreira1969@gmail.com"
echo OK - Identidade configurada
echo.

echo [3/7] Inicializando repositorio Git...
git init
echo OK - Git inicializado
echo.

echo [4/7] Configurando repositorio remoto...
git remote remove origin 2>nul
git remote add origin https://github.com/jaferreira1969-cell/forensesistemas.git
echo OK - Remoto configurado
echo.

echo [5/7] Adicionando arquivos...
git add .
echo OK - Arquivos adicionados
echo.

echo [6/7] Criando commit...
git commit -m "Deploy automatico via GitHub + Vercel"
echo OK - Commit criado
echo.

echo [7/7] Enviando para GitHub...
echo.
echo ATENCAO: O GitHub vai pedir suas credenciais!
echo Usuario: jaferreira1969-cell
echo Senha: Use um Personal Access Token (NAO a senha normal)
echo.
echo Para criar token: https://github.com/settings/tokens
echo Marque: repo (todas as opcoes)
echo.
pause

git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ERRO no push! Verifique suas credenciais.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   SUCESSO! Codigo enviado para GitHub!
echo ============================================
echo.
echo Proximo Passo: Conectar Vercel ao GitHub
echo.
echo 1. Acesse: https://vercel.com/dashboard
echo 2. Clique em "Add New..." - "Project"
echo 3. Clique em "Import Git Repository"
echo 4. Selecione "forensesistemas"
echo 5. Configure as variaveis de ambiente:
echo    - DATABASE_URL = postgresql://postgres.gxgixydlxmoyhhuummmg:TSpjxZJhUGs6cNuA@aws-0-us-west-2.pooler.supabase.com:6543/postgres
echo    - SECRET_KEY = OykmZfZ10bToETAu_2eE-dAlXAeIu1BQALfCazXVPKE
echo 6. Clique "Deploy"
echo.
echo Pronto! A partir de agora, todo "git push" faz deploy automatico!
echo.
pause
