-- ==========================================================================
-- SCRIPT 6: POLÍTICAS DE COMPRESSÃO (TimescaleDB)
-- Descrição: Ativar compressão e políticas automáticas para hypertables
-- ==========================================================================

\echo '🗜️  Configurando compressão TimescaleDB...'

-- ============================================================================
-- 1) HYPERTABLE: dados_gps
-- Segmentação por atleta para consultas por atleta; ordenação por time
-- ============================================================================

DO $$
BEGIN
    EXECUTE $$ALTER TABLE dados_gps SET (
        timescaledb.compress,
        timescaledb.compress_segmentby = 'atleta_id',
        timescaledb.compress_orderby = 'time DESC'
    )$$;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_compression_policy('dados_gps', INTERVAL '30 days');
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- ============================================================================
-- 2) HYPERTABLE: dados_pse
-- Segmentação por atleta; ordenação por time
-- ============================================================================

DO $$
BEGIN
    EXECUTE $$ALTER TABLE dados_pse SET (
        timescaledb.compress,
        timescaledb.compress_segmentby = 'atleta_id',
        timescaledb.compress_orderby = 'time DESC'
    )$$;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_compression_policy('dados_pse', INTERVAL '30 days');
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- ============================================================================
-- 3) HYPERTABLE: contexto_competitivo
-- Segmentação por sessão (jogo); ordenação por time
-- ============================================================================

DO $$
BEGIN
    EXECUTE $$ALTER TABLE contexto_competitivo SET (
        timescaledb.compress,
        timescaledb.compress_segmentby = 'sessao_id',
        timescaledb.compress_orderby = 'time DESC'
    )$$;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_compression_policy('contexto_competitivo', INTERVAL '60 days');
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- ============================================================================
-- 4) Continuous aggregates (opcional)
-- Nota: Em algumas versões do TimescaleDB a compressão de CAGGs pode exigir
-- configurações específicas. Mantemos idempotente e tolerante a erros.
-- ============================================================================

DO $$
BEGIN
    EXECUTE $$ALTER MATERIALIZED VIEW ca_gps_diario_atleta SET (timescaledb.compress = true)$$;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_compression_policy('ca_gps_diario_atleta', INTERVAL '90 days');
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    EXECUTE $$ALTER MATERIALIZED VIEW ca_gps_semanal_atleta SET (timescaledb.compress = true)$$;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_compression_policy('ca_gps_semanal_atleta', INTERVAL '180 days');
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    EXECUTE $$ALTER MATERIALIZED VIEW ca_pse_diario_atleta SET (timescaledb.compress = true)$$;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_compression_policy('ca_pse_diario_atleta', INTERVAL '90 days');
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    EXECUTE $$ALTER MATERIALIZED VIEW ca_contexto_sessao_minuto SET (timescaledb.compress = true)$$;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_compression_policy('ca_contexto_sessao_minuto', INTERVAL '30 days');
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- ============================================================================
-- 5) Verificar políticas ativas (informativo)
-- ============================================================================

\echo '📋 Políticas de compressão (se suportado pela versão):'
SELECT *
FROM timescaledb_information.jobs
WHERE proc_name IN ('policy_compression', 'policy_refresh_continuous_aggregate')
ORDER BY job_id;

\echo '✅ Compressão configurada (se suportada)!'
