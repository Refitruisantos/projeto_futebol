-- ============================================================================
-- SCRIPT 3: ÍNDICES E OTIMIZAÇÃO
-- Descrição: Índices recomendados para hypertables e tabelas relacionais
-- ============================================================================

\echo '⚡ Criando índices de otimização...'

-- ============================================================================
-- 1. DADOS GPS (hypertable)
-- Padrões de consulta típicos:
--   - por atleta e intervalo temporal (funções de carga)
--   - por sessão e intervalo temporal
--   - por tempo (exploração / debugging)
-- ============================================================================

-- Garantir índices base (idempotente)
CREATE INDEX IF NOT EXISTS idx_dados_gps_time ON dados_gps(time DESC);
CREATE INDEX IF NOT EXISTS idx_dados_gps_atleta ON dados_gps(atleta_id);
CREATE INDEX IF NOT EXISTS idx_dados_gps_sessao ON dados_gps(sessao_id);

-- Índices compostos para acelerar filtros por atleta/sessão + janela temporal
CREATE INDEX IF NOT EXISTS idx_dados_gps_atleta_time ON dados_gps(atleta_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_dados_gps_sessao_time ON dados_gps(sessao_id, time DESC);

-- Cobrir consultas que agregam por atleta e sessão dentro de janelas
CREATE INDEX IF NOT EXISTS idx_dados_gps_atleta_sessao_time ON dados_gps(atleta_id, sessao_id, time DESC);

-- ============================================================================
-- 2. DADOS PSE (hypertable)
-- Padrões de consulta típicos:
--   - por atleta e intervalo temporal
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_dados_pse_time ON dados_pse(time DESC);
CREATE INDEX IF NOT EXISTS idx_dados_pse_atleta ON dados_pse(atleta_id);
CREATE INDEX IF NOT EXISTS idx_dados_pse_atleta_time ON dados_pse(atleta_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_dados_pse_sessao_time ON dados_pse(sessao_id, time DESC);

-- ============================================================================
-- 3. CONTEXTO COMPETITIVO (hypertable)
-- Padrões de consulta típicos:
--   - por sessão (jogo) e evolução temporal
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_contexto_time ON contexto_competitivo(time DESC);
CREATE INDEX IF NOT EXISTS idx_contexto_sessao ON contexto_competitivo(sessao_id);
CREATE INDEX IF NOT EXISTS idx_contexto_sessao_time ON contexto_competitivo(sessao_id, time DESC);

-- Opcional: filtros frequentes por adversário/local/estado do marcador
CREATE INDEX IF NOT EXISTS idx_contexto_adversario ON contexto_competitivo(adversario);
CREATE INDEX IF NOT EXISTS idx_contexto_local ON contexto_competitivo(local);
CREATE INDEX IF NOT EXISTS idx_contexto_estado_marcador ON contexto_competitivo(estado_marcador);

-- ============================================================================
-- 4. ALERTAS (relacional)
-- Útil para dashboards e filtros por atributos JSONB
-- ============================================================================

-- Índices já existentes no schema: atleta_id/data_geracao, tipo, não resolvidos
-- Complemento para JSONB (condicoes/metricas/contexto)
CREATE INDEX IF NOT EXISTS idx_alertas_condicoes_gin ON alertas USING GIN (condicoes);
CREATE INDEX IF NOT EXISTS idx_alertas_metricas_gin ON alertas USING GIN (metricas);
CREATE INDEX IF NOT EXISTS idx_alertas_contexto_gin ON alertas USING GIN (contexto);

-- ============================================================================
-- 5. Manutenção / estatísticas
-- ============================================================================

ANALYZE atletas;
ANALYZE sessoes;
ANALYZE dados_gps;
ANALYZE dados_pse;
ANALYZE contexto_competitivo;
ANALYZE testes_fisicos;
ANALYZE lesoes;
ANALYZE alertas;

\echo '✅ Índices criados com sucesso!'
\echo '📌 Próximo passo: Executar 04_continuous_aggregates.sql'
