#!/usr/bin/env python3
"""Show all the comprehensive mock data that was generated"""

import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host='localhost', port='5433', database='futebol_tese',
    user='postgres', password='desporto.20'
)

print("🔍 COMPREHENSIVE MOCK DATA OVERVIEW")
print("=" * 80)

# 1. Enhanced Wellness Data
print("\n💤 ENHANCED WELLNESS DATA (with detailed sleep tracking):")
query = """
    SELECT 
        atleta_id, data, wellness_score, sleep_hours,
        tempo_cama, eficiencia_sono, sono_profundo_min, 
        ranking_wellness, training_recommendation
    FROM dados_wellness 
    WHERE tempo_cama IS NOT NULL 
    ORDER BY data DESC LIMIT 5
"""
df = pd.read_sql(query, conn)
print(df.to_string(index=False))

# 2. Enhanced GPS Data
print("\n🏃‍♂️ ENHANCED GPS DATA (with decelerations & player load):")
query = """
    SELECT 
        atleta_id, sessao_id, distancia_total, velocidade_max,
        num_desaceleracoes_altas, desaceleracao_maxima, player_load
    FROM dados_gps 
    WHERE num_desaceleracoes_altas IS NOT NULL 
    LIMIT 5
"""
df = pd.read_sql(query, conn)
print(df.to_string(index=False))

# 3. Portuguese Opponents
print("\n⚽ PORTUGUESE OPPONENT ANALYSIS:")
query = """
    SELECT 
        nome_equipa, ranking_liga, estilo_jogo, 
        dificuldade_casa, dificuldade_fora, posse_bola_media
    FROM analise_adversarios 
    ORDER BY ranking_liga
"""
df = pd.read_sql(query, conn)
print(df.to_string(index=False))

# 4. Physical Evaluations
print("\n🏋️‍♂️ PHYSICAL EVALUATIONS:")
query = """
    SELECT 
        a.nome_completo, af.data_avaliacao, af.sprint_35m_seconds,
        af.cmj_height_cm, af.vo2_max_ml_kg_min, af.percentile_speed
    FROM avaliacoes_fisicas af
    JOIN atletas a ON af.atleta_id = a.id
    ORDER BY af.data_avaliacao DESC LIMIT 5
"""
df = pd.read_sql(query, conn)
print(df.to_string(index=False))

# 5. Sessions with Opponents
print("\n📅 SESSIONS WITH OPPONENT DATA:")
query = """
    SELECT 
        data, tipo, adversario, dificuldade_adversario
    FROM sessoes 
    WHERE adversario IS NOT NULL 
    ORDER BY data DESC LIMIT 5
"""
df = pd.read_sql(query, conn)
print(df.to_string(index=False))

# 6. Load Metrics
print("\n📊 LOAD METRICS:")
query = """
    SELECT 
        atleta_id, semana_inicio, carga_total_semanal,
        carga_aguda, carga_cronica, acwr, monotonia
    FROM metricas_carga 
    ORDER BY semana_inicio DESC LIMIT 5
"""
df = pd.read_sql(query, conn)
print(df.to_string(index=False))

# Summary counts
print("\n📈 DATA SUMMARY:")
tables = [
    ('dados_wellness', 'tempo_cama IS NOT NULL'),
    ('dados_gps', 'num_desaceleracoes_altas IS NOT NULL'),
    ('analise_adversarios', '1=1'),
    ('avaliacoes_fisicas', '1=1'),
    ('sessoes', 'adversario IS NOT NULL'),
    ('metricas_carga', '1=1')
]

for table, condition in tables:
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {condition}")
    count = cursor.fetchone()[0]
    print(f"   {table}: {count} records")

conn.close()
print("\n✅ This is the FULL comprehensive mock data system!")
print("   Much more than basic CSV files - complete football monitoring simulation")
