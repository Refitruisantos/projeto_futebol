# ============================================================================
# SCRIPT DE SETUP AUTOMÁTICO - Windows PowerShell
# Configuração completa do sistema PostgreSQL + TimescaleDB
# ============================================================================

Write-Host "🚀 Iniciando setup automático da base de dados..." -ForegroundColor Cyan
Write-Host ""

# Variáveis
$DB_NAME = "futebol_tese"
$DB_USER = "postgres"
$SQL_DIR = ".\sql"

# ============================================================================
# VERIFICAR PRÉ-REQUISITOS
# ============================================================================

Write-Host "🔍 Verificando pré-requisitos..." -ForegroundColor Yellow

# Verificar PostgreSQL
try {
    $pgVersion = psql --version
    Write-Host "✅ PostgreSQL instalado: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PostgreSQL não encontrado!" -ForegroundColor Red
    Write-Host "   Instalar: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

# Verificar Python
try {
    $pyVersion = python --version
    Write-Host "✅ Python instalado: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# CRIAR BASE DE DADOS
# ============================================================================

Write-Host "📦 Criando base de dados '$DB_NAME'..." -ForegroundColor Yellow

# Verificar se DB já existe
$dbExists = psql -U $DB_USER -lqt | Select-String -Pattern $DB_NAME

if ($dbExists) {
    Write-Host "⚠️  Base de dados '$DB_NAME' já existe!" -ForegroundColor Yellow
    $resposta = Read-Host "   Deseja recriar? (s/N)"
    
    if ($resposta -eq "s" -or $resposta -eq "S") {
        Write-Host "   Eliminando base de dados existente..." -ForegroundColor Yellow
        psql -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"
        
        Write-Host "   Criando nova base de dados..." -ForegroundColor Yellow
        psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"
        Write-Host "✅ Base de dados recriada" -ForegroundColor Green
    } else {
        Write-Host "   Mantendo base de dados existente" -ForegroundColor Yellow
    }
} else {
    psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;"
    Write-Host "✅ Base de dados criada" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# EXECUTAR SCRIPTS SQL
# ============================================================================

Write-Host "⚙️  Executando scripts SQL..." -ForegroundColor Yellow

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
        psql -U $DB_USER -d $DB_NAME -f $scriptPath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $script executado com sucesso" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Erro ao executar $script" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "   ⚠️  $script não encontrado - pulando" -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================================================
# INSTALAR DEPENDÊNCIAS PYTHON
# ============================================================================

Write-Host "📚 Instalando dependências Python..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependências instaladas" -ForegroundColor Green
    } else {
        Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  requirements.txt não encontrado" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# CRIAR FICHEIRO .ENV
# ============================================================================

Write-Host "🔐 Configurando variáveis de ambiente..." -ForegroundColor Yellow

$envFile = ".env"

if (Test-Path $envFile) {
    Write-Host "⚠️  Ficheiro .env já existe" -ForegroundColor Yellow
} else {
    $password = Read-Host "   Digite a password do PostgreSQL" -AsSecureString
    $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
    
$envContent = @"
# Configuração da Base de Dados
DB_HOST=localhost
DB_PORT=5433
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$passwordPlain
"@
    
    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "✅ Ficheiro .env criado" -ForegroundColor Green
}

Write-Host ""

# ============================================================================
# TESTAR INSTALAÇÃO
# ============================================================================

Write-Host "🧪 Testando instalação..." -ForegroundColor Yellow

if (Test-Path "python\01_conexao_db.py") {
    python python\01_conexao_db.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Teste de conexão bem-sucedido!" -ForegroundColor Green
    } else {
        Write-Host "❌ Teste de conexão falhou" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️  Script de teste não encontrado" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# RESUMO FINAL
# ============================================================================

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Base de Dados:" -ForegroundColor Yellow
Write-Host "   Nome: $DB_NAME"
Write-Host "   Host: localhost:5433"
Write-Host "   User: $DB_USER"
Write-Host ""
Write-Host "📝 Próximos Passos:" -ForegroundColor Yellow
Write-Host "   1. Verificar se todas as tabelas foram criadas:"
Write-Host "      psql -U $DB_USER -d $DB_NAME -c '\dt'"
Write-Host ""
Write-Host "   2. Verificar hypertables:"
Write-Host "      psql -U $DB_USER -d $DB_NAME -c 'SELECT * FROM timescaledb_information.hypertables;'"
Write-Host ""
Write-Host "   3. Começar a inserir dados:"
Write-Host "      python python\02_inserir_dados_gps.py"
Write-Host ""
Write-Host "🎓 Documentação: 00_GUIA_IMPLEMENTACAO_PRATICA.md" -ForegroundColor Cyan
Write-Host ""

# Pausa final
Read-Host "Pressionar Enter para sair"
