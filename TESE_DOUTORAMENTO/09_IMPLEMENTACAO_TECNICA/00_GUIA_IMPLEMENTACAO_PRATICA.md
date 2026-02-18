# Guia de Implementação Prática
## Sistema de Base de Dados Temporal para Tese

---

## 🎯 Objetivo

Implementar na prática o sistema PostgreSQL + TimescaleDB descrito no capítulo de metodologia, com todos os scripts prontos a executar.

---

## 📋 Pré-requisitos

### Software Necessário
- **PostgreSQL 14+** (ou 15/16)
- **TimescaleDB 2.10+**
- **Python 3.10+**
- **Git** (opcional, recomendado)

### Hardware Mínimo
- 8GB RAM
- 50GB espaço disco (para dados de 2 épocas)
- Processador quad-core

---

## 🚀 Instalação Rápida (Windows)

### Opção 1: Instalação Manual

#### Passo 1: Instalar PostgreSQL
```powershell
# Download do instalador oficial
# https://www.postgresql.org/download/windows/

# Ou via winget (Windows 11)
winget install PostgreSQL.PostgreSQL
```

**Configurações na instalação**:
- Porta: `5432` (padrão)
- Username: `postgres`
- Password: **[escolher uma senha forte]**
- Locale: `Portuguese, Portugal`

#### Passo 2: Instalar TimescaleDB
```powershell
# Download da extensão
# https://docs.timescale.com/install/latest/self-hosted/installation-windows/

# Após download, executar instalador
# Selecionar a versão do PostgreSQL instalada (14, 15 ou 16)
```

#### Passo 3: Ativar TimescaleDB
```sql
-- Conectar ao PostgreSQL como superuser
psql -U postgres

-- Criar base de dados
CREATE DATABASE futebol_tese;

-- Conectar à base
\c futebol_tese

-- Ativar extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Verificar instalação
\dx
```

✅ Se ver `timescaledb` na lista, está instalado corretamente!

---

### Opção 2: Docker (Recomendado para Testes)

#### Passo 1: Instalar Docker Desktop
```powershell
# Download: https://www.docker.com/products/docker-desktop/
# Ou via winget
winget install Docker.DockerDesktop
```

#### Passo 2: Criar docker-compose.yml
Ver ficheiro `docker-compose.yml` nesta pasta.

#### Passo 3: Iniciar Container
```powershell
# Na pasta do projeto
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

# Iniciar PostgreSQL + TimescaleDB
docker-compose up -d

# Verificar se está a correr
docker ps

# Logs
docker-compose logs -f
```

---

## 📁 Estrutura de Ficheiros

```
09_IMPLEMENTACAO_TECNICA/
├── 00_GUIA_IMPLEMENTACAO_PRATICA.md    # Este ficheiro
├── docker-compose.yml                   # Setup Docker
├── requirements.txt                     # Dependências Python
│
├── sql/
│   ├── 01_criar_schema.sql             # Criar tabelas
│   ├── 02_criar_hypertables.sql        # Converter para TimescaleDB
│   ├── 03_indices_otimizacao.sql       # Criar índices
│   ├── 04_continuous_aggregates.sql    # Agregações automáticas
│   ├── 05_funcoes_auxiliares.sql       # Funções úteis (ACWR, etc.)
│   ├── 06_politicas_compressao.sql     # Compressão de dados
│   └── 99_queries_exemplo.sql          # Queries úteis
│
├── python/
│   ├── 01_conexao_db.py                # Classe de conexão
│   ├── 02_inserir_dados_gps.py         # Inserir dados GPS
│   ├── 03_inserir_dados_pse.py         # Inserir dados PSE
│   ├── 04_processar_pdf.py             # Parser de PDFs
│   ├── 05_validacao_dados.py           # Validar dados
│   ├── 06_backup_restore.py            # Backup automático
│   └── 07_queries_analise.py           # Queries para análise
│
└── scripts/
    ├── setup_completo.ps1               # Script automático Windows
    └── testar_instalacao.py             # Testar se tudo funciona
```

---

## ⚙️ Setup Completo Passo a Passo

### Passo 1: Criar Base de Dados
```powershell
# Executar
psql -U postgres -c "CREATE DATABASE futebol_tese;"
```

### Passo 2: Executar Scripts SQL (Ordem Importante!)
```powershell
cd sql

# 1. Schema base
psql -U postgres -d futebol_tese -f 01_criar_schema.sql

# 2. Hypertables
psql -U postgres -d futebol_tese -f 02_criar_hypertables.sql

# 3. Índices
psql -U postgres -d futebol_tese -f 03_indices_otimizacao.sql

# 4. Continuous aggregates
psql -U postgres -d futebol_tese -f 04_continuous_aggregates.sql

# 5. Funções
psql -U postgres -d futebol_tese -f 05_funcoes_auxiliares.sql

# 6. Compressão
psql -U postgres -d futebol_tese -f 06_politicas_compressao.sql
```

