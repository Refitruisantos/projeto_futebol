# ============================================================================
# SCRIPT DE SETUP AUTOMATICO - Windows PowerShell
# Configuracao completa do sistema PostgreSQL + TimescaleDB
# ============================================================================

Write-Host "Iniciando setup automatico da base de dados..." -ForegroundColor Cyan
Write-Host ""

# Variaveis
$DB_NAME = "futebol_tese"
$DB_USER = "postgres"
$DB_PORT = "5433"
$SQL_DIR = ".\sql"

# ============================================================================
# VERIFICAR PRE-REQUISITOS
# ============================================================================

Write-Host "Verificando pre-requisitos..." -ForegroundColor Yellow

# Verificar PostgreSQL
try {
    $pgVersion = psql --version
    Write-Host "[OK] PostgreSQL instalado: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] PostgreSQL nao encontrado!" -ForegroundColor Red
    Write-Host "   Instalar: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

# Verificar Python
try {
    $pyVersion = python --version
    Write-Host "[OK] Python instalado: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python nao encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# CRIAR BASE DE DADOS
# ============================================================================

Write-Host "Criando base de dados '$DB_NAME'..." -ForegroundColor Yellow

# Verificar se DB ja existe
$dbExists = psql -U $DB_USER -p $DB_PORT -lqt | Select-String -Pattern $DB_NAME

if ($dbExists) {
    Write-Host "[AVISO] Base de dados '$DB_NAME' ja existe!" -ForegroundColor Yellow
    $resposta = Read-Host "   Deseja recriar? (s/N)"
    
    if ($resposta -eq "s" -or $resposta -eq "S") {
        Write-Host "   Eliminando base de dados existente..." -ForegroundColor Yellow
        psql -U $DB_USER -p $DB_PORT -c "DROP DATABASE IF EXISTS $DB_NAME;"
        
        Write-Host "   Criando nova base de dados..." -ForegroundColor Yellow
        psql -U $DB_USER -p $DB_PORT -c "CREATE DATABASE $DB_NAME;"
        Write-Host "[OK] Base de dados recriada" -ForegroundColor Green
    } else {
        Write-Host "   Mantendo base de dados existente" -ForegroundColor Yellow
    }
} else {
    psql -U $DB_USER -p $DB_PORT -c "CREATE DATABASE $DB_NAME;"
    Write-Host "[OK] Base de dados criada" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# EXECUTAR SCRIPTS SQL
# ============================================================================

Write-Host "Executando scripts SQL..." -ForegroundColor Yellow

$scripts = @(
    "01_criar_schema.sql",
    "02_criar_hypertables.sql",
    "03_indices_otimizacao.sql",
    "04_continuous_aggregates.sql",
    "05_funcoes_auxiliares.sql",
    "06_politicas_compressao.sql"
)

foreach ($script in $scripts) {
    $scriptPath = Join-Path $SQL_DIR $script
    
    if (Test-Path $scriptPath) {
        Write-Host "   Executando $script..." -ForegroundColor Cyan
        psql -U $DB_USER -p $DB_PORT -d $DB_NAME -f $scriptPath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   [OK] $script executado com sucesso" -ForegroundColor Green
        } else {
            Write-Host "   [ERRO] Erro ao executar $script" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "   [AVISO] $script nao encontrado - pulando" -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================================================
# INSTALAR DEPENDENCIAS PYTHON
# ============================================================================

Write-Host "Instalando dependencias Python..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] Erro ao instalar dependencias" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[AVISO] requirements.txt nao encontrado" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# CRIAR FICHEIRO .ENV
# ============================================================================

Write-Host "Configurando variaveis de ambiente..." -ForegroundColor Yellow

$envFile = ".env"

if (Test-Path $envFile) {
    Write-Host "[AVISO] Ficheiro .env ja existe" -ForegroundColor Yellow
} else {
    $password = Read-Host "   Digite a password do PostgreSQL" -AsSecureString
    $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
    
$envContent = @"
# Configuracao da Base de Dados
DB_HOST=localhost
DB_PORT=5433
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$passwordPlain
"@
    
    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "[OK] Ficheiro .env criado" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# TESTAR INSTALACAO
# ============================================================================

Write-Host "Testando instalacao..." -ForegroundColor Yellow

if (Test-Path "python\01_conexao_db.py") {
    python python\01_conexao_db.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Teste de conexao bem-sucedido!" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] Teste de conexao falhou" -ForegroundColor Red
    }
} else {
    Write-Host "[AVISO] Script de teste nao encontrado" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# RESUMO FINAL
# ============================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "[OK] SETUP COMPLETO!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Base de Dados:" -ForegroundColor Yellow
Write-Host "   Nome: $DB_NAME"
Write-Host "   Host: localhost:5433"
Write-Host "   User: $DB_USER"
Write-Host ""
Write-Host "Proximos Passos:" -ForegroundColor Yellow
Write-Host "   1. Verificar se todas as tabelas foram criadas:"
Write-Host "      psql -U $DB_USER -p $DB_PORT -d $DB_NAME -c '\dt'"
Write-Host ""
Write-Host "   2. Verificar hypertables:"
Write-Host "      psql -U $DB_USER -p $DB_PORT -d $DB_NAME -c 'SELECT * FROM timescaledb_information.hypertables;'"
Write-Host ""
Write-Host "   3. Comecar a inserir dados:"
Write-Host "      python python\02_inserir_dados_gps.py"
Write-Host ""
Write-Host "Documentacao: 00_GUIA_IMPLEMENTACAO_PRATICA.md" -ForegroundColor Cyan
Write-Host ""

# Pausa final
Read-Host "Pressione Enter para sair"
