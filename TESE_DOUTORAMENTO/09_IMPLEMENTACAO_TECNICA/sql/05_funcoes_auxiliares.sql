-- ============================================================================
-- SCRIPT 5: FUNÇÕES AUXILIARES
-- Descrição: Funções úteis para análise de dados
-- ============================================================================

\echo '🔧 Criando funções auxiliares...'

-- ============================================================================
-- FUNÇÃO 1: Calcular Carga Acumulada (últimos N dias)
-- ============================================================================
CREATE OR REPLACE FUNCTION carga_acumulada_n_dias(
    p_atleta_id INTEGER,
    p_data_referencia TIMESTAMP,
    p_n_dias INTEGER DEFAULT 7
)
RETURNS FLOAT AS $$
DECLARE
    v_carga FLOAT;
BEGIN
    SELECT COALESCE(SUM(player_load), 0)
    INTO v_carga
    FROM dados_gps
    WHERE atleta_id = p_atleta_id
      AND time BETWEEN (p_data_referencia - (p_n_dias || ' days')::INTERVAL) 
                   AND p_data_referencia;
    
    RETURN v_carga;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION carga_acumulada_n_dias IS 
'Calcula soma do player load nos últimos N dias para um atleta';

-- Exemplo de uso:
-- SELECT carga_acumulada_n_dias(1, NOW(), 7);

-- ============================================================================
-- FUNÇÃO 2: Calcular ACWR (Acute:Chronic Workload Ratio)
-- ============================================================================
CREATE OR REPLACE FUNCTION calcular_acwr(
    p_atleta_id INTEGER,
    p_data_referencia TIMESTAMP
)
RETURNS FLOAT AS $$
DECLARE
    v_carga_aguda FLOAT;
    v_carga_cronica FLOAT;
    v_acwr FLOAT;
BEGIN
    -- Carga aguda (últimos 7 dias)
    v_carga_aguda := carga_acumulada_n_dias(p_atleta_id, p_data_referencia, 7);
    
    -- Carga crónica (últimos 28 dias)
    v_carga_cronica := carga_acumulada_n_dias(p_atleta_id, p_data_referencia, 28);
    
    -- ACWR = Carga Aguda / (Carga Crónica / 4)
    -- Nota: Divide por 4 para ter média semanal crónica
    IF v_carga_cronica > 0 THEN
        v_acwr := v_carga_aguda / (v_carga_cronica / 4.0);
    ELSE
        v_acwr := NULL;
    END IF;
    
    RETURN v_acwr;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calcular_acwr IS 
'Calcula ACWR (Acute:Chronic Workload Ratio) - Hulin et al. 2016';

-- Exemplo de uso:
-- SELECT calcular_acwr(1, NOW());

-- ============================================================================
-- FUNÇÃO 3: Classificar ACWR
-- ============================================================================
CREATE OR REPLACE FUNCTION classificar_acwr(p_acwr FLOAT)
RETURNS VARCHAR AS $$
BEGIN
    IF p_acwr IS NULL THEN
        RETURN 'SEM_DADOS';
    ELSIF p_acwr < 0.8 THEN
        RETURN 'SUBCARGA';  -- Risco de destreino
    ELSIF p_acwr >= 0.8 AND p_acwr <= 1.3 THEN
        RETURN 'SWEET_SPOT';  -- Zona ótima
    ELSIF p_acwr > 1.3 AND p_acwr <= 1.5 THEN
        RETURN 'RISCO_MODERADO';
    ELSE
        RETURN 'RISCO_ALTO';  -- > 1.5
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION classificar_acwr IS 
'Classifica ACWR em categorias de risco (Hulin et al. 2016)';

-- Exemplo:
-- SELECT classificar_acwr(1.2);  -- Retorna 'SWEET_SPOT'

-- ============================================================================
-- FUNÇÃO 4: Média Móvel de Player Load
-- ============================================================================
CREATE OR REPLACE FUNCTION media_movel_player_load(
    p_atleta_id INTEGER,
    p_data_referencia TIMESTAMP,
    p_n_dias INTEGER DEFAULT 7
)
RETURNS FLOAT AS $$
DECLARE
    v_media FLOAT;
    v_count INTEGER;
BEGIN
    SELECT AVG(player_load), COUNT(*)
    INTO v_media, v_count
    FROM dados_gps
    WHERE atleta_id = p_atleta_id
      AND time BETWEEN (p_data_referencia - (p_n_dias || ' days')::INTERVAL) 
                   AND p_data_referencia;
    
    -- Retornar NULL se menos de 3 sessões
    IF v_count < 3 THEN
        RETURN NULL;
    END IF;
    
    RETURN v_media;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION media_movel_player_load IS 
'Calcula média móvel do player load (requer mínimo 3 sessões)';

