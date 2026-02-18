#!/usr/bin/env python3
"""
Wellness and Physical Evaluation System
=======================================
Creates comprehensive athlete wellness tracking and physical evaluation system.

Based on scientific literature:
- Hooper & Mackinnon (1995): Monitoring overtraining in athletes
- McLean et al. (2010): Neuromuscular, endocrine, and perceptual fatigue responses
- Thorpe et al. (2015): Monitoring fatigue during the in-season competitive phase
- Buchheit (2014): Monitoring training status with HR measures
"""

import psycopg2
import os
from datetime import datetime, timedelta
import random
import numpy as np

try:
    load_dotenv = __import__('dotenv').load_dotenv
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5433'),
        database=os.getenv('DB_NAME', 'futebol_tese'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'desporto.20')
    )
except:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )

cursor = conn.cursor()

print("🏥 Creating Wellness & Physical Evaluation System\n")

# 1. Create wellness data table
print("1️⃣ Creating wellness data table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dados_wellness (
        id SERIAL PRIMARY KEY,
        atleta_id INTEGER REFERENCES atletas(id),
        data DATE NOT NULL,
        
        -- Subjective wellness (Hooper & Mackinnon scale 1-7)
        sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 7),
        sleep_hours DECIMAL(3,1),
        fatigue_level INTEGER CHECK (fatigue_level BETWEEN 1 AND 7),
        muscle_soreness INTEGER CHECK (muscle_soreness BETWEEN 1 AND 7),
        stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 7),
        mood INTEGER CHECK (mood BETWEEN 1 AND 7),
        
        -- Objective measures
        resting_hr INTEGER,
        hrv_rmssd DECIMAL(5,2), -- Heart Rate Variability
        body_weight DECIMAL(5,2),
        hydration_status INTEGER CHECK (hydration_status BETWEEN 1 AND 5),
        
        -- Wellness composite score (calculated)
        wellness_score DECIMAL(4,2),
        wellness_status VARCHAR(20), -- excellent, good, moderate, poor, very_poor
        
        -- Training readiness
        readiness_score DECIMAL(4,2),
        training_recommendation VARCHAR(50),
        
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