### Passo 4: Configurar Conexão
```powershell
# Criar ficheiro .env
echo "DB_HOST=localhost" > .env
echo "DB_PORT=5432" >> .env
echo "DB_NAME=futebol_tese" >> .env
echo "DB_USER=postgres" >> .env
echo "DB_PASSWORD=sua_senha_aqui" >> .env
```

### Passo 5: Testar Instalação
```powershell
python scripts/testar_instalacao.py
```

✅ Se todos os testes passarem, sistema está operacional!

---

## 🎯 Próximos Passos Após Setup

### 1. Inserir Dados de Teste
```powershell
# Dados fictícios para testar
python python/02_inserir_dados_gps.py --teste --n-sessoes 10
```

### 2. Executar Queries de Exemplo
```powershell
python python/07_queries_analise.py --atleta-id 1 --ultimos-dias 30
```

### 3. Processar PDFs Reais
```powershell
python python/04_processar_pdf.py --input "C:\caminho\para\relatorio.pdf"
```

---

## 🔍 Verificar se Está Tudo OK

### Checklist Rápida
```sql
-- 1. TimescaleDB ativo?
SELECT * FROM pg_extension WHERE extname = 'timescaledb';

-- 2. Hypertables criadas?
SELECT * FROM timescaledb_information.hypertables;

-- 3. Tabelas existem?
\dt

-- 4. Continuous aggregates?
SELECT * FROM timescaledb_information.continuous_aggregates;

-- 5. Políticas de compressão?
SELECT * FROM timescaledb_information.compression_settings;
```

---

## 📊 Dashboard de Monitorização

### Ver Estatísticas da Base de Dados
```sql
-- Tamanho de cada hypertable
SELECT 
    hypertable_name,
    pg_size_pretty(hypertable_size(hypertable_name::regclass)) AS size
FROM timescaledb_information.hypertables;

-- Número de chunks
SELECT 
    hypertable_name,
    COUNT(*) AS num_chunks
FROM timescaledb_information.chunks
GROUP BY hypertable_name;

-- Taxa de compressão
SELECT 
    hypertable_name,
    compression_status,
    pg_size_pretty(before_compression_total_bytes) AS original,
    pg_size_pretty(after_compression_total_bytes) AS compressed,
    ROUND(100.0 * after_compression_total_bytes / 
          NULLIF(before_compression_total_bytes, 0), 2) AS compression_ratio
FROM timescaledb_information.hypertable_compression_stats;
```

---

## 🆘 Resolução de Problemas

### Problema 1: "Extension timescaledb not found"
**Solução**:
```sql
-- Verificar se instalado
SELECT * FROM pg_available_extensions WHERE name = 'timescaledb';

-- Se não aparecer, reinstalar TimescaleDB
-- https://docs.timescale.com/install/latest/
```

### Problema 2: "Permission denied for schema timescaledb"
**Solução**:
```sql
-- Dar permissões ao user
GRANT ALL ON SCHEMA timescaledb TO postgres;
```

### Problema 3: Conexão Python Falha
**Solução**:
```python
# Verificar credenciais em .env
# Testar conexão manual
psql -U postgres -d futebol_tese -h localhost -p 5432
```

### Problema 4: Performance Lenta
**Solução**:
```sql
-- Executar ANALYZE
ANALYZE dados_gps;
ANALYZE dados_pse;

-- Verificar índices
\d+ dados_gps
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- **TimescaleDB**: https://docs.timescale.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **psycopg2** (Python): https://www.psycopg.org/docs/

### Tutoriais Úteis
- TimescaleDB Getting Started: https://docs.timescale.com/getting-started/latest/
- Time-series queries: https://docs.timescale.com/use-timescale/latest/

---

## ✅ Checklist Final

### Antes de Iniciar Recolha de Dados
- [ ] PostgreSQL instalado e a correr
- [ ] TimescaleDB ativado
- [ ] Todas as tabelas criadas
- [ ] Hypertables configuradas
- [ ] Índices criados
- [ ] Continuous aggregates ativos
- [ ] Funções auxiliares disponíveis
- [ ] Políticas de compressão ativas
- [ ] Python conecta com sucesso
- [ ] Backup automático configurado
- [ ] Queries de teste executadas com sucesso

---

## 🎓 Próximas Etapas (Tese)

1. **Estudo Piloto** (2 semanas)
   - Testar com 5 atletas
   - Validar pipeline completo
   - Ajustar scripts

2. **Recolha Época 1** (10 meses)
   - 28 atletas
   - Processar PDFs semanalmente
   - Monitorizar qualidade dados

3. **Análise de Dados** (4 meses)
   - Executar queries analíticas
   - Preparar datasets para ML
   - Gerar visualizações

4. **Validação Época 2** (10 meses)
   - Testar modelos em tempo real
   - Validação prospetiva

---

**Está pronto para começar! 🚀**

**Próximo ficheiro**: `docker-compose.yml` ou `sql/01_criar_schema.sql`