-- ============================================================================
-- FUNÇÃO 5: Calcular Monotonia (Foster 1998)
-- ============================================================================
CREATE OR REPLACE FUNCTION calcular_monotonia(
    p_atleta_id INTEGER,
    p_data_referencia TIMESTAMP,
    p_n_dias INTEGER DEFAULT 7
)
RETURNS FLOAT AS $$
DECLARE
    v_media FLOAT;
    v_desvio FLOAT;
    v_monotonia FLOAT;
BEGIN
    SELECT AVG(player_load), STDDEV_SAMP(player_load)
    INTO v_media, v_desvio
    FROM dados_gps
    WHERE atleta_id = p_atleta_id
      AND time BETWEEN (p_data_referencia - (p_n_dias || ' days')::INTERVAL) 
                   AND p_data_referencia;
    
    -- Monotonia = Média / Desvio Padrão
    IF v_desvio IS NOT NULL AND v_desvio > 0 THEN
        v_monotonia := v_media / v_desvio;
    ELSE
        v_monotonia := NULL;
    END IF;
    
    RETURN v_monotonia;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calcular_monotonia IS 
'Calcula monotonia do treino (Foster 1998) - valores altos indicam falta de variação';

-- ============================================================================
-- FUNÇÃO 6: Calcular Strain (Foster 1998)
-- ============================================================================
CREATE OR REPLACE FUNCTION calcular_strain(
    p_atleta_id INTEGER,
    p_data_referencia TIMESTAMP,
    p_n_dias INTEGER DEFAULT 7
)
RETURNS FLOAT AS $$
DECLARE
    v_carga FLOAT;
    v_monotonia FLOAT;
    v_strain FLOAT;
BEGIN
    v_carga := carga_acumulada_n_dias(p_atleta_id, p_data_referencia, p_n_dias);
    v_monotonia := calcular_monotonia(p_atleta_id, p_data_referencia, p_n_dias);
    
    -- Strain = Carga × Monotonia
    IF v_monotonia IS NOT NULL THEN
        v_strain := v_carga * v_monotonia;
    ELSE
        v_strain := NULL;
    END IF;
    
    RETURN v_strain;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calcular_strain IS 
'Calcula strain (Foster 1998) - combina carga e monotonia';

