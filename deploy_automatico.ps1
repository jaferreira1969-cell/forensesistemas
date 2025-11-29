# Script de Deploy Automatizado - Vercel
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Deploy Automatizado - Vercel" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Git
Write-Host "[1/5] Verificando Git..." -ForegroundColor Yellow
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "Instalando Git..." -ForegroundColor Yellow
    winget install --id Git.Git -e --silent
    Write-Host "Git instalado! REINICIE o terminal e execute novamente." -ForegroundColor Green
    Read-Host "Pressione Enter"
    exit
}
Write-Host "OK - Git instalado" -ForegroundColor Green

# Verificar Node
Write-Host ""
Write-Host "[2/5] Verificando Node.js..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "Instalando Node.js..." -ForegroundColor Yellow
    winget install OpenJS.NodeJS.LTS --silent
    Write-Host "Node.js instalado! REINICIE o terminal e execute novamente." -ForegroundColor Green
    Read-Host "Pressione Enter"
    exit
}
Write-Host "OK - Node.js instalado" -ForegroundColor Green

# Instalar Vercel CLI
Write-Host ""
Write-Host "[3/5] Instalando Vercel CLI..." -ForegroundColor Yellow
npm install -g vercel 2>&1 | Out-Null
Write-Host "OK - Vercel CLI instalado" -ForegroundColor Green

# Inicializar Git
Write-Host ""
Write-Host "[4/5] Configurando Git..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    Write-Host "Git inicializado" -ForegroundColor Green
}

# Verificar usuário Git
$gitUser = git config user.name
if (-not $gitUser) {
    Write-Host ""
    $nome = Read-Host "Digite seu nome"
    $email = Read-Host "Digite seu email"
    git config user.name "$nome"
    git config user.email "$email"
    Write-Host "Usuário configurado" -ForegroundColor Green
}

# Criar .gitignore
if (-not (Test-Path ".gitignore")) {
    @"
__pycache__/
*.pyc
venv/
.venv/
*.db
node_modules/
dist/
.env
start_backend.bat
.vercel
"@ | Out-File ".gitignore" -Encoding UTF8
    Write-Host ".gitignore criado" -ForegroundColor Green
}

# Commit
Write-Host ""
Write-Host "[5/5] Criando commit..." -ForegroundColor Yellow
git add .
git commit -m "Deploy Vercel" 2>&1 | Out-Null
Write-Host "OK - Commit criado" -ForegroundColor Green

# Instruções finais
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AGORA EXECUTE:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. vercel login" -ForegroundColor Yellow
Write-Host "   (Login no Vercel)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. vercel" -ForegroundColor Yellow
Write-Host "   (Deploy de teste)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. No Dashboard Vercel, adicione:" -ForegroundColor Yellow
Write-Host "   DATABASE_URL = postgresql://..." -ForegroundColor Gray
Write-Host "   SECRET_KEY = (gere com: python -c 'import secrets; print(secrets.token_urlsafe(32))')" -ForegroundColor Gray
Write-Host ""
Write-Host "4. vercel --prod" -ForegroundColor Yellow
Write-Host "   (Deploy em produção)" -ForegroundColor Gray
Write-Host ""

$login = Read-Host "Executar 'vercel login' agora? (S/N)"
if ($login -eq "S") {
    vercel login
}

Write-Host ""
Write-Host "Pronto!" -ForegroundColor Green
