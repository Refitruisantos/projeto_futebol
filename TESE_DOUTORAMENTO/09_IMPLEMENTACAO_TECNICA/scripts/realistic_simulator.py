#!/usr/bin/env python3
"""
Realistic Data Simulator - 10 Games, 10 Weeks
===============================================

Creates realistic training and game data for 10 weeks with proper risk distribution.
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta
import numpy as np
import random

def get_db_connection():
    """Get direct database connection"""
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
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def generate_realistic_schedule():
    """Generate 10-week schedule with games and training"""
    
    schedule = []
    start_date = datetime(2025, 1, 6)
    
    for week in range(10):
        week_start = start_date + timedelta(weeks=week)
        
        # Weekly pattern: Mon-Fri training, Sat game, Sun recovery
        weekly_sessions = [
            {'date': week_start, 'type': 'treino', 'duration': 75, 'intensity': 'medium'},
            {'date': week_start + timedelta(days=1), 'type': 'treino', 'duration': 90, 'intensity': 'high'},
            {'date': week_start + timedelta(days=2), 'type': 'treino', 'duration': 60, 'intensity': 'low'},
            {'date': week_start + timedelta(days=3), 'type': 'treino', 'duration': 85, 'intensity': 'high'},
            {'date': week_start + timedelta(days=4), 'type': 'treino', 'duration': 70, 'intensity': 'medium'},
            {'date': week_start + timedelta(days=5), 'type': 'jogo', 'duration': 105, 'intensity': 'very_high'},
            {'date': week_start + timedelta(days=6), 'type': 'recuperacao', 'duration': 45, 'intensity': 'very_low'}
        ]
        
        schedule.extend(weekly_sessions)
    
    return schedule

def generate_position_profiles():
    """Realistic training profiles by position"""
    
    return {
        'GR': {
            'pse_baseline': 4.5, 'pse_variation': 1.0,
            'distance_per_min': 80, 'speed_max': 25, 'accel_per_min': 0.15
        },
        'DC': {
            'pse_baseline': 6.2, 'pse_variation': 1.2,
            'distance_per_min': 95, 'speed_max': 27, 'accel_per_min': 0.18
        },
        'DL': {
            'pse_baseline': 6.8, 'pse_variation': 1.3,
            'distance_per_min': 110, 'speed_max': 30, 'accel_per_min': 0.22
        },
        'MC': {
            'pse_baseline': 7.1, 'pse_variation': 1.1,
            'distance_per_min': 120, 'speed_max': 32, 'accel_per_min': 0.25
        },
        'EX': {
            'pse_baseline': 6.9, 'pse_variation': 1.4,
            'distance_per_min': 115, 'speed_max': 34, 'accel_per_min': 0.20
        },
        'AV': {
            'pse_baseline': 7.3, 'pse_variation': 1.2,
            'distance_per_min': 105, 'speed_max': 33, 'accel_per_min': 0.23
        }
    }

def simulate_realistic_data():
    """Generate and insert realistic 10-week data"""
    
    print("🔄 Generating 10 weeks of realistic data...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM metricas_carga")
        cursor.execute("DELETE FROM dados_pse")
        cursor.execute("DELETE FROM dados_gps")
        cursor.execute("DELETE FROM sessoes")
        conn.commit()
        print("   Cleared existing data")
        
        # Get athletes
        cursor.execute("SELECT id, nome_completo, posicao FROM atletas WHERE ativo = TRUE")
        athletes = cursor.fetchall()
        print(f"   Found {len(athletes)} athletes")
        
        # Generate schedule
        schedule = generate_realistic_schedule()
        print(f"   Generated {len(schedule)} sessions (10 weeks)")
        
        # Get position profiles
        profiles = generate_position_profiles()
        
        # Insert sessions
        session_id_map = {}
        for i, session in enumerate(schedule):
            cursor.execute("""
                INSERT INTO sessoes (data, tipo, duracao_min, adversario, local, resultado)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                session['date'], session['type'], session['duration'],
                f"Adversário {i%5 + 1}" if session['type'] == 'jogo' else '',
                'casa' if session['type'] == 'jogo' else 'casa',
                f"{random.randint(0,4)}-{random.randint(0,4)}" if session['type'] == 'jogo' else ''
            ))
            
            session_id = cursor.fetchone()[0]
            session_id_map[i] = session_id
        
        conn.commit()
        print("   Sessions inserted")
        
        # Generate data for each athlete
        pse_records = 0
        gps_records = 0
        
        for athlete_id, nome, posicao in athletes:
            profile = profiles[posicao]
            
            for i, session in enumerate(schedule):
                session_id = session_id_map[i]
                
                # Generate realistic PSE
                intensity_modifiers = {
                    'very_low': 0.6, 'low': 0.8, 'medium': 1.0, 'high': 1.2, 'very_high': 1.4
                }
                
                base_pse = profile['pse_baseline']
                modifier = intensity_modifiers[session['intensity']]
                variation = np.random.normal(1.0, 0.15)
                
                pse = max(1.0, min(10.0, base_pse * modifier * variation))
                load = pse * session['duration']
                
                # Insert PSE data
                cursor.execute("""
                    INSERT INTO dados_pse (atleta_id, sessao_id, time, pse, duracao_min, carga_total)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    athlete_id, session_id, session['date'], pse, session['duration'], load
                ))
                pse_records += 1
                
                # Generate GPS data (skip recovery sessions)
                if session['type'] != 'recuperacao':
                    distance = profile['distance_per_min'] * session['duration'] * np.random.uniform(0.9, 1.1)
                    max_speed = profile['speed_max'] * np.random.uniform(0.85, 1.15)
                    accelerations = profile['accel_per_min'] * session['duration'] * np.random.uniform(0.8, 1.2)
                    
                    cursor.execute("""
                        INSERT INTO dados_gps (atleta_id, sessao_id, time, distancia_total, velocidade_max, 
                                           velocidade_media, aceleracoes, desaceleracoes, sprints)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        athlete_id, session_id, session['date'], distance, max_speed,
                        distance / session['duration'] * 60, int(accelerations),
                        int(accelerations * 0.9), int(accelerations * 0.3)
                    ))
                    gps_records += 1
        
        conn.commit()
        print(f"   Data generated: {pse_records} PSE records, {gps_records} GPS records")
        
        # Calculate realistic metrics
        calculate_realistic_metrics(cursor, athletes, schedule)
        
        print(f"\n✅ 10-week realistic data simulation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

def calculate_realistic_metrics(cursor, athletes, schedule):
    """Calculate metrics with realistic risk distribution"""
    
    print("   Calculating realistic metrics...")
    
    # Group sessions by week
    weeks = {}
    for session in schedule:
        week_start = session['date'] - timedelta(days=session['date'].weekday())
        if week_start not in weeks:
            weeks[week_start] = []
        weeks[week_start].append(session)
    
    metrics_count = 0
    
    for athlete_id, nome, posicao in athletes:
        # Create realistic load progression for this athlete
        base_load = np.random.normal(3000, 500)
        
        for week_start, week_sessions in weeks.items():
            try:
                # Get PSE data for this week
                session_dates = [s['date'] for s in week_sessions]
                
                cursor.execute("""
                    SELECT carga_total, pse, duracao_min, time
                    FROM dados_pse 
                    WHERE atleta_id = %s AND DATE(time) = ANY(%s)
                    ORDER BY time
                """, (athlete_id, session_dates))
                
                pse_data = cursor.fetchall()
                
                if len(pse_data) < 3:
                    continue
                
                # Calculate loads with realistic variation
                loads = [row[0] for row in pse_data if row[0] and row[0] > 0]
                
                # Add realistic progression and variation
                week_factor = 1.0 + (len(weeks) - list(weeks.keys()).index(week_start)) * 0.05
                individual_variation = np.random.normal(1.0, 0.1)
                
                adjusted_loads = [load * week_factor * individual_variation for load in loads]
                weekly_load = sum(adjusted_loads)
                
                # Calculate metrics
                mean_load = np.mean(adjusted_loads)
                std_load = np.std(adjusted_loads)
                monotony = mean_load / std_load if std_load > 0 else 1.0
                strain = weekly_load * monotony
                
                # Realistic ACWR calculation
                if len(adjusted_loads) >= 3:
                    acute_load = np.mean(adjusted_loads[-3:])
                    chronic_load = weekly_load / len(week_sessions) * 4  # 4-week average estimate
                    acwr = acute_load / chronic_load if chronic_load > 0 else 1.0
                else:
                    acwr = 1.0
                
                # Realistic risk distribution (not all red!)
                risk_monotony = 'green' if monotony < 2.0 else 'yellow' if monotony < 3.0 else 'red'
                risk_strain = 'green' if strain < 8000 else 'yellow' if strain < 12000 else 'red'
                risk_acwr = 'green' if 0.8 <= acwr <= 1.5 else 'yellow' if 0.6 <= acwr <= 1.8 else 'red'
                
                # Get GPS averages
                cursor.execute("""
                    SELECT AVG(distancia_total), AVG(velocidade_max), AVG(aceleracoes)
                    FROM dados_gps 
                    WHERE atleta_id = %s AND DATE(time) = ANY(%s)
                """, (athlete_id, session_dates))
                
                gps_avg = cursor.fetchone()
                avg_distance = gps_avg[0] or 5000
                avg_speed_max = gps_avg[1] or 25
                avg_accelerations = gps_avg[2] or 15
                
                # Insert metrics
                cursor.execute("""
                    INSERT INTO metricas_carga (
                        atleta_id, semana_inicio, semana_fim, carga_total_semanal,
                        media_carga, desvio_padrao, dias_treino, monotonia, tensao, acwr,
                        carga_aguda, carga_cronica, variacao_percentual,
                        z_score_carga, z_score_monotonia, z_score_tensao, z_score_acwr,
                        nivel_risco_monotonia, nivel_risco_tensao, nivel_risco_acwr
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    athlete_id, week_start, week_start + timedelta(days=6),
                    weekly_load, mean_load, std_load, len(pse_data),
                    monotony, strain, acwr, weekly_load, weekly_load * 4, 0.0,
                    0.0, 0.0, 0.0, 0.0,
                    risk_monotony, risk_strain, risk_acwr
                ))
                
                metrics_count += 1
                
            except Exception as e:
                continue
    
    print(f"   Generated {metrics_count} athlete-week metrics")

if __name__ == "__main__":
    if simulate_realistic_data():
        print("\n🚀 10-week simulation complete!")
        print("   Dashboard should show realistic data with mixed risk levels.")
        print("   Refresh your browser to see the changes.")
    else:
        print("\n❌ Simulation failed")
