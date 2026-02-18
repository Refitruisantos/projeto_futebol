# Futebol Analytics - Web Application

Sistema web para gestão e análise de dados GPS e PSE de futebol (FastAPI + React).

## 📁 Estrutura

```
09_IMPLEMENTACAO_TECNICA/
├── backend/          # FastAPI REST API
│   ├── main.py
│   ├── database.py
│   ├── routers/
│   │   ├── athletes.py
│   │   ├── sessions.py
│   │   ├── metrics.py
│   │   └── ingestion.py
│   └── requirements.txt
│
└── frontend/         # React + Vite
    ├── src/
    │   ├── pages/
    │   ├── components/
    │   └── api/
    └── package.json
```

## 🚀 Setup e Instalação

### Backend (FastAPI)

```powershell
# Ir para a pasta backend
cd backend

# Instalar dependências
pip install -r requirements.txt

# Garantir que .env existe na pasta pai (09_IMPLEMENTACAO_TECNICA/)
# com as credenciais da base de dados

# Iniciar servidor (porta 8000)
uvicorn main:app --reload
```

### Frontend (React)

```powershell
# Ir para a pasta frontend
cd frontend

# Instalar dependências (primeira vez)
npm install

# Iniciar servidor de desenvolvimento (porta 5173)
npm run dev
```

## 🔗 URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## 📊 Funcionalidades

### Dashboard
- Visão geral da equipa
- Top 5 atletas por carga (7 dias)
- Atletas em risco (ACWR > 1.5)
- Resumo de sessões

### Atletas
- Lista completa de atletas
- Perfil individual com métricas
- Histórico de sessões recentes
- ACWR, monotonia, strain

### Sessões
- Treinos e jogos
- Dados GPS por atleta/sessão
- Comparação de métricas

### Upload
- Carregar ficheiros CSV Catapult
- Histórico de uploads
- Deteção automática de duplicados

## 🔐 Autenticação (Futuro)

Atualmente o sistema não tem autenticação. Para produção, adicionar:
- JWT tokens
- Roles (admin, coach, physio)
- Login page

## 📝 API Endpoints

### Athletes
- `GET /api/athletes/` - Lista atletas
- `GET /api/athletes/{id}` - Detalhes atleta
- `GET /api/athletes/{id}/metrics` - Métricas

### Sessions
- `GET /api/sessions/` - Lista sessões
- `GET /api/sessions/{id}` - Detalhes sessão

### Metrics
- `GET /api/metrics/team/dashboard` - Dashboard equipa
- `GET /api/metrics/team/summary` - Resumo equipa

### Ingestion
- `POST /api/ingest/catapult` - Upload Catapult CSV
- `GET /api/ingest/history` - Histórico uploads

## 🔧 Configuração

### Variáveis de Ambiente

O backend usa as mesmas variáveis `.env` da pasta pai:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=futebol_tese
DB_USER=postgres
DB_PASSWORD=sua_senha
```

### CORS

Backend permite requisições de:
- `http://localhost:5173` (Vite dev)
- `http://localhost:3000` (alternativo)

Editar em `backend/main.py` se necessário.

## 📦 Dependências

### Backend
- FastAPI
- Uvicorn
- psycopg2-binary
- pandas
- python-dotenv

### Frontend
- React 18
- React Router
- Axios
- TailwindCSS
- Lucide Icons
- Vite

## 🐛 Troubleshooting

### Backend não inicia
- Verificar se PostgreSQL está a correr
- Confirmar credenciais `.env`
- Testar conexão: `python scripts/testar_instalacao.py`

### Frontend não conecta ao backend
- Verificar se backend está em http://localhost:8000
- Ver erros de CORS na consola do browser
- Confirmar proxy em `frontend/vite.config.js`

### Upload de CSV falha
- Verificar formato do CSV (headers corretos)
- Nomes de jogadores devem existir na tabela `atletas`
- Ver resposta detalhada em `/docs` (Swagger)

## 📚 Próximos Passos

1. **Adicionar autenticação** (JWT)
2. **Gráficos interativos** (evolução temporal)
3. **Exportar relatórios** (PDF/Excel)
4. **Notificações** (alertas em tempo real)
5. **Deploy** (Docker + Nginx)

## 🎓 Contexto Tese

Sistema desenvolvido para gestão de dados GPS (Catapult) e PSE no âmbito de tese de doutoramento em Ciências do Desporto. Base de dados PostgreSQL + TimescaleDB para séries temporais.