# 2. Create physical evaluation table
print("2️⃣ Creating physical evaluation table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS avaliacoes_fisicas (
        id SERIAL PRIMARY KEY,
        atleta_id INTEGER REFERENCES atletas(id),
        data_avaliacao DATE NOT NULL,
        tipo_avaliacao VARCHAR(50), -- pre_season, mid_season, post_season
        
        -- Speed & Agility Tests
        test_5_0_5_seconds DECIMAL(4,2), -- 5-0-5 agility test (seconds)
        sprint_35m_seconds DECIMAL(4,2), -- 35m sprint (seconds)
        
        -- Jump Tests (Bosco et al., 1983)
        cmj_height_cm DECIMAL(5,2), -- Countermovement Jump (cm)
        squat_jump_height_cm DECIMAL(5,2), -- Squat Jump (cm)
        hop_test_distance_m DECIMAL(5,2), -- Single leg hop test (meters)
        
        -- Endurance Tests
        bronco_test_time_seconds DECIMAL(6,2), -- Bronco fitness test (seconds)
        vo2_max_ml_kg_min DECIMAL(5,2), -- VO2 max calculated from bronco
        
        -- Derived metrics
        reactive_strength_index DECIMAL(6,2), -- CMJ/contact time
        power_to_weight_ratio DECIMAL(6,2),
        speed_endurance_index DECIMAL(6,2),
        
        -- Percentiles compared to position
        percentile_speed INTEGER,
        percentile_power INTEGER,
        percentile_endurance INTEGER,
        
        observacoes TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

# 3. Create opponent analysis table
print("3️⃣ Creating opponent analysis table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS analise_adversarios (
        id SERIAL PRIMARY KEY,
        nome_equipa VARCHAR(100) NOT NULL,
        
        -- Team strength factors (Lago-Peñas et al., 2010)
        ranking_liga INTEGER, -- Current league position
        pontos_ultimos_5_jogos INTEGER, -- Points in last 5 games
        golos_marcados_casa DECIMAL(3,1), -- Home goals scored average
        golos_sofridos_casa DECIMAL(3,1), -- Home goals conceded average
        golos_marcados_fora DECIMAL(3,1), -- Away goals scored average
        golos_sofridos_fora DECIMAL(3,1), -- Away goals conceded average
        
        -- Performance metrics
        posse_bola_media DECIMAL(4,1), -- Average possession %
        passes_certos_percentagem DECIMAL(4,1), -- Pass accuracy %
        finalizacoes_por_jogo DECIMAL(4,1), -- Shots per game
        
        -- Tactical factors (Castellano et al., 2012)
        estilo_jogo VARCHAR(50), -- attacking, defensive, balanced, counter_attack
        intensidade_pressao VARCHAR(20), -- high, medium, low
        
        -- Difficulty calculation
        dificuldade_casa DECIMAL(3,1) CHECK (dificuldade_casa BETWEEN 0 AND 5),
        dificuldade_fora DECIMAL(3,1) CHECK (dificuldade_fora BETWEEN 0 AND 5),
        
        ultima_atualizacao TIMESTAMP DEFAULT NOW()
    )
""")

# 4. Update sessions table for opponent difficulty
print("4️⃣ Adding opponent difficulty to sessions...")
cursor.execute("""
    ALTER TABLE sessoes 
    ADD COLUMN IF NOT EXISTS dificuldade_adversario DECIMAL(3,1) CHECK (dificuldade_adversario BETWEEN 0 AND 5)
""")

conn.commit()

# 5. Generate physical evaluation data for all athletes
print("\n5️⃣ Generating pre-season physical evaluations...")

cursor.execute("SELECT id, posicao, EXTRACT(YEAR FROM AGE(data_nascimento)) as idade FROM atletas WHERE ativo = TRUE")
athletes = cursor.fetchall()

# Position-based norms (based on literature)
POSITION_NORMS = {
    'GR': {  # Goalkeeper
        'sprint_35m': (4.8, 5.2),
        'test_5_0_5': (4.2, 4.6),
        'cmj': (35, 45),
        'squat_jump': (32, 42),
        'bronco': (1020, 1080),
        'vo2_max': (45, 52)
    },
    'DC': {  # Centre-back
        'sprint_35m': (4.4, 4.8),
        'test_5_0_5': (4.0, 4.4),
        'cmj': (38, 48),
        'squat_jump': (35, 45),
        'bronco': (980, 1040),
        'vo2_max': (48, 55)
    },
    'DL': {  # Full-back
        'sprint_35m': (4.2, 4.6),
        'test_5_0_5': (3.8, 4.2),
        'cmj': (40, 50),
        'squat_jump': (37, 47),
        'bronco': (940, 1000),
        'vo2_max': (52, 58)
    },
    'MC': {  # Central midfielder
        'sprint_35m': (4.3, 4.7),
        'test_5_0_5': (3.9, 4.3),
        'cmj': (39, 49),
        'squat_jump': (36, 46),
        'bronco': (920, 980),
        'vo2_max': (54, 60)
    },
    'MO': {  # Attacking midfielder
        'sprint_35m': (4.1, 4.5),
        'test_5_0_5': (3.7, 4.1),
        'cmj': (41, 51),
        'squat_jump': (38, 48),
        'bronco': (960, 1020),
        'vo2_max': (50, 57)
    },
    'AV': {  # Winger
        'sprint_35m': (4.0, 4.4),
        'test_5_0_5': (3.6, 4.0),
        'cmj': (42, 52),
        'squat_jump': (39, 49),
        'bronco': (950, 1010),
        'vo2_max': (51, 58)
    },
    'PL': {  # Striker
        'sprint_35m': (4.1, 4.5),
        'test_5_0_5': (3.8, 4.2),
        'cmj': (40, 50),
        'squat_jump': (37, 47),
        'bronco': (970, 1030),
        'vo2_max': (49, 56)
    }
}

eval_date = datetime(2025, 8, 10).date()  # Pre-season evaluation

for athlete_id, position, age in athletes:
    norms = POSITION_NORMS.get(position, POSITION_NORMS['MC'])
    
    # Age adjustment factor (performance declines ~1% per year after 25)
    age_factor = max(0.85, 1 - (max(0, float(age) - 25) * 0.01))
    
    # Generate test results with some individual variation
    sprint_35m = random.uniform(*norms['sprint_35m']) * (1 + random.uniform(-0.1, 0.05))
    test_5_0_5 = random.uniform(*norms['test_5_0_5']) * (1 + random.uniform(-0.1, 0.05))
    cmj = random.uniform(*norms['cmj']) * age_factor * (1 + random.uniform(-0.15, 0.15))
    squat_jump = random.uniform(*norms['squat_jump']) * age_factor * (1 + random.uniform(-0.15, 0.15))
    bronco_time = random.uniform(*norms['bronco']) * (1 + random.uniform(-0.05, 0.1))
    
    # Calculate VO2 max from Bronco test (Ramsbottom et al., 1988)
    vo2_max = 15.3 * (1800 / bronco_time) if bronco_time > 0 else random.uniform(*norms['vo2_max'])
    
    # Hop test (typically 2.2-2.8x leg length, estimate ~2.5m average)
    hop_distance = random.uniform(2.2, 2.8) * age_factor
    
    # Calculate derived metrics
    rsi = min(99.99, cmj / 0.25)  # Assuming 250ms contact time, cap at 99.99
    power_weight = min(99.99, (cmj * 9.81 * 75) / 10000)  # Estimate power-to-weight, reduced scale
    speed_endurance = min(99.99, (35 / sprint_35m) * (1800 / bronco_time) * 0.001)  # Reduced scale
    
    cursor.execute("""
        INSERT INTO avaliacoes_fisicas (
            atleta_id, data_avaliacao, tipo_avaliacao,
            test_5_0_5_seconds, sprint_35m_seconds,
            cmj_height_cm, squat_jump_height_cm, hop_test_distance_m,
            bronco_test_time_seconds, vo2_max_ml_kg_min,
            reactive_strength_index, power_to_weight_ratio, speed_endurance_index,
            percentile_speed, percentile_power, percentile_endurance
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        athlete_id, eval_date, 'pre_season',
        round(test_5_0_5, 2), round(sprint_35m, 2),
        round(cmj, 1), round(squat_jump, 1), round(hop_distance, 2),
        round(bronco_time, 1), round(vo2_max, 1),
        round(rsi, 2), round(power_weight, 1), round(speed_endurance, 2),
        random.randint(25, 95), random.randint(25, 95), random.randint(25, 95)
    ))

