-- ============================================================================
-- SCRIPT 1: CRIAR SCHEMA COMPLETO
-- Base de Dados: futebol_tese
-- Descrição: Tabelas relacionais e estrutura base para hypertables
-- ============================================================================

-- Ativar extensão TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Outras extensões úteis
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;  -- Estatísticas de queries
EXCEPTION WHEN others THEN
    NULL;
END $$;
CREATE EXTENSION IF NOT EXISTS btree_gist;          -- Índices avançados

-- ============================================================================
-- TABELA: ATLETAS (Relacional)
-- ============================================================================
CREATE TABLE IF NOT EXISTS atletas (
    id SERIAL PRIMARY KEY,
    jogador_id VARCHAR(100) UNIQUE NOT NULL,
    nome_completo VARCHAR(200) NOT NULL,
    data_nascimento DATE,
    
    -- Características
    posicao VARCHAR(50) CHECK (posicao IN ('GR', 'DC', 'DL', 'MC', 'EX', 'AV')),
    numero_camisola INTEGER CHECK (numero_camisola BETWEEN 1 AND 99),
    pe_dominante VARCHAR(20) CHECK (pe_dominante IN ('Direito', 'Esquerdo', 'Ambos')),
    
    -- Antropometria
    altura_cm INTEGER CHECK (altura_cm BETWEEN 150 AND 210),
    massa_kg DECIMAL(5,2) CHECK (massa_kg BETWEEN 45 AND 120),
    
    -- Status
    ativo BOOLEAN DEFAULT TRUE,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_atletas_jogador_id ON atletas(jogador_id);
CREATE INDEX idx_atletas_posicao ON atletas(posicao);
CREATE INDEX idx_atletas_ativo ON atletas(ativo);

COMMENT ON TABLE atletas IS 'Informação base dos atletas';
COMMENT ON COLUMN atletas.posicao IS 'GR=Guarda-Redes, DC=Defesa Central, DL=Defesa Lateral, MC=Médio Centro, EX=Extremo, AV=Avançado';

-- ============================================================================
-- TABELA: SESSOES (Relacional)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessoes (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    hora_inicio TIME,
    
    -- Tipo de sessão
    tipo VARCHAR(50) CHECK (tipo IN ('treino', 'jogo', 'recuperacao', 'teste_fisico')),
    duracao_min INTEGER CHECK (duracao_min > 0),
    
    -- Contexto de jogo (se aplicável)
    adversario VARCHAR(100),
    local VARCHAR(50) CHECK (local IN ('casa', 'fora', 'neutro')),
    competicao VARCHAR(100),
    jornada INTEGER,
    resultado VARCHAR(20),  -- Ex: '2-1', '0-0'
    
    -- Condições
    condicoes_meteorologicas VARCHAR(100),
    temperatura_celsius INTEGER,
    
    -- Metadados
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessoes_data ON sessoes(data DESC);
CREATE INDEX idx_sessoes_tipo ON sessoes(tipo);
CREATE INDEX idx_sessoes_adversario ON sessoes(adversario);

COMMENT ON TABLE sessoes IS 'Sessões de treino, jogos e testes';

-- ============================================================================
-- TABELA: DADOS GPS (Será convertida em Hypertable)
-- ============================================================================
CREATE TABLE IF NOT EXISTS dados_gps (
    time TIMESTAMP NOT NULL,
    atleta_id INTEGER NOT NULL REFERENCES atletas(id) ON DELETE CASCADE,
    sessao_id INTEGER REFERENCES sessoes(id) ON DELETE CASCADE,
    
    -- Métricas GPS básicas
    distancia_total FLOAT CHECK (distancia_total >= 0),
    velocidade_max FLOAT CHECK (velocidade_max >= 0 AND velocidade_max <= 45),
    velocidade_media FLOAT CHECK (velocidade_media >= 0),
    
    -- Intensidade
    sprints INTEGER CHECK (sprints >= 0),
    aceleracoes INTEGER CHECK (aceleracoes >= 0),
    desaceleracoes INTEGER CHECK (desaceleracoes >= 0),
    
    -- Carga
    player_load FLOAT CHECK (player_load >= 0),
    player_load_min FLOAT,
    
    -- Métricas avançadas
    rhie FLOAT CHECK (rhie >= 0),  -- Running High Intensity Efforts
    bout_recovery FLOAT CHECK (bout_recovery >= 0),
    
    -- Acelerações/Desacelerações detalhadas
    max_acc_b1_3 FLOAT,
    max_decel_b1_3 FLOAT,
    tot_effs_gen2 INTEGER,
    
    -- Zonas de velocidade
    effs_19_8_kmh INTEGER,  -- Esforços > 19.8 km/h
    dist_19_8_kmh FLOAT,
    effs_25_2_kmh INTEGER,  -- Sprints > 25.2 km/h
    dist_25_2_kmh FLOAT,
    hs_dist FLOAT,  -- High Speed Distance
    
    -- Contexto temporal dentro do jogo/treino
    minuto_jogo INTEGER CHECK (minuto_jogo >= 0 AND minuto_jogo <= 120),
    fase_jogo VARCHAR(20) CHECK (fase_jogo IN ('0-30', '30-75', '75-90+')),
    
    -- Frequência cardíaca (se disponível)
    fc_media INTEGER CHECK (fc_media > 0 AND fc_media < 220),
    fc_max INTEGER CHECK (fc_max > 0 AND fc_max < 220),
    percent_fc_max FLOAT CHECK (percent_fc_max >= 0 AND percent_fc_max <= 100),
    
    -- Metadados
    fonte VARCHAR(50),  -- 'pdf', 'csv', 'api_catapult', 'manual'
    qualidade_sinal VARCHAR(20) CHECK (qualidade_sinal IN ('excelente', 'boa', 'aceitavel', 'baixa')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices (serão recriados após hypertable)
CREATE INDEX idx_dados_gps_time ON dados_gps(time DESC);
CREATE INDEX idx_dados_gps_atleta ON dados_gps(atleta_id);
CREATE INDEX idx_dados_gps_sessao ON dados_gps(sessao_id);

COMMENT ON TABLE dados_gps IS 'Dados GPS de cada sessão (será convertida em hypertable)';

-- ============================================================================
-- TABELA: DADOS PSE (Será convertida em Hypertable)
-- ============================================================================
CREATE TABLE IF NOT EXISTS dados_pse (
    time TIMESTAMP NOT NULL,
    atleta_id INTEGER NOT NULL REFERENCES atletas(id) ON DELETE CASCADE,
    sessao_id INTEGER REFERENCES sessoes(id) ON DELETE CASCADE,
    
    -- PSE (Perceção Subjetiva do Esforço)
    pse FLOAT NOT NULL CHECK (pse BETWEEN 1 AND 10),
    duracao_min INTEGER CHECK (duracao_min > 0),
    carga_total FLOAT,  -- PSE × duração
    
    -- Wellness (estado pré-treino)
    qualidade_sono INTEGER CHECK (qualidade_sono BETWEEN 1 AND 5),
    fadiga INTEGER CHECK (fadiga BETWEEN 1 AND 5),
    dor_muscular INTEGER CHECK (dor_muscular BETWEEN 1 AND 5),
    humor INTEGER CHECK (humor BETWEEN 1 AND 5),
    stress INTEGER CHECK (stress BETWEEN 1 AND 5),
    
    -- TQR (Total Quality Recovery) - se usado
    tqr INTEGER CHECK (tqr BETWEEN 6 AND 20),
    
    -- Observações
    comentarios TEXT,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_dados_pse_time ON dados_pse(time DESC);
CREATE INDEX idx_dados_pse_atleta ON dados_pse(atleta_id);

COMMENT ON TABLE dados_pse IS 'Perceção Subjetiva do Esforço e Wellness';

-- ============================================================================
-- TABELA: CONTEXTO COMPETITIVO (Será convertida em Hypertable)
-- ============================================================================
CREATE TABLE IF NOT EXISTS contexto_competitivo (
    time TIMESTAMP NOT NULL,
    sessao_id INTEGER NOT NULL REFERENCES sessoes(id) ON DELETE CASCADE,
    
    -- Momento do jogo
    minuto_jogo INTEGER CHECK (minuto_jogo >= 0),
    fase_jogo VARCHAR(20) CHECK (fase_jogo IN ('0-30', '30-75', '75-90+')),
    
    -- Marcador
    golos_favor INTEGER DEFAULT 0,
    golos_contra INTEGER DEFAULT 0,
    diferenca_golos INTEGER,  -- favor - contra
    estado_marcador VARCHAR(50) CHECK (estado_marcador IN (
        'vitoria_folgada', 'vitoria_curta', 'empate', 
        'derrota_curta', 'derrota_folgada'
    )),
    
    -- Adversário
    adversario VARCHAR(100),
    nivel_adversario INTEGER CHECK (nivel_adversario BETWEEN 1 AND 5),
    classificacao_adversario INTEGER,  -- Posição na tabela
    
    -- Contexto
    local VARCHAR(20) CHECK (local IN ('casa', 'fora', 'neutro')),
    importancia INTEGER CHECK (importancia BETWEEN 1 AND 5),
    
    -- Tática (se disponível)
    sistema_tatico VARCHAR(20),  -- Ex: '4-3-3', '4-4-2'
    posse_bola_percent FLOAT CHECK (posse_bola_percent BETWEEN 0 AND 100),
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contexto_time ON contexto_competitivo(time DESC);
CREATE INDEX idx_contexto_sessao ON contexto_competitivo(sessao_id);

COMMENT ON TABLE contexto_competitivo IS 'Contexto competitivo durante jogos';

-- ============================================================================
-- TABELA: TESTES FÍSICOS (Relacional - eventos pontuais)
-- ============================================================================
CREATE TABLE IF NOT EXISTS testes_fisicos (
    id SERIAL PRIMARY KEY,
    atleta_id INTEGER NOT NULL REFERENCES atletas(id) ON DELETE CASCADE,
    data_teste DATE NOT NULL,
    momento VARCHAR(50) CHECK (momento IN ('pre_epoca', 'meio_epoca', 'final_epoca', 'ad_hoc')),
    
    -- Testes aeróbios
    mas_kmh FLOAT CHECK (mas_kmh > 0),  -- Máxima Aeróbia
    vam_kmh FLOAT,  -- Velocidade Aeróbia Máxima
    vo2max_est FLOAT,  -- VO2max estimado
    tempo_2000m_s FLOAT,
    
    -- Velocidade
    mss_kmh FLOAT CHECK (mss_kmh > 0),  -- Velocidade Máxima
    asr_kmh FLOAT,  -- Capacidade Repetir Sprints
    velocidade_10m_s FLOAT,
    velocidade_35m_s FLOAT,
    velocidade_35m_kmh FLOAT,
    
    -- Força/Potência
    cmj_cm FLOAT CHECK (cmj_cm >= 0),  -- Counter Movement Jump
    sj_cm FLOAT CHECK (sj_cm >= 0),  -- Squat Jump
    rsi FLOAT,  -- Reactive Strength Index
    
    -- Agilidade
    t_test_s FLOAT,
    illinois_s FLOAT,
    
    -- Outros
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_testes_atleta ON testes_fisicos(atleta_id, data_teste DESC);
CREATE INDEX idx_testes_data ON testes_fisicos(data_teste DESC);

COMMENT ON TABLE testes_fisicos IS 'Testes físicos pontuais (3-4 por época)';

-- ============================================================================
-- TABELA: LESÕES (Relacional)
-- ============================================================================
CREATE TABLE IF NOT EXISTS lesoes (
    id SERIAL PRIMARY KEY,
    atleta_id INTEGER NOT NULL REFERENCES atletas(id) ON DELETE CASCADE,
    data_lesao DATE NOT NULL,
    data_retorno DATE,
    
    -- Tipo de lesão
    tipo_lesao VARCHAR(100) NOT NULL,
    localizacao VARCHAR(100),
    gravidade VARCHAR(50) CHECK (gravidade IN ('ligeira', 'moderada', 'grave', 'muito_grave')),
    
    -- Duração
    dias_ausencia INTEGER,
    sessoes_perdidas INTEGER,
    jogos_perdidos INTEGER,
    
    -- Causa
    mecanismo VARCHAR(100) CHECK (mecanismo IN ('contacto', 'sem_contacto', 'sobrecarga', 'outro')),
    contexto VARCHAR(100),  -- 'treino', 'jogo', 'outro'
    
    -- Observações
    diagnostico_medico TEXT,
    tratamento TEXT,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lesoes_atleta ON lesoes(atleta_id, data_lesao DESC);
CREATE INDEX idx_lesoes_tipo ON lesoes(tipo_lesao);
CREATE INDEX idx_lesoes_gravidade ON lesoes(gravidade);

COMMENT ON TABLE lesoes IS 'Registo de lesões dos atletas';

-- ============================================================================
-- TABELA: ALERTAS (Será usada pelo sistema ML)
-- ============================================================================
CREATE TABLE IF NOT EXISTS alertas (
    id SERIAL PRIMARY KEY,
    atleta_id INTEGER NOT NULL REFERENCES atletas(id) ON DELETE CASCADE,
    data_geracao TIMESTAMP NOT NULL DEFAULT NOW(),
    data_referencia TIMESTAMP,
    
    -- Tipo e severidade
    tipo_alerta VARCHAR(100) NOT NULL CHECK (tipo_alerta IN (
        'risco_lesao_alto', 'risco_lesao_moderado', 
        'fadiga_acumulada', 'overtraining', 
        'queda_performance', 'alerta_wellness'
    )),
    severidade VARCHAR(20) CHECK (severidade IN ('CRÍTICO', 'ALTO', 'MÉDIO', 'BAIXO')),
    origem VARCHAR(50) CHECK (origem IN ('ML', 'REGRA', 'LSTM', 'TEMPO_REAL', 'MANUAL')),
    
    -- Dados do alerta
    condicoes JSONB,  -- Condições que geraram alerta
    metricas JSONB,  -- Métricas relevantes
    contexto JSONB,  -- Contexto competitivo
    
    -- Machine Learning
    modelo_usado VARCHAR(50),
    probabilidade FLOAT CHECK (probabilidade BETWEEN 0 AND 1),
    shap_valores JSONB,  -- Explicabilidade
    
    -- Ação
    recomendacao TEXT,
    acao_tomada TEXT,
    visualizado BOOLEAN DEFAULT FALSE,
    resolvido BOOLEAN DEFAULT FALSE,
    data_resolucao TIMESTAMP,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alertas_atleta ON alertas(atleta_id, data_geracao DESC);
CREATE INDEX idx_alertas_tipo ON alertas(tipo_alerta);
CREATE INDEX idx_alertas_nao_resolvidos ON alertas(atleta_id) WHERE resolvido = FALSE;

COMMENT ON TABLE alertas IS 'Alertas gerados pelo sistema (ML e regras)';

-- ============================================================================
-- TRIGGERS PARA UPDATED_AT
-- ============================================================================
CREATE OR REPLACE FUNCTION atualizar_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_atletas_updated_at
    BEFORE UPDATE ON atletas
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

-- ============================================================================
-- FIM DO SCRIPT 1
-- ============================================================================

-- Verificar tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Sucesso!
\echo '✅ Schema base criado com sucesso!'
\echo '📌 Próximo passo: Executar 02_criar_hypertables.sql'
