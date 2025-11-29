# Sistema Forense de Análise de Chamadas

Sistema web completo para análise e tratamento de dados de chamadas telefônicas de operações de investigação.

## Funcionalidades

### 📊 Gestão de Operações
- Sistema multi-operações com dados isolados por caso
- Seletor para alternar entre diferentes investigações

### 📁 Importação de Dados
- Upload de múltiplos arquivos HTML
- Processamento automático com parsing de dados
- Extração de informações: ALVO, REMETENTE, DESTINATÁRIO, IP, PORTA, Data/Hora

### 📈 Dashboard Analítico
- Total de telefones localizados
- Estatísticas por telefone
- Gráfico de evolução temporal de mensagens
- Métricas de comunicação

### 🕸️ Visualização em Grafos
- **Grafo Geral**: Rede completa de comunicações
- **Grafo de IPs Comuns**: Telefones conectados a IPs compartilhados
- Interatividade: zoom, pan, clique para detalhes

### 🗺️ Geolocalização de IPs
- Mapa interativo com marcadores de IPs
- Sincronização automática via API de geolocalização
- Informações detalhadas: localização, provedor, quantidade de mensagens

### 📋 Lista de Mensagens
- Tabela paginada e pesquisável
- Filtros avançados
- Exportação de dados

## Stack Tecnológica

### Backend
- **Framework**: FastAPI (Python)
- **Banco de Dados**: SQLite
- **ORM**: SQLAlchemy
- **Validação**: Pydantic
- **Parsing**: BeautifulSoup4

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Estilização**: Tailwind CSS
- **Grafos**: Cytoscape.js
- **Mapas**: Leaflet
- **Gráficos**: Recharts
- **Roteamento**: React Router

## Instalação

### Pré-requisitos
- Python 3.8+
- Node.js 16+ e npm
- Git (opcional)

### Backend

1. Navegue até a pasta do backend:
```bash
cd backend
```

2. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

3. Inicie o servidor:
```bash
uvicorn main:app --reload
```

O backend estará disponível em `http://localhost:8000`

### Frontend

1. Navegue até a pasta do frontend:
```bash
cd frontend
```

2. Instale as dependências:
```bash
npm install
```

3. Inicie o servidor de desenvolvimento:
```bash
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

## Estrutura do Projeto

```
Forense/
├── backend/
│   ├── main.py              # Aplicação FastAPI principal
│   ├── database.py          # Configuração do banco de dados
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── routers/             # Endpoints da API
│   │   ├── operations.py    # CRUD de operações
│   │   ├── upload.py        # Upload de arquivos
│   │   ├── dashboard.py     # Estatísticas
│   │   ├── graph.py         # Dados de grafos
│   │   ├── geolocation.py   # Geolocalização
│   │   └── messages.py      # Listagem de mensagens
│   ├── services/            # Lógica de negócio
│   │   ├── parser.py        # Parser HTML
│   │   └── geolocation.py   # API de geolocalização
│   └── requirements.txt     # Dependências Python
│
└── frontend/
    ├── src/
    │   ├── pages/           # Páginas da aplicação
    │   │   ├── Dashboard.tsx
    │   │   ├── Upload.tsx
    │   │   ├── GraphView.tsx
    │   │   ├── MapView.tsx
    │   │   └── Messages.tsx
    │   ├── components/      # Componentes reutilizáveis
    │   │   ├── Graph.tsx
    │   │   └── ui/          # Componentes UI (shadcn)
    │   ├── services/        # API client
    │   │   └── api.ts
    │   ├── App.tsx          # Componente principal
    │   └── main.tsx         # Entry point
    ├── package.json
    └── vite.config.ts

```

## Uso

### 1. Criar uma Operação
- Acesse a página "Importar"
- Crie uma nova operação ou selecione uma existente

### 2. Importar Dados
- Faça upload de arquivos HTML com dados de chamadas
- O sistema processará automaticamente

### 3. Visualizar Dashboard
- Acesse o Dashboard para ver estatísticas gerais
- Gráficos de evolução temporal
- Totais de telefones, mensagens e IPs

### 4. Explorar Grafos
- Visualize a rede de comunicações
- Alterne entre "Grafo Geral" e "IPs Comuns"
- Interaja com os nós para ver detalhes

### 5. Mapear IPs
- Clique em "Sincronizar IPs" para geolocalizar
- Visualize marcadores no mapa
- Clique nos marcadores para ver detalhes

### 6. Pesquisar Mensagens
- Use a barra de pesquisa para filtrar
- Navegue entre páginas
- Exporte dados conforme necessário

## API Endpoints

### Operações
- `GET /operacoes/` - Listar operações
- `POST /operacoes/` - Criar operação
- `GET /operacoes/{id}` - Detalhes da operação
- `DELETE /operacoes/{id}` - Deletar operação

### Upload
- `POST /upload/` - Upload de arquivos HTML

### Dashboard
- `GET /dashboard/{id}/stats` - Estatísticas
- `GET /dashboard/{id}/telefones` - Lista de telefones
- `GET /dashboard/{id}/evolution` - Evolução temporal

### Grafos
- `GET /graph/{id}/general` - Grafo geral
- `GET /graph/{id}/common-ips` - Grafo de IPs comuns

### Geolocalização
- `POST /geolocation/{id}/sync` - Sincronizar geolocalização
- `GET /geolocation/{id}/map` - Dados para mapa

### Mensagens
- `GET /mensagens/{id}` - Listar mensagens (com paginação e busca)

## Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:
- `operacoes` - Operações/Casos
- `telefones` - Telefones identificados
- `ips` - Endereços IP e geolocalização
- `mensagens` - Registros de mensagens
- `comunicacoes` - Agregação de comunicações para grafos

## Desenvolvimento

### Backend
```bash
# Com hot-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Modo desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview da build
npm run preview
```

## Solução de Problemas

### Backend não inicia
- Verifique se todas as dependências estão instaladas: `pip install -r requirements.txt`
- Confirme que Python 3.8+ está instalado

### Frontend não compila
- Delete `node_modules` e `package-lock.json`, reinstale: `npm install`
- Verifique a versão do Node.js: `node -v` (deve ser 16+)

### CORS Errors
- Certifique-se de que o backend está rodando na porta 8000
- Verifique a configuração de CORS em `backend/main.py`

### Geolocalização não funciona
- A API gratuita tem limite de requisições
- Aguarde alguns segundos entre sincronizações

## Licença

Este projeto foi desenvolvido para fins de investigação forense.

## Suporte

Para questões ou problemas, consulte a documentação ou entre em contato com a equipe de desenvolvimento.