conn.commit()
print(f"✅ Generated physical evaluations for {len(athletes)} athletes")

# 6. Create opponent data
print("\n6️⃣ Creating opponent difficulty ratings...")

OPPONENTS = [
    ('Sporting CP', 1, 13, 2.8, 0.9, 1.8, 1.2, 62.5, 87.2, 14.2, 'attacking', 'high'),
    ('FC Porto', 2, 12, 2.6, 1.0, 1.9, 1.3, 59.8, 85.8, 13.8, 'balanced', 'high'),
    ('SL Benfica', 3, 11, 2.5, 1.1, 1.7, 1.4, 61.2, 86.5, 13.5, 'attacking', 'medium'),
    ('SC Braga', 4, 10, 2.2, 1.2, 1.5, 1.5, 55.3, 82.1, 12.1, 'balanced', 'medium'),
    ('Vitória SC', 8, 7, 1.8, 1.4, 1.2, 1.7, 48.2, 78.5, 10.8, 'defensive', 'low'),
    ('Gil Vicente', 12, 5, 1.4, 1.6, 1.0, 1.9, 45.1, 76.2, 9.5, 'defensive', 'low'),
    ('Rio Ave', 14, 4, 1.2, 1.8, 0.9, 2.1, 43.8, 74.8, 8.9, 'counter_attack', 'medium'),
    ('Casa Pia', 15, 3, 1.0, 1.9, 0.8, 2.2, 42.5, 73.1, 8.2, 'defensive', 'low'),
    ('Estoril Praia', 16, 2, 0.9, 2.0, 0.7, 2.3, 41.2, 71.5, 7.8, 'defensive', 'low'),
    ('Portimonense', 18, 1, 0.7, 2.2, 0.5, 2.5, 39.8, 69.2, 7.1, 'defensive', 'low')
]

