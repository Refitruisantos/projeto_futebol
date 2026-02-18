#!/usr/bin/env python3
"""
Enhanced Risk Prediction System
===============================
Integrates wellness, physical evaluation, and training load data for comprehensive
risk assessment and substitution recommendations.

Based on scientific literature:
- Gabbett (2016): The training-injury prevention paradox
- Bourdon et al. (2017): Monitoring athlete training loads
- Saw et al. (2016): Monitoring the athlete training response
- Thorpe et al. (2017): The influence of changes in acute and chronic loads
"""

import psycopg2
import os
from datetime import datetime, timedelta
import numpy as np
import json

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

print("🧠 Enhanced Risk Prediction System\n")

# 1. Create enhanced risk assessment table
print("1️⃣ Creating enhanced risk assessment table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_assessment (
        id SERIAL PRIMARY KEY,
        atleta_id INTEGER REFERENCES atletas(id),
        data_avaliacao DATE NOT NULL,
        
        -- Training Load Risk Factors (Gabbett, 2016)
        acwr_risk_score DECIMAL(4,2), -- Acute:Chronic Workload Ratio risk
        monotony_risk_score DECIMAL(4,2), -- Training monotony risk
        strain_risk_score DECIMAL(4,2), -- Training strain risk
        
        -- Wellness Risk Factors (Saw et al., 2016)
        wellness_risk_score DECIMAL(4,2), -- Current wellness status
        wellness_trend_score DECIMAL(4,2), -- 7-day wellness trend
        sleep_risk_score DECIMAL(4,2), -- Sleep quality/quantity risk
        
        -- Physical Readiness Factors
        physical_readiness_score DECIMAL(4,2), -- Based on physical tests
        fatigue_accumulation_score DECIMAL(4,2), -- Cumulative fatigue
        
        -- Contextual Factors
        opponent_difficulty_factor DECIMAL(4,2), -- Next opponent difficulty
        position_specific_risk DECIMAL(4,2), -- Position-based risk adjustment
        
        -- Composite Risk Scores
        injury_risk_score DECIMAL(4,2), -- Overall injury risk (0-10)
        performance_risk_score DECIMAL(4,2), -- Performance decline risk (0-10)
        substitution_risk_score DECIMAL(4,2), -- Risk of needing substitution (0-10)
        
        -- Risk Categories
        injury_risk_category VARCHAR(20), -- low, moderate, high, very_high
        performance_risk_category VARCHAR(20),
        substitution_risk_category VARCHAR(20),
        
        -- Recommendations
        training_recommendation TEXT,
        match_recommendation TEXT,
        substitution_recommendation TEXT,
        
        -- Confidence and validity
        prediction_confidence DECIMAL(4,2), -- Model confidence (0-1)
        data_completeness DECIMAL(4,2), -- Available data completeness (0-1)
        
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

# 2. Create match readiness assessment table
print("2️⃣ Creating match readiness assessment table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS match_readiness (
        id SERIAL PRIMARY KEY,
        atleta_id INTEGER REFERENCES atletas(id),
        sessao_id INTEGER REFERENCES sessoes(id),
        data_jogo DATE NOT NULL,
        
        -- Pre-match readiness factors
        wellness_readiness DECIMAL(4,2), -- 0-10 scale
        physical_readiness DECIMAL(4,2), -- 0-10 scale
        training_load_readiness DECIMAL(4,2), -- 0-10 scale
        
        -- Match-specific factors
        opponent_difficulty DECIMAL(3,1), -- 0-5 scale
        expected_minutes INTEGER, -- Expected playing time
        position_demands_score DECIMAL(4,2), -- Position-specific demands
        
        -- Overall readiness
        overall_readiness_score DECIMAL(4,2), -- 0-10 composite score
        readiness_category VARCHAR(20), -- excellent, good, moderate, poor, very_poor
        
        -- Substitution predictions
        substitution_probability DECIMAL(4,2), -- 0-1 probability
        predicted_substitution_minute INTEGER, -- Predicted sub minute
        substitution_reason VARCHAR(100), -- fatigue, injury_risk, performance
        
        -- Recommendations
        starting_recommendation BOOLEAN, -- Should start the match
        minutes_recommendation INTEGER, -- Recommended max minutes
        monitoring_priority VARCHAR(20), -- low, medium, high, critical
        
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

conn.commit()

# 3. Enhanced risk calculation function
def calculate_enhanced_risk(athlete_id, assessment_date):
    """Calculate comprehensive risk assessment for an athlete"""
    
    # Get recent training load data
    cursor.execute("""
        SELECT acwr, monotonia, tensao, carga_total_semanal
        FROM metricas_carga
        WHERE atleta_id = %s
        ORDER BY semana_inicio DESC
        LIMIT 4
    """, (athlete_id,))
    
    load_data = cursor.fetchall()
    if not load_data:
        return None
    
    recent_acwr = float(load_data[0][0]) if load_data[0][0] else 1.0
    recent_monotony = float(load_data[0][1]) if load_data[0][1] else 2.0
    recent_strain = float(load_data[0][2]) if load_data[0][2] else 1000
    
    # ACWR Risk (Gabbett, 2016)
    if recent_acwr < 0.8 or recent_acwr > 1.5:
        acwr_risk = min(10, abs(recent_acwr - 1.0) * 8)
    else:
        acwr_risk = 2.0
    
    # Monotony Risk
    monotony_risk = min(10, max(0, (recent_monotony - 2.0) * 2))
    
    # Strain Risk
    strain_risk = min(10, max(0, (recent_strain - 10000) / 2000))
    
    # Get recent wellness data
    cursor.execute("""
        SELECT wellness_score, readiness_score, sleep_quality, fatigue_level
        FROM dados_wellness
        WHERE atleta_id = %s AND data >= %s
        ORDER BY data DESC
        LIMIT 7
    """, (athlete_id, assessment_date - timedelta(days=7)))
    
    wellness_data = cursor.fetchall()
    
    if wellness_data:
        recent_wellness = np.mean([float(w[0]) for w in wellness_data if w[0]])
        wellness_trend = np.polyfit(range(len(wellness_data)), [float(w[0]) for w in wellness_data if w[0]], 1)[0] if len(wellness_data) > 2 else 0
        avg_sleep = np.mean([float(w[2]) for w in wellness_data if w[2]])
        avg_fatigue = np.mean([float(w[3]) for w in wellness_data if w[3]])
        
        wellness_risk = max(0, (7 - recent_wellness) * 1.5)
        wellness_trend_risk = max(0, -wellness_trend * 10)  # Negative trend = higher risk
        sleep_risk = max(0, (4 - avg_sleep) * 2)
        fatigue_risk = max(0, (avg_fatigue - 3) * 2)
    else:
        wellness_risk = 5.0  # Default moderate risk
        wellness_trend_risk = 3.0
        sleep_risk = 3.0
        fatigue_risk = 3.0
    
    # Get physical evaluation data
    cursor.execute("""
        SELECT percentile_speed, percentile_power, percentile_endurance
        FROM avaliacoes_fisicas
        WHERE atleta_id = %s
        ORDER BY data_avaliacao DESC
        LIMIT 1
    """, (athlete_id,))
    
    physical_data = cursor.fetchone()
    if physical_data:
        avg_percentile = np.mean(physical_data)
        physical_readiness = max(2, 10 - (avg_percentile / 10))  # Lower percentile = higher risk
    else:
        physical_readiness = 5.0
    
    # Get position-specific risk
    cursor.execute("SELECT posicao FROM atletas WHERE id = %s", (athlete_id,))
    position = cursor.fetchone()[0]
    
    # Position risk factors (based on injury rates and demands)
    position_risk_factors = {
        'GR': 1.0,   # Lowest risk
        'DC': 1.2,   # Moderate risk
        'DL': 1.8,   # Higher risk (more running)
        'MC': 2.0,   # High risk (most demanding)
        'MO': 1.6,   # Moderate-high risk
        'AV': 1.9,   # High risk (sprints, changes of direction)
        'PL': 1.4    # Moderate risk
    }
    
    position_multiplier = position_risk_factors.get(position, 1.5)
    
    # Calculate composite scores
    injury_risk = (acwr_risk * 0.3 + monotony_risk * 0.2 + wellness_risk * 0.3 + 
                  physical_readiness * 0.2) * position_multiplier
    
    performance_risk = (wellness_risk * 0.4 + fatigue_risk * 0.3 + 
                       strain_risk * 0.2 + physical_readiness * 0.1)
    
    substitution_risk = (injury_risk * 0.4 + performance_risk * 0.4 + 
                        wellness_trend_risk * 0.2)
    
    # Cap at 10
    injury_risk = min(10, injury_risk)
    performance_risk = min(10, performance_risk)
    substitution_risk = min(10, substitution_risk)
    
    # Determine categories
    def get_risk_category(score):
        if score < 3:
            return 'low'
        elif score < 5:
            return 'moderate'
        elif score < 7:
            return 'high'
        else:
            return 'very_high'
    
    # Generate recommendations
    training_rec = generate_training_recommendation(injury_risk, wellness_risk, fatigue_risk)
    match_rec = generate_match_recommendation(substitution_risk, performance_risk)
    sub_rec = generate_substitution_recommendation(substitution_risk, position)
    
    # Calculate confidence based on data availability
    data_completeness = (len(load_data) / 4 * 0.3 + 
                        len(wellness_data) / 7 * 0.4 + 
                        (1 if physical_data else 0) * 0.3)
    
    confidence = min(1.0, data_completeness * 0.8 + 0.2)  # Base confidence of 0.2
    
    return {
        'acwr_risk_score': round(acwr_risk, 2),
        'monotony_risk_score': round(monotony_risk, 2),
        'strain_risk_score': round(strain_risk, 2),
        'wellness_risk_score': round(wellness_risk, 2),
        'wellness_trend_score': round(wellness_trend_risk, 2),
        'sleep_risk_score': round(sleep_risk, 2),
        'physical_readiness_score': round(physical_readiness, 2),
        'fatigue_accumulation_score': round(fatigue_risk, 2),
        'position_specific_risk': round(position_multiplier, 2),
        'injury_risk_score': round(injury_risk, 2),
        'performance_risk_score': round(performance_risk, 2),
        'substitution_risk_score': round(substitution_risk, 2),
        'injury_risk_category': get_risk_category(injury_risk),
        'performance_risk_category': get_risk_category(performance_risk),
        'substitution_risk_category': get_risk_category(substitution_risk),
        'training_recommendation': training_rec,
        'match_recommendation': match_rec,
        'substitution_recommendation': sub_rec,
        'prediction_confidence': round(confidence, 2),
        'data_completeness': round(data_completeness, 2)
    }

def generate_training_recommendation(injury_risk, wellness_risk, fatigue_risk):
    """Generate training recommendations based on risk scores"""
    if injury_risk > 7 or wellness_risk > 7:
        return "Complete rest or very light recovery session only"
    elif injury_risk > 5 or wellness_risk > 5:
        return "Modified training - reduce intensity by 30-40%"
    elif fatigue_risk > 6:
        return "Focus on recovery protocols, avoid high-intensity work"
    else:
        return "Normal training load acceptable"

def generate_match_recommendation(substitution_risk, performance_risk):
    """Generate match participation recommendations"""
    if substitution_risk > 8:
        return "Consider not starting - high substitution risk"
    elif substitution_risk > 6:
        return "Start but monitor closely - prepare early substitution"
    elif performance_risk > 7:
        return "May start but expect reduced performance"
    else:
        return "Cleared for normal match participation"

def generate_substitution_recommendation(substitution_risk, position):
    """Generate substitution timing recommendations"""
    base_minutes = {
        'GR': 90,  # Goalkeepers rarely substituted
        'DC': 75,  # Centre-backs can play longer
        'DL': 65,  # Full-backs high intensity
        'MC': 60,  # Midfielders most demanding
        'MO': 70,  # Attacking mids moderate
        'AV': 65,  # Wingers high intensity
        'PL': 70   # Strikers moderate
    }
    
    base_min = base_minutes.get(position, 70)
    
    if substitution_risk > 8:
        return f"High risk - consider substitution around {base_min - 20} minutes"
    elif substitution_risk > 6:
        return f"Moderate risk - monitor for substitution around {base_min - 10} minutes"
    elif substitution_risk > 4:
        return f"Low risk - normal substitution timing around {base_min} minutes"
    else:
        return "Very low substitution risk - can play full match"

# 4. Generate risk assessments for all athletes
print("\n3️⃣ Generating enhanced risk assessments...")

cursor.execute("SELECT id FROM atletas WHERE ativo = TRUE")
athletes = cursor.fetchall()

assessment_date = datetime.now().date()
assessments_created = 0

for (athlete_id,) in athletes:
    risk_data = calculate_enhanced_risk(athlete_id, assessment_date)
    
    if risk_data:
        cursor.execute("""
            INSERT INTO risk_assessment (
                atleta_id, data_avaliacao,
                acwr_risk_score, monotony_risk_score, strain_risk_score,
                wellness_risk_score, wellness_trend_score, sleep_risk_score,
                physical_readiness_score, fatigue_accumulation_score,
                position_specific_risk,
                injury_risk_score, performance_risk_score, substitution_risk_score,
                injury_risk_category, performance_risk_category, substitution_risk_category,
                training_recommendation, match_recommendation, substitution_recommendation,
                prediction_confidence, data_completeness
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            athlete_id, assessment_date,
            risk_data['acwr_risk_score'], risk_data['monotony_risk_score'], risk_data['strain_risk_score'],
            risk_data['wellness_risk_score'], risk_data['wellness_trend_score'], risk_data['sleep_risk_score'],
            risk_data['physical_readiness_score'], risk_data['fatigue_accumulation_score'],
            risk_data['position_specific_risk'],
            risk_data['injury_risk_score'], risk_data['performance_risk_score'], risk_data['substitution_risk_score'],
            risk_data['injury_risk_category'], risk_data['performance_risk_category'], risk_data['substitution_risk_category'],
            risk_data['training_recommendation'], risk_data['match_recommendation'], risk_data['substitution_recommendation'],
            risk_data['prediction_confidence'], risk_data['data_completeness']
        ))
        
        assessments_created += 1

conn.commit()
print(f"✅ Created {assessments_created} enhanced risk assessments")

# 5. Generate match readiness for next game
print("\n4️⃣ Generating match readiness assessments...")

# Get next game
cursor.execute("""
    SELECT id, data, adversario, dificuldade_adversario
    FROM sessoes
    WHERE tipo = 'jogo' AND data >= %s
    ORDER BY data ASC
    LIMIT 1
""", (datetime.now().date(),))

next_game = cursor.fetchone()

if next_game:
    game_id, game_date, opponent, difficulty = next_game
    print(f"   Next game: {opponent} on {game_date} (Difficulty: {difficulty})")
    
    readiness_created = 0
    
    for (athlete_id,) in athletes:
        # Get latest risk assessment
        cursor.execute("""
            SELECT wellness_risk_score, physical_readiness_score, 
                   injury_risk_score, substitution_risk_score
            FROM risk_assessment
            WHERE atleta_id = %s
            ORDER BY data_avaliacao DESC
            LIMIT 1
        """, (athlete_id,))
        
        risk_data = cursor.fetchone()
        if not risk_data:
            continue
            
        wellness_risk, physical_risk, injury_risk, sub_risk = risk_data
        
        # Convert risk scores to readiness scores (inverse relationship)
        wellness_readiness = max(0, 10 - wellness_risk)
        physical_readiness = max(0, 10 - physical_risk)
        load_readiness = max(0, 10 - injury_risk)
        
        # Get position demands
        cursor.execute("SELECT posicao FROM atletas WHERE id = %s", (athlete_id,))
        position = cursor.fetchone()[0]
        
        position_demands = {
            'GR': 3.0,   # Lowest physical demands
            'DC': 5.0,   # Moderate demands
            'DL': 8.0,   # High demands
            'MC': 9.0,   # Highest demands
            'MO': 7.0,   # High demands
            'AV': 8.5,   # Very high demands
            'PL': 6.0    # Moderate-high demands
        }
        
        demands_score = position_demands.get(position, 7.0)
        
        # Calculate overall readiness
        overall_readiness = (wellness_readiness * 0.4 + 
                           physical_readiness * 0.3 + 
                           load_readiness * 0.3)
        
        # Adjust for opponent difficulty
        difficulty_adjustment = (difficulty or 2.5) / 5.0  # Normalize to 0-1
        adjusted_readiness = overall_readiness * (1 - difficulty_adjustment * 0.2)
        
        # Determine readiness category
        if adjusted_readiness >= 8:
            readiness_cat = 'excellent'
        elif adjusted_readiness >= 6.5:
            readiness_cat = 'good'
        elif adjusted_readiness >= 5:
            readiness_cat = 'moderate'
        elif adjusted_readiness >= 3:
            readiness_cat = 'poor'
        else:
            readiness_cat = 'very_poor'
        
        # Calculate substitution probability
        sub_probability = min(1.0, sub_risk / 10)
        
        # Predict substitution minute based on position and risk
        base_minutes = {'GR': 90, 'DC': 75, 'DL': 65, 'MC': 60, 'MO': 70, 'AV': 65, 'PL': 70}
        predicted_minute = max(45, base_minutes.get(position, 70) - int(sub_risk * 5))
        
        # Determine substitution reason
        if wellness_risk > 6:
            sub_reason = 'fatigue'
        elif injury_risk > 6:
            sub_reason = 'injury_risk'
        else:
            sub_reason = 'performance'
        
        # Starting recommendation
        should_start = adjusted_readiness >= 5.0 and injury_risk < 7
        
        # Minutes recommendation
        if adjusted_readiness >= 7:
            max_minutes = 90
        elif adjusted_readiness >= 5:
            max_minutes = 75
        else:
            max_minutes = 60
        
        # Monitoring priority
        if injury_risk > 7 or sub_risk > 7:
            monitoring = 'critical'
        elif injury_risk > 5 or sub_risk > 5:
            monitoring = 'high'
        elif adjusted_readiness < 6:
            monitoring = 'medium'
        else:
            monitoring = 'low'
        
        cursor.execute("""
            INSERT INTO match_readiness (
                atleta_id, sessao_id, data_jogo,
                wellness_readiness, physical_readiness, training_load_readiness,
                opponent_difficulty, expected_minutes, position_demands_score,
                overall_readiness_score, readiness_category,
                substitution_probability, predicted_substitution_minute, substitution_reason,
                starting_recommendation, minutes_recommendation, monitoring_priority
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            athlete_id, game_id, game_date,
            round(wellness_readiness, 2), round(physical_readiness, 2), round(load_readiness, 2),
            difficulty, max_minutes, demands_score,
            round(adjusted_readiness, 2), readiness_cat,
            round(sub_probability, 2), predicted_minute, sub_reason,
            should_start, max_minutes, monitoring
        ))
        
        readiness_created += 1
    
    conn.commit()
    print(f"✅ Created {readiness_created} match readiness assessments")

# 6. Show summary and high-risk athletes
print("\n📊 Enhanced Risk System Summary:")

cursor.execute("""
    SELECT 
        COUNT(*) as total_assessments,
        COUNT(CASE WHEN injury_risk_category = 'high' THEN 1 END) as high_injury_risk,
        COUNT(CASE WHEN injury_risk_category = 'very_high' THEN 1 END) as very_high_injury_risk,
        COUNT(CASE WHEN substitution_risk_category IN ('high', 'very_high') THEN 1 END) as high_sub_risk,
        ROUND(AVG(prediction_confidence), 2) as avg_confidence
    FROM risk_assessment
    WHERE data_avaliacao = %s
""", (assessment_date,))

summary = cursor.fetchone()
print(f"   Total assessments: {summary[0]}")
print(f"   High injury risk: {summary[1]}")
print(f"   Very high injury risk: {summary[2]}")
print(f"   High substitution risk: {summary[3]}")
print(f"   Average confidence: {summary[4]}")

print("\n🚨 High-Risk Athletes:")
cursor.execute("""
    SELECT 
        a.nome_completo,
        a.posicao,
        ra.injury_risk_score,
        ra.substitution_risk_score,
        ra.training_recommendation
    FROM risk_assessment ra
    JOIN atletas a ON ra.atleta_id = a.id
    WHERE ra.data_avaliacao = %s
    AND (ra.injury_risk_category IN ('high', 'very_high') 
         OR ra.substitution_risk_category IN ('high', 'very_high'))
    ORDER BY ra.injury_risk_score DESC
""", (assessment_date,))

high_risk = cursor.fetchall()
for nome, pos, inj_risk, sub_risk, rec in high_risk:
    print(f"   {nome} ({pos}): Injury={inj_risk:.1f}, Sub={sub_risk:.1f} - {rec}")

if next_game:
    print(f"\n⚽ Match Readiness for {opponent}:")
    cursor.execute("""
        SELECT 
            a.nome_completo,
            a.posicao,
            mr.overall_readiness_score,
            mr.readiness_category,
            mr.starting_recommendation,
            mr.monitoring_priority
        FROM match_readiness mr
        JOIN atletas a ON mr.atleta_id = a.id
        WHERE mr.data_jogo = %s
        ORDER BY mr.overall_readiness_score DESC
        LIMIT 10
    """, (game_date,))
    
    readiness = cursor.fetchall()
    for nome, pos, score, cat, start, monitor in readiness:
        start_text = "✅" if start else "❌"
        print(f"   {start_text} {nome} ({pos}): {score:.1f} ({cat}) - Monitor: {monitor}")

cursor.close()
conn.close()

print("\n✅ ENHANCED RISK SYSTEM COMPLETE!")
print("   ✅ Comprehensive risk assessment implemented")
print("   ✅ Match readiness predictions created")
print("   ✅ Substitution recommendations generated")
print("   ✅ Training modifications suggested")
print("\n📚 Scientific Foundation:")
print("   • Gabbett (2016) - Training-injury prevention paradox")
print("   • Bourdon et al. (2017) - Monitoring athlete training loads")
print("   • Saw et al. (2016) - Monitoring athlete training response")
print("   • Thorpe et al. (2017) - Acute and chronic load influences")
