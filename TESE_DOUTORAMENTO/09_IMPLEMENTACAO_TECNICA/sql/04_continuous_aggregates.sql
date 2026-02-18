-- ============================================================================
-- SCRIPT 4: CONTINUOUS AGGREGATES (TimescaleDB)
-- Descrição: Agregações contínuas para acelerar análises e dashboards
-- ============================================================================

\echo '📈 Criando continuous aggregates...'

-- ============================================================================
-- 1) GPS - Agregado diário por atleta
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS ca_gps_diario_atleta
WITH (timescaledb.continuous)
AS
SELECT
    time_bucket(INTERVAL '1 day', time) AS dia,
    atleta_id,
    COUNT(*) AS n_registos,
    COUNT(DISTINCT sessao_id) AS n_sessoes,

    SUM(COALESCE(distancia_total, 0)) AS distancia_total_sum,
    MAX(velocidade_max) AS velocidade_max_max,
    AVG(velocidade_media) AS velocidade_media_avg,

    SUM(COALESCE(sprints, 0)) AS sprints_sum,
    SUM(COALESCE(aceleracoes, 0)) AS aceleracoes_sum,
    SUM(COALESCE(desaceleracoes, 0)) AS desaceleracoes_sum,

    SUM(COALESCE(player_load, 0)) AS player_load_sum,
    AVG(player_load_min) AS player_load_min_avg,

    SUM(COALESCE(hs_dist, 0)) AS hs_dist_sum,
    SUM(COALESCE(dist_19_8_kmh, 0)) AS dist_19_8_kmh_sum,
    SUM(COALESCE(dist_25_2_kmh, 0)) AS dist_25_2_kmh_sum,

    AVG(fc_media) AS fc_media_avg,
    MAX(fc_max) AS fc_max_max,
    AVG(percent_fc_max) AS percent_fc_max_avg
FROM dados_gps
GROUP BY 1, 2
WITH NO DATA;

CREATE INDEX IF NOT EXISTS idx_ca_gps_diario_atleta_dia_atleta
ON ca_gps_diario_atleta (dia DESC, atleta_id);

-- ============================================================================
-- 2) GPS - Agregado semanal por atleta (útil para ACWR/monitorização semanal)
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS ca_gps_semanal_atleta
WITH (timescaledb.continuous)
AS
SELECT
    time_bucket(INTERVAL '7 days', time) AS semana,
    atleta_id,
    COUNT(DISTINCT sessao_id) AS n_sessoes,
    SUM(COALESCE(player_load, 0)) AS player_load_sum,
    SUM(COALESCE(distancia_total, 0)) AS distancia_total_sum,
    SUM(COALESCE(hs_dist, 0)) AS hs_dist_sum,
    SUM(COALESCE(sprints, 0)) AS sprints_sum
FROM dados_gps
GROUP BY 1, 2
WITH NO DATA;

CREATE INDEX IF NOT EXISTS idx_ca_gps_semanal_atleta_semana_atleta
ON ca_gps_semanal_atleta (semana DESC, atleta_id);

-- ============================================================================
-- 3) PSE/Wellness - Agregado diário por atleta
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS ca_pse_diario_atleta
WITH (timescaledb.continuous)
AS
SELECT
    time_bucket(INTERVAL '1 day', time) AS dia,
    atleta_id,
    COUNT(*) AS n_registos,
    COUNT(DISTINCT sessao_id) AS n_sessoes,

    AVG(pse) AS pse_avg,
    MAX(pse) AS pse_max,
    SUM(COALESCE(carga_total, 0)) AS carga_total_sum,

    AVG(qualidade_sono) AS qualidade_sono_avg,
    AVG(fadiga) AS fadiga_avg,
    AVG(dor_muscular) AS dor_muscular_avg,
    AVG(humor) AS humor_avg,
    AVG(stress) AS stress_avg,
    AVG(tqr) AS tqr_avg
FROM dados_pse
GROUP BY 1, 2
WITH NO DATA;

CREATE INDEX IF NOT EXISTS idx_ca_pse_diario_atleta_dia_atleta
ON ca_pse_diario_atleta (dia DESC, atleta_id);

-- ============================================================================
-- 4) Contexto competitivo - Agregado por sessão e minuto (para jogos)
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS ca_contexto_sessao_minuto
WITH (timescaledb.continuous)
AS
SELECT
    sessao_id,
    time_bucket(INTERVAL '1 minute', time) AS minuto_ts,

    MAX(minuto_jogo) AS minuto_jogo_max,
    MAX(golos_favor) AS golos_favor_max,
    MAX(golos_contra) AS golos_contra_max,
    MAX(diferenca_golos) AS diferenca_golos_max,
    MAX(estado_marcador) AS estado_marcador_max,

    MAX(adversario) AS adversario_max,
    MAX(nivel_adversario) AS nivel_adversario_max,
    MAX(classificacao_adversario) AS classificacao_adversario_max,
    MAX(local) AS local_max,
    MAX(importancia) AS importancia_max,
    MAX(sistema_tatico) AS sistema_tatico_max,
    AVG(posse_bola_percent) AS posse_bola_percent_avg
FROM contexto_competitivo
GROUP BY 1, 2
WITH NO DATA;

CREATE INDEX IF NOT EXISTS idx_ca_contexto_sessao_minuto
ON ca_contexto_sessao_minuto (sessao_id, minuto_ts DESC);

-- ============================================================================
-- Policies de refresh (idempotente)
-- Nota: se a versão do TimescaleDB não suportar estas funções, comenta este bloco.
-- ============================================================================

DO $$
BEGIN
    PERFORM add_continuous_aggregate_policy(
        'ca_gps_diario_atleta',
        start_offset => INTERVAL '60 days',
        end_offset   => INTERVAL '1 hour',
        schedule_interval => INTERVAL '1 hour'
    );
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_continuous_aggregate_policy(
        'ca_gps_semanal_atleta',
        start_offset => INTERVAL '180 days',
        end_offset   => INTERVAL '1 hour',
        schedule_interval => INTERVAL '6 hours'
    );
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_continuous_aggregate_policy(
        'ca_pse_diario_atleta',
        start_offset => INTERVAL '60 days',
        end_offset   => INTERVAL '1 hour',
        schedule_interval => INTERVAL '1 hour'
    );
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    PERFORM add_continuous_aggregate_policy(
        'ca_contexto_sessao_minuto',
        start_offset => INTERVAL '30 days',
        end_offset   => INTERVAL '10 minutes',
        schedule_interval => INTERVAL '10 minutes'
    );
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- Inicializar materialização (opcional)
-- CALL refresh_continuous_aggregate('ca_gps_diario_atleta', NULL, NULL);

\echo '✅ Continuous aggregates criadas com sucesso!'
\echo '📌 Próximo passo: Executar 05_funcoes_auxiliares.sql'