for nome, ranking, pontos, gm_casa, gs_casa, gm_fora, gs_fora, posse, passes, final, estilo, pressao in OPPONENTS:
    # Calculate difficulty based on multiple factors (Lago-Peñas et al., 2010)
    # Factors: ranking (40%), recent form (25%), attacking threat (20%), home advantage (15%)
    
    ranking_score = (19 - ranking) / 18 * 5  # Invert ranking (1st = highest score)
    form_score = pontos / 15 * 5  # Max 15 points in 5 games
    attack_score = (gm_casa + gm_fora) / 5 * 5  # Attacking threat
    
    # Home difficulty (easier for them at home = harder for us)
    dif_casa = (ranking_score * 0.4 + form_score * 0.25 + attack_score * 0.2 + 0.8) # Home advantage
    dif_fora = (ranking_score * 0.4 + form_score * 0.25 + attack_score * 0.2 + 0.3) # Away disadvantage
    
    # Clamp to 0-5 range
    dif_casa = max(0, min(5, dif_casa))
    dif_fora = max(0, min(5, dif_fora))
    
    cursor.execute("""
        INSERT INTO analise_adversarios (
            nome_equipa, ranking_liga, pontos_ultimos_5_jogos,
            golos_marcados_casa, golos_sofridos_casa,
            golos_marcados_fora, golos_sofridos_fora,
            posse_bola_media, passes_certos_percentagem, finalizacoes_por_jogo,
            estilo_jogo, intensidade_pressao,
            dificuldade_casa, dificuldade_fora
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        nome, ranking, pontos, gm_casa, gs_casa, gm_fora, gs_fora,
        posse, passes, final, estilo, pressao, round(dif_casa, 1), round(dif_fora, 1)
    ))

# Update existing games with opponent difficulty
cursor.execute("""
    UPDATE sessoes s
    SET dificuldade_adversario = CASE 
        WHEN s.local = 'casa' THEN a.dificuldade_fora
        ELSE a.dificuldade_casa
    END
    FROM analise_adversarios a
    WHERE s.tipo = 'jogo' AND s.adversario = a.nome_equipa
""")

conn.commit()
print(f"✅ Created opponent analysis for {len(OPPONENTS)} teams")

# 7. Generate wellness data for the season
print("\n7️⃣ Generating wellness data for the season...")

start_date = datetime(2025, 8, 17)
end_date = datetime(2025, 12, 14)
current_date = start_date

wellness_records = 0

while current_date <= end_date:
    # Skip some days (athletes don't always report wellness)
    if random.random() < 0.85:  # 85% compliance rate
        for athlete_id, position, age in athletes:
            # Base wellness varies by individual and training load
            base_wellness = random.uniform(4.5, 6.5)
            
            # Get training load for this week
            week_start = current_date - timedelta(days=7)
            cursor.execute("""
                SELECT AVG(carga_total) as avg_load
                FROM dados_pse 
                WHERE atleta_id = %s AND time >= %s AND time <= %s
            """, (athlete_id, week_start, current_date))
            
            load_result = cursor.fetchone()
            avg_load = load_result[0] if load_result and load_result[0] else 400
            
            # Adjust wellness based on training load (higher load = lower wellness)
            load_factor = max(0.7, 1 - (avg_load - 400) / 1000)
            adjusted_wellness = base_wellness * load_factor
            
            # Individual metrics with realistic correlations
            sleep_quality = max(1, min(7, int(adjusted_wellness + random.uniform(-1, 1))))
            sleep_hours = max(5.0, min(10.0, 7.5 + random.uniform(-1.5, 1.5)))
            fatigue = max(1, min(7, int(8 - adjusted_wellness + random.uniform(-0.5, 0.5))))
            soreness = max(1, min(7, int(8 - adjusted_wellness + random.uniform(-1, 1))))
            stress = max(1, min(7, int(4 + random.uniform(-2, 2))))
            mood = max(1, min(7, int(adjusted_wellness + random.uniform(-1, 1))))
            
            # Objective measures
            resting_hr = int(55 + (7 - adjusted_wellness) * 5 + random.uniform(-5, 5))
            hrv = max(20, min(80, 45 + (adjusted_wellness - 4) * 8 + random.uniform(-10, 10)))
            weight = 75 + random.uniform(-2, 2)  # Stable weight
            hydration = max(1, min(5, int(3 + random.uniform(-1, 2))))
            
            # Calculate composite wellness score (McLean et al., 2010)
            wellness_score = (sleep_quality + (8-fatigue) + (8-soreness) + mood) / 4
            
            # Determine status
            if wellness_score >= 6:
                status = 'excellent'
                readiness = 1.0
                recommendation = 'full_training'
            elif wellness_score >= 5:
                status = 'good'
                readiness = 0.85
                recommendation = 'normal_training'
            elif wellness_score >= 4:
                status = 'moderate'
                readiness = 0.7
                recommendation = 'modified_training'
            elif wellness_score >= 3:
                status = 'poor'
                readiness = 0.5
                recommendation = 'light_training'
            else:
                status = 'very_poor'
                readiness = 0.3
                recommendation = 'rest_recovery'
            
            cursor.execute("""
                INSERT INTO dados_wellness (
                    atleta_id, data, sleep_quality, sleep_hours,
                    fatigue_level, muscle_soreness, stress_level, mood,
                    resting_hr, hrv_rmssd, body_weight, hydration_status,
                    wellness_score, wellness_status, readiness_score, training_recommendation
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                athlete_id, current_date.date(), sleep_quality, sleep_hours,
                fatigue, soreness, stress, mood,
                resting_hr, round(hrv, 1), round(weight, 1), hydration,
                round(wellness_score, 2), status, round(readiness, 2), recommendation
            ))
            
            wellness_records += 1
    
    current_date += timedelta(days=1)

