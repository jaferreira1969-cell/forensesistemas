@echo off
echo ============================================
echo   Iniciando Backend - Supabase (PostgreSQL)
echo ============================================
echo.

REM Configurar connection string do Supabase
set DATABASE_URL=postgresql://postgres.gxgixydlxmoyhhuummmg:TSpjxZJhUGs6cNuA@aws-0-us-west-2.pooler.supabase.com:6543/postgres

echo Database: Supabase PostgreSQL
echo Host: aws-0-us-west-2.pooler.supabase.com
echo.
echo Iniciando servidor...
echo.

python main.py