-- ============================================================================
-- FUNÇÃO 7: Resumo Completo de um Atleta
-- ============================================================================
CREATE OR REPLACE FUNCTION resumo_atleta(
    p_atleta_id INTEGER,
    p_data_referencia TIMESTAMP DEFAULT NOW()
)
RETURNS TABLE(
    metrica VARCHAR,
    valor_7d FLOAT,
    valor_14d FLOAT,
    valor_28d FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'Carga Total'::VARCHAR,
        carga_acumulada_n_dias(p_atleta_id, p_data_referencia, 7),
        carga_acumulada_n_dias(p_atleta_id, p_data_referencia, 14),
        carga_acumulada_n_dias(p_atleta_id, p_data_referencia, 28)
    UNION ALL
    SELECT 
        'Média Diária'::VARCHAR,
        media_movel_player_load(p_atleta_id, p_data_referencia, 7),
        media_movel_player_load(p_atleta_id, p_data_referencia, 14),
        media_movel_player_load(p_atleta_id, p_data_referencia, 28)
    UNION ALL
    SELECT 
        'Monotonia'::VARCHAR,
        calcular_monotonia(p_atleta_id, p_data_referencia, 7),
        calcular_monotonia(p_atleta_id, p_data_referencia, 14),
        calcular_monotonia(p_atleta_id, p_data_referencia, 28)
    UNION ALL
    SELECT 
        'Strain'::VARCHAR,
        calcular_strain(p_atleta_id, p_data_referencia, 7),
        calcular_strain(p_atleta_id, p_data_referencia, 14),
        calcular_strain(p_atleta_id, p_data_referencia, 28)
    UNION ALL
    SELECT 
        'ACWR'::VARCHAR,
        calcular_acwr(p_atleta_id, p_data_referencia),
        NULL,
        NULL;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION resumo_atleta IS 
'Retorna resumo completo das métricas de carga para um atleta';

-- Exemplo de uso:
-- SELECT * FROM resumo_atleta(1, NOW());

-- ============================================================================
-- FUNÇÃO 8: Número de Sessões nos Últimos N Dias
-- ============================================================================
CREATE OR REPLACE FUNCTION num_sessoes_n_dias(
    p_atleta_id INTEGER,
    p_data_referencia TIMESTAMP,
    p_n_dias INTEGER DEFAULT 7
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(DISTINCT sessao_id)
    INTO v_count
    FROM dados_gps
    WHERE atleta_id = p_atleta_id
      AND time BETWEEN (p_data_referencia - (p_n_dias || ' days')::INTERVAL) 
                   AND p_data_referencia;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FUNÇÃO 9: Identificar Atletas em Risco
-- ============================================================================
CREATE OR REPLACE FUNCTION atletas_em_risco(
    p_data_referencia TIMESTAMP DEFAULT NOW(),
    p_threshold_acwr FLOAT DEFAULT 1.5
)
RETURNS TABLE(
    atleta_id INTEGER,
    nome VARCHAR,
    posicao VARCHAR,
    acwr FLOAT,
    classificacao VARCHAR,
    carga_7d FLOAT,
    num_sessoes INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.nome_completo,
        a.posicao,
        calcular_acwr(a.id, p_data_referencia) AS acwr_value,
        classificar_acwr(calcular_acwr(a.id, p_data_referencia)),
        carga_acumulada_n_dias(a.id, p_data_referencia, 7),
        num_sessoes_n_dias(a.id, p_data_referencia, 7)
    FROM atletas a
    WHERE a.ativo = TRUE
      AND calcular_acwr(a.id, p_data_referencia) > p_threshold_acwr
    ORDER BY calcular_acwr(a.id, p_data_referencia) DESC;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION atletas_em_risco IS 
'Lista atletas com ACWR acima do threshold (padrão: 1.5)';

-- Exemplo:
-- SELECT * FROM atletas_em_risco(NOW(), 1.5);

-- ============================================================================
-- FUNÇÃO 10: Calcular Z-Score por Posição
-- ============================================================================
CREATE OR REPLACE FUNCTION calcular_zscore_posicao(
    p_atleta_id INTEGER,
    p_metrica VARCHAR,
    p_valor FLOAT,
    p_periodo INTERVAL DEFAULT INTERVAL '30 days'
)
RETURNS FLOAT AS $$
DECLARE
    v_posicao VARCHAR;
    v_media FLOAT;
    v_desvio FLOAT;
    v_zscore FLOAT;
BEGIN
    -- Obter posição do atleta
    SELECT posicao INTO v_posicao FROM atletas WHERE id = p_atleta_id;
    
    -- Calcular média e desvio da posição (simplificado, só para player_load)
    IF p_metrica = 'player_load' THEN
        SELECT AVG(g.player_load), STDDEV_SAMP(g.player_load)
        INTO v_media, v_desvio
        FROM dados_gps g
        JOIN atletas a ON g.atleta_id = a.id
        WHERE a.posicao = v_posicao
          AND g.time > NOW() - p_periodo;
    END IF;
    
    -- Calcular z-score
    IF v_desvio IS NOT NULL AND v_desvio > 0 THEN
        v_zscore := (p_valor - v_media) / v_desvio;
    ELSE
        v_zscore := NULL;
    END IF;
    
    RETURN v_zscore;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION calcular_zscore_posicao IS 
'Calcula z-score de uma métrica comparado com média da posição';

-- ============================================================================
-- VIEW: Dashboard Principal
-- ============================================================================
CREATE OR REPLACE VIEW dashboard_principal AS
SELECT 
    a.id AS atleta_id,
    a.nome_completo,
    a.posicao,
    calcular_acwr(a.id, NOW()) AS acwr_atual,
    classificar_acwr(calcular_acwr(a.id, NOW())) AS status_acwr,
    carga_acumulada_n_dias(a.id, NOW(), 7) AS carga_7d,
    media_movel_player_load(a.id, NOW(), 7) AS media_7d,
    num_sessoes_n_dias(a.id, NOW(), 7) AS sessoes_7d,
    calcular_monotonia(a.id, NOW(), 7) AS monotonia_7d
FROM atletas a
WHERE a.ativo = TRUE
ORDER BY calcular_acwr(a.id, NOW()) DESC NULLS LAST;

COMMENT ON VIEW dashboard_principal IS 
'View para dashboard com métricas principais de todos os atletas ativos';

-- Uso:
-- SELECT * FROM dashboard_principal;

-- ============================================================================
-- FIM DO SCRIPT 5
-- ============================================================================

\echo '✅ Funções auxiliares criadas com sucesso!'
\echo ''
\echo '📋 Funções disponíveis:'
\echo '  - carga_acumulada_n_dias(atleta_id, data, n_dias)'
\echo '  - calcular_acwr(atleta_id, data)'
\echo '  - classificar_acwr(acwr_valor)'
\echo '  - media_movel_player_load(atleta_id, data, n_dias)'
\echo '  - calcular_monotonia(atleta_id, data, n_dias)'
\echo '  - calcular_strain(atleta_id, data, n_dias)'
\echo '  - resumo_atleta(atleta_id, data)'
\echo '  - atletas_em_risco(data, threshold)'
\echo '  - calcular_zscore_posicao(atleta_id, metrica, valor, periodo)'
\echo ''
\echo '📊 Views disponíveis:'
\echo '  - dashboard_principal'
\echo ''
\echo '💡 Exemplo de uso:'
\echo '   SELECT * FROM resumo_atleta(1, NOW());'
\echo '   SELECT * FROM atletas_em_risco();'
\echo '   SELECT * FROM dashboard_principal;'
