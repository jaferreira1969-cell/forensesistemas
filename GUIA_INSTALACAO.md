# 🚀 Guia de Instalação - Sistema Forense

Este guia explica como configurar e rodar o Sistema Forense em um novo computador.

## 📋 Pré-requisitos

Antes de começar, você precisa instalar dois programas no computador:

1.  **Python** (para o Backend)
    *   Baixe em: [python.org](https://www.python.org/downloads/)
    *   **IMPORTANTE:** Na instalação, marque a opção **"Add Python to PATH"**.
2.  **Node.js** (para o Frontend)
    *   Baixe em: [nodejs.org](https://nodejs.org/) (Versão LTS recomendada).

---

## ⚙️ Instalação Passo a Passo

### 1. Copiar os Arquivos
Copie a pasta inteira do projeto `Forense` para o novo computador.

### 2. Instalar Dependências (Automático)
Dê um duplo clique no arquivo **`instalar_dependencias.bat`**.

Ele vai verificar se você tem Python e Node.js e instalar tudo o que o sistema precisa automaticamente.

*Se der erro dizendo que Python ou Node não foram encontrados, instale-os usando os links acima e tente novamente.*

---

## ▶️ Como Rodar o Sistema

Para facilitar, criei um arquivo chamado **`iniciar_sistema.bat`** na pasta principal.

1.  Dê um duplo clique em **`iniciar_sistema.bat`**.
2.  Duas janelas pretas vão abrir (uma para o Backend, outra para o Frontend).
3.  O sistema deve abrir automaticamente no seu navegador (geralmente em `http://localhost:5173`).

**Nota:** Não feche as janelas pretas enquanto estiver usando o sistema.

---

## 🛠️ Solução de Problemas Comuns

*   **Erro "python não encontrado":** Verifique se marcou "Add Python to PATH" na instalação.
*   **Erro "npm não encontrado":** Reinicie o computador após instalar o Node.js.
*   **Porta em uso:** Se der erro de porta, verifique se não há outro sistema rodando na porta 8000 ou 5173.
