# Instruções de Instalação PostgreSQL + TimescaleDB
## Windows 11

---

## 📦 Instalação PostgreSQL

### Método 1: Instalador Oficial (Recomendado)

1. **Download**: https://www.postgresql.org/download/windows/
   - Versão recomendada: **PostgreSQL 15** ou **16**
   - Ficheiro: `postgresql-15-windows-x64.exe` (~250 MB)

2. **Executar instalador**:
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4 (interface gráfica)
   - ✅ Command Line Tools
   - ✅ Stack Builder (para TimescaleDB)

3. **Configurações importantes**:
   ```
   Porta: 5432 (padrão)
   Password: [ESCOLHER UMA SENHA FORTE]
   Locale: Portuguese, Portugal
   ```

4. **Anotar a password!** ⚠️ Vai precisar depois

5. **Verificar instalação**:
   ```powershell
   # Abrir novo terminal PowerShell
   psql --version
   # Deve mostrar: psql (PostgreSQL) 15.x
   ```

---

### Método 2: WinGet (Windows 11)

```powershell
# Executar como Administrador
winget install PostgreSQL.PostgreSQL.15

# Aguardar instalação...

# Verificar
psql --version
```

---

## 🔧 Instalação TimescaleDB

### Opção A: Via Stack Builder (Durante instalação PostgreSQL)

1. No final da instalação do PostgreSQL, o **Stack Builder** abre automaticamente
2. Selecionar: **Spatial Extensions** → **TimescaleDB**
3. Seguir wizard de instalação

---

### Opção B: Download Manual (Se já instalou PostgreSQL)

1. **Download**: https://docs.timescale.com/install/latest/self-hosted/installation-windows/

2. **Selecionar versão** compatível com seu PostgreSQL:
   - PostgreSQL 15 → TimescaleDB 2.13+
   - PostgreSQL 16 → TimescaleDB 2.14+

3. **Executar instalador** `timescaledb-postgresql-15.exe`

4. **Verificar instalação**:
   ```powershell
   # Conectar ao PostgreSQL
   psql -U postgres
   
   # Criar extensão (numa base de dados de teste)
   CREATE DATABASE teste;
   \c teste
   CREATE EXTENSION timescaledb;
   
   # Se funcionar, está OK!
   \dx
   # Deve mostrar: timescaledb | 2.13.x
   
   # Sair
   \q
   ```

---

## ✅ Checklist Pós-Instalação

- [ ] PostgreSQL instalado
- [ ] `psql --version` funciona no terminal
- [ ] TimescaleDB instalado
- [ ] Password do postgres anotada
- [ ] Porta 5432 livre (não usada por outro serviço)

---

## 🚀 Depois de Instalar

### Executar Setup Automático

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

# Executar script
.\scripts\setup_completo.ps1
```

O script vai:
1. ✅ Criar base de dados `futebol_tese`
2. ✅ Executar todos os scripts SQL
3. ✅ Criar tabelas e hypertables
4. ✅ Instalar dependências Python
5. ✅ Testar conexão

---

## 🆘 Problemas Comuns

### Erro: "psql: command not found" (Após instalação)

**Causa**: PostgreSQL não adicionado ao PATH

**Solução**:
1. Abrir **Variáveis de Ambiente**:
   - `Win + R` → `sysdm.cpl` → Aba "Avançado" → "Variáveis de Ambiente"

2. Editar variável **Path** (do sistema):
   - Adicionar: `C:\Program Files\PostgreSQL\15\bin`
   - Adicionar: `C:\Program Files\PostgreSQL\15\lib`

3. **Reiniciar terminal** e testar:
   ```powershell
   psql --version
   ```

---

### Erro: "could not connect to server"

**Causa**: Serviço PostgreSQL não iniciado

**Solução**:
```powershell
# Ver status do serviço
Get-Service postgresql*

# Iniciar serviço
Start-Service postgresql-x64-15

# Configurar para iniciar automaticamente
Set-Service postgresql-x64-15 -StartupType Automatic
```

---

### Erro: "password authentication failed"

**Causa**: Password incorreta

**Solução**: Resetar password
```powershell
# Editar pg_hba.conf (localização típica)
# C:\Program Files\PostgreSQL\15\data\pg_hba.conf

# Mudar linha:
# host    all    all    127.0.0.1/32    scram-sha-256
# para:
# host    all    all    127.0.0.1/32    trust

# Reiniciar serviço
Restart-Service postgresql-x64-15

# Conectar sem password
psql -U postgres

# Alterar password
ALTER USER postgres PASSWORD 'nova_senha_forte';

# Reverter pg_hba.conf para "scram-sha-256"
# Reiniciar serviço novamente
```

---

## 📚 Recursos

- **Documentação PostgreSQL**: https://www.postgresql.org/docs/
- **Documentação TimescaleDB**: https://docs.timescale.com/
- **Tutorial Windows**: https://www.postgresqltutorial.com/postgresql-getting-started/install-postgresql/

---

## 🐳 Alternativa: Docker (Mais Simples)

Se tiver dificuldades com a instalação, considere usar **Docker** (Opção 2):

1. Instalar Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Executar: `docker-compose up -d`
3. Tudo funciona imediatamente! ✨

---

**Tempo estimado de instalação**: 15-30 minutos  
**Dificuldade**: ⭐⭐ (Média)
