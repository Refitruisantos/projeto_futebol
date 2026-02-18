-- Drop existing view if it exists
DROP VIEW IF EXISTS dashboard_principal CASCADE;

-- Create a simplified dashboard view that works with the data we have
CREATE VIEW dashboard_principal AS
SELECT 
    a.id AS atleta_id,
    a.nome_completo AS nome,
    a.posicao,
    a.numero_camisola,
    
    -- GPS metrics - averages across all sessions
    ROUND(AVG(g.distancia_total)::numeric, 2) AS distancia_total_media,
    ROUND(MAX(g.velocidade_max)::numeric, 2) AS velocidade_max_recorde,
    ROUND(AVG(g.aceleracoes)::numeric, 2) AS aceleracoes_media,
    ROUND(AVG(g.desaceleracoes)::numeric, 2) AS desaceleracoes_media,
    ROUND(AVG(g.effs_19_8_kmh)::numeric, 2) AS hsrs_media,
    ROUND(AVG(g.dist_19_8_kmh)::numeric, 2) AS dist_hsr_media,
    
    -- Count of sessions participated
    COUNT(DISTINCT g.sessao_id) AS num_sessoes,
    
    -- Most recent session date
    MAX(g.time) AS ultima_sessao,
    
    -- Status indicators
    CASE 
        WHEN COUNT(DISTINCT g.sessao_id) >= 4 THEN 'Normal'
        WHEN COUNT(DISTINCT g.sessao_id) BETWEEN 2 AND 3 THEN 'Atenção'
        ELSE 'Risco'
    END AS status_carga,
    
    -- Active flag
    a.ativo

FROM atletas a
LEFT JOIN dados_gps g ON a.id = g.atleta_id
WHERE a.ativo = TRUE
GROUP BY a.id, a.nome_completo, a.posicao, a.numero_camisola, a.ativo
ORDER BY distancia_total_media DESC NULLS LAST;

-- Verify view was created
SELECT COUNT(*) as athlete_count FROM dashboard_principal;
SELECT nome, distancia_total_media, num_sessoes FROM dashboard_principal LIMIT 5;