conn.commit()
print(f"✅ Generated {wellness_records} wellness records")

# 8. Show summary
print("\n📊 System Summary:")

cursor.execute("SELECT COUNT(*) FROM avaliacoes_fisicas")
physical_count = cursor.fetchone()[0]
print(f"   Physical evaluations: {physical_count}")

cursor.execute("SELECT COUNT(*) FROM dados_wellness")
wellness_count = cursor.fetchone()[0]
print(f"   Wellness records: {wellness_count}")

cursor.execute("SELECT COUNT(*) FROM analise_adversarios")
opponent_count = cursor.fetchone()[0]
print(f"   Opponent analyses: {opponent_count}")

# Show sample data
print("\n📋 Sample Physical Evaluation:")
cursor.execute("""
    SELECT a.nome_completo, af.sprint_35m_seconds, af.cmj_height_cm, 
           af.vo2_max_ml_kg_min, af.percentile_speed
    FROM avaliacoes_fisicas af
    JOIN atletas a ON af.atleta_id = a.id
    LIMIT 3
""")

for nome, sprint, cmj, vo2, perc in cursor.fetchall():
    print(f"   {nome}: 35m={sprint}s, CMJ={cmj}cm, VO2={vo2}, Speed%={perc}")

print("\n📋 Sample Wellness Data:")
cursor.execute("""
    SELECT a.nome_completo, dw.data, dw.wellness_score, dw.wellness_status, dw.training_recommendation
    FROM dados_wellness dw
    JOIN atletas a ON dw.atleta_id = a.id
    ORDER BY dw.data DESC
    LIMIT 3
""")

for nome, data, score, status, rec in cursor.fetchall():
    print(f"   {nome} ({data}): Score={score}, Status={status}, Rec={rec}")

print("\n📋 Opponent Difficulty Ratings:")
cursor.execute("""
    SELECT nome_equipa, dificuldade_casa, dificuldade_fora, estilo_jogo
    FROM analise_adversarios
    ORDER BY dificuldade_casa DESC
    LIMIT 5
""")

for nome, dif_casa, dif_fora, estilo in cursor.fetchall():
    print(f"   {nome}: Home={dif_casa}, Away={dif_fora}, Style={estilo}")

cursor.close()
conn.close()

print("\n✅ WELLNESS & PHYSICAL SYSTEM COMPLETE!")
print("   ✅ Physical evaluation tests implemented")
print("   ✅ Wellness monitoring system created")
print("   ✅ Opponent difficulty rating system")
print("   ✅ Training readiness recommendations")
print("\n📚 Scientific References:")
print("   • Hooper & Mackinnon (1995) - Wellness monitoring")
print("   • McLean et al. (2010) - Fatigue responses")
print("   • Lago-Peñas et al. (2010) - Team performance factors")
print("   • Bosco et al. (1983) - Jump test protocols")
print("   • Ramsbottom et al. (1988) - VO2 estimation")
