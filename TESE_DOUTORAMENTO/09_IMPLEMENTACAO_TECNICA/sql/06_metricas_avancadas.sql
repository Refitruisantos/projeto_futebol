-- Advanced Training Load Metrics Schema
-- Metrics: Monotony, Strain, ACWR, Z-Score, Variation %

-- Drop table if exists (for clean re-creation during development)
DROP TABLE IF EXISTS metricas_carga CASCADE;

-- Create metrics table
CREATE TABLE metricas_carga (
    id SERIAL PRIMARY KEY,
    atleta_id INTEGER NOT NULL REFERENCES atletas(id) ON DELETE CASCADE,
    semana_inicio DATE NOT NULL,
    semana_fim DATE NOT NULL,
    
    -- Basic weekly metrics
    carga_total_semanal DECIMAL(10,2),      -- Sum of all daily loads (RPE × duration)
    media_carga DECIMAL(10,2),               -- Average daily load
    desvio_padrao DECIMAL(10,2),             -- Standard deviation of daily loads
    dias_treino INTEGER,                     -- Number of training days in week
    
    -- Advanced metrics
    monotonia DECIMAL(10,4),                 -- Monotony = mean / std_dev
    tensao DECIMAL(10,2),                    -- Strain = total_load × monotony
    variacao_percentual DECIMAL(10,2),       -- Week-to-week % change
    
    -- ACWR (Acute:Chronic Workload Ratio)
    carga_aguda DECIMAL(10,2),               -- 7-day rolling average
    carga_cronica DECIMAL(10,2),             -- 28-day rolling average
    acwr DECIMAL(10,4),                      -- Acute / Chronic ratio
    
    -- Z-Scores (standardized scores relative to team)
    z_score_carga DECIMAL(10,4),             -- (load - team_avg) / team_std
    z_score_monotonia DECIMAL(10,4),         -- Standardized monotony
    z_score_tensao DECIMAL(10,4),            -- Standardized strain
    z_score_acwr DECIMAL(10,4),              -- Standardized ACWR
    
    -- Risk indicators
    nivel_risco_monotonia VARCHAR(10),       -- 'green', 'yellow', 'red'
    nivel_risco_tensao VARCHAR(10),          -- 'green', 'yellow', 'red'
    nivel_risco_acwr VARCHAR(10),            -- 'green', 'yellow', 'red'
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_athlete_week UNIQUE (atleta_id, semana_inicio),
    CONSTRAINT check_week_order CHECK (semana_fim >= semana_inicio)
);

-- Indexes for performance
CREATE INDEX idx_metricas_atleta ON metricas_carga(atleta_id);
CREATE INDEX idx_metricas_semana_inicio ON metricas_carga(semana_inicio);
CREATE INDEX idx_metricas_semana_fim ON metricas_carga(semana_fim);
CREATE INDEX idx_metricas_created ON metricas_carga(created_at);

-- Comments for documentation
COMMENT ON TABLE metricas_carga IS 'Advanced training load metrics for injury prevention and performance optimization';
COMMENT ON COLUMN metricas_carga.monotonia IS 'Training load monotony: mean/std_dev. >2.0 indicates high injury risk';
COMMENT ON COLUMN metricas_carga.tensao IS 'Training strain: total_load × monotony. >6000 indicates high stress';
COMMENT ON COLUMN metricas_carga.acwr IS 'Acute:Chronic Workload Ratio. Sweet spot: 0.8-1.3';
COMMENT ON COLUMN metricas_carga.z_score_carga IS 'Standardized load relative to team average';

-- Create view for easy risk zone queries
CREATE OR REPLACE VIEW vw_metricas_risco AS
SELECT 
    mc.*,
    a.nome_completo,
    a.posicao,
    CASE 
        WHEN mc.nivel_risco_monotonia = 'red' OR 
             mc.nivel_risco_tensao = 'red' OR 
             mc.nivel_risco_acwr = 'red' THEN 'high'
        WHEN mc.nivel_risco_monotonia = 'yellow' OR 
             mc.nivel_risco_tensao = 'yellow' OR 
             mc.nivel_risco_acwr = 'yellow' THEN 'moderate'
        ELSE 'low'
    END as risco_geral
FROM metricas_carga mc
JOIN atletas a ON a.id = mc.atleta_id
ORDER BY mc.semana_inicio DESC, a.nome_completo;

COMMENT ON VIEW vw_metricas_risco IS 'Metrics with athlete info and overall risk assessment';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON metricas_carga TO postgres;
GRANT USAGE, SELECT ON SEQUENCE metricas_carga_id_seq TO postgres;
GRANT SELECT ON vw_metricas_risco TO postgres;
