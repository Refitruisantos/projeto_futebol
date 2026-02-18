-- ============================================================================
-- SCRIPT 2: CONVERTER TABELAS EM HYPERTABLES
-- Descrição: Converter tabelas temporais para hypertables TimescaleDB
-- ============================================================================

\echo '🔄 Convertendo tabelas em hypertables TimescaleDB...'

-- ============================================================================
-- 1. DADOS GPS
-- ============================================================================
SELECT create_hypertable(
    'dados_gps',
    'time',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

\echo '✅ Hypertable dados_gps criada (chunks de 1 semana)'

-- ============================================================================
-- 2. DADOS PSE
-- ============================================================================
SELECT create_hypertable(
    'dados_pse',
    'time',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

\echo '✅ Hypertable dados_pse criada (chunks de 1 semana)'

-- ============================================================================
-- 3. CONTEXTO COMPETITIVO
-- ============================================================================
SELECT create_hypertable(
    'contexto_competitivo',
    'time',
    chunk_time_interval => INTERVAL '1 week',
    if_not_exists => TRUE
);

\echo '✅ Hypertable contexto_competitivo criada (chunks de 1 semana)'

-- ============================================================================
-- VERIFICAR HYPERTABLES CRIADAS
-- ============================================================================
\echo '📊 Hypertables criadas:'

SELECT 
    hypertable_schema,
    hypertable_name,
    num_dimensions,
    num_chunks,
    compression_enabled
FROM timescaledb_information.hypertables
ORDER BY hypertable_name;

-- ============================================================================
-- FIM DO SCRIPT 2
-- ============================================================================

\echo '✅ Todas as hypertables criadas com sucesso!'
\echo '📌 Próximo passo: Executar 03_indices_otimizacao.sql'
