@echo off
echo Iniciando backend com Supabase (PostgreSQL)...
set DATABASE_URL=postgresql://[SEU_USUARIO]:[SUA_SENHA]@[SEU_HOST].supabase.co:5432/postgres
python main.py
