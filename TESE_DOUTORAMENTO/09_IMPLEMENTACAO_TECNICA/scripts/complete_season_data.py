#!/usr/bin/env python3
"""
Complete Season Data - August 17 to December 14
===============================================

Generates realistic data for the full season period.
"""

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

def generate_complete_season_data():
    """Generate complete season data from Aug 17 to Dec 14"""
    
    print("🔄 GENERATING COMPLETE SEASON DATA")
    print("=" * 50)
    print("   Period: August 17 - December 14, 2025")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing data
        print("   Clearing existing data...")
        cursor.execute("DELETE FROM dados_pse")
        cursor.execute("DELETE FROM dados_gps")
        cursor.execute("DELETE FROM sessoes")
        cursor.execute("DELETE FROM metricas_carga")
        conn.commit()
        
        # Date range
        start_date = datetime(2025, 8, 17)
        end_date = datetime(2025, 12, 14)
        total_days = (end_date - start_date).days + 1
        
        print(f"   Period: {total_days} days")
        
        # Get athletes
        cursor.execute("SELECT id, nome_completo, posicao FROM atletas WHERE ativo = TRUE ORDER BY id")
        athletes = cursor.fetchall()
        print(f"   Athletes: {len(athletes)}")
        
        # Generate sessions for the entire period
        sessions = []
        current_date = start_date
        
        # Generate weekly schedule
        while current_date <= end_date:
            week_num = ((current_date - start_date).days // 7) + 1
            
            # Monday - Rest
            if current_date.weekday() == 0:
                continue
            
            # Tuesday - Training
            elif current_date.weekday() == 1:
                sessions.append({
                    'date': current_date,
                    'type': 'treino',
                    'week': week_num,
                    'day_num': 2
                })
            
            # Wednesday - Training
            elif current_date.weekday() == 2:
                sessions.append({
                    'date': current_date,
                    'type': 'treino',
                    'week': week_num,
                    'day_num': 3
                })
            
            # Thursday - Training
            elif current_date.weekday() == 3:
                sessions.append({
                    'date': current_date,
                    'type': 'treino',
                    'week': week_num,
                    'day_num': 4
                })
            
            # Friday - Light Training or Game
            elif current_date.weekday() == 4:
                # Every other Friday is a game
                if week_num % 2 == 1:
                    sessions.append({
                        'date': current_date,
                        'type': 'jogo',
                        'week': week_num,
                        'day_num': 5
                    })
                else:
                    sessions.append({
                        'date': current_date,
                        'type': 'treino',
                        'week': week_num,
                        'day_num': 5
                    })
            
            # Saturday - Game or Rest
            elif current_date.weekday() == 5:
                if week_num % 2 == 0:  # Alternate with Friday
                    sessions.append({
                        'date': current_date,
                        'type': 'jogo',
                        'week': week_num,
                        'day_num': 6
                    })
            
            # Sunday - Rest
            elif current_date.weekday() == 6:
                continue
            
            current_date += timedelta(days=1)
        
        print(f"   Generated {len(sessions)} sessions")
        
        # Generate opponents for games
        opponents = [
            {"name": "Sporting CP", "difficulty": 9.5, "league_pos": 2, "form": "WWWWW"},
            {"name": "FC Porto", "difficulty": 9.3, "league_pos": 1, "form": "WWLWW"},
            {"name": "Benfica", "difficulty": 9.1, "league_pos": 3, "form": "WLWWW"},
            {"name": "Braga", "difficulty": 7.8, "league_pos": 4, "form": "WWLWL"},
            {"name": "Vitória SC", "difficulty": 6.5, "league_pos": 5, "form": "LWWLW"},
            {"name": "Moreirense", "difficulty": 5.2, "league_pos": 8, "form": "WLLWL"},
            {"name": "Famalicão", "difficulty": 4.8, "league_pos": 10, "form": "LDLWL"},
            {"name": "Gil Vicente", "difficulty": 4.5, "league_pos": 12, "form": "DLLLD"},
            {"name": "Portimonense", "difficulty": 3.8, "league_pos": 14, "form": "LDLLD"},
            {"name": "Estoril", "difficulty": 3.2, "league_pos": 16, "form": "DLLDL"},
            {"name": "Arouca", "difficulty": 4.0, "league_pos": 11, "form": "LDWLL"},
            {"name": "Boavista", "difficulty": 5.5, "league_pos": 7, "form": "WLWLD"},
            {"name": "Casa Pia", "difficulty": 3.5, "league_pos": 15, "form": "DDLLD"},
            {"name": "Estrela Amadora", "difficulty": 3.0, "league_pos": 17, "form": "LDLDL"},
            {"name": "Farense", "difficulty": 2.8, "league_pos": 18, "form": "DLLDL"}
        ]
        
        # Insert sessions
        game_count = 0
        for session in sessions:
            if session['type'] == 'jogo':
                opponent = opponents[game_count % len(opponents)]
                game_count += 1
                
                # Generate scientific score
                base_score = 50 + (opponent['difficulty'] * 5)
                performance_modifier = random.uniform(-10, 15)
                scientific_score = base_score + performance_modifier
                
                cursor.execute("""
                    INSERT INTO sessoes (data, tipo, adversario, local, resultado, competicao, jornada, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    session['date'],
                    'jogo',
                    opponent['name'],
                    random.choice(['casa', 'fora']),
                    f"{random.randint(0,4)}-{random.randint(0,4)}",
                    "Liga Portugal",
                    game_count,
                    f"Difficulty: {opponent['difficulty']}/10 | Scientific Score: {scientific_score:.1f} | Form: {opponent['form']}"
                ))
            else:
                cursor.execute("""
                    INSERT INTO sessoes (data, tipo, local, observacoes)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    session['date'],
                    'treino',
                    'casa',
                    f"Week {session['week']} - Day {session['day_num']}"
                ))
            
            session_id = cursor.fetchone()[0]
            session['id'] = session_id
        
        conn.commit()
        print(f"   ✅ Sessions inserted")
        
        # Generate PSE and GPS data for each session
        pse_count = 0
        gps_count = 0
        
        for session in sessions:
            for athlete_id, nome, posicao in athletes:
                # Position-based PSE values
                if posicao == 'GR':
                    base_pse = 3.5
                    base_duration = 90
                elif posicao in ['DC', 'DL']:
                    base_pse = 5.5
                    base_duration = 95
                elif posicao == 'MC':
                    base_pse = 6.5
                    base_duration = 100
                elif posicao in ['EX', 'AV']:
                    base_pse = 7.0
                    base_duration = 105
                else:
                    base_pse = 5.0
                    base_duration = 90
                
                # Add variation
                pse_variation = random.uniform(-1.5, 1.5)
                duration_variation = random.uniform(-10, 10)
                
                pse_value = max(1, min(10, base_pse + pse_variation))
                duration = max(60, base_duration + duration_variation)
                pse_load = pse_value * duration
                
                # Insert PSE data
                cursor.execute("""
                    INSERT INTO dados_pse (atleta_id, sessao_id, pse, duration, carga_total, time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    athlete_id, session['id'], pse_value, duration, pse_load, session['date']
                ))
                pse_count += 1
                
                # Insert GPS data
                if session['type'] == 'jogo':
                    distance = random.uniform(8000, 12000)
                    speed_max = random.uniform(25, 35)
                    accelerations = random.uniform(20, 40)
                    sprints = random.uniform(15, 30)
                else:
                    distance = random.uniform(4000, 8000)
                    speed_max = random.uniform(20, 30)
                    accelerations = random.uniform(10, 25)
                    sprints = random.uniform(5, 15)
                
                cursor.execute("""
                    INSERT INTO dados_gps (atleta_id, sessao_id, distancia_total, velocidade_max, aceleracoes, sprints, time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    athlete_id, session['id'], distance, speed_max, accelerations, sprints, session['date']
                ))
                gps_count += 1
        
        conn.commit()
        print(f"   ✅ PSE data: {pse_count} records")
        print(f"   ✅ GPS data: {gps_count} records")
        
        # Calculate weekly metrics
        print("   Calculating weekly metrics...")
        
        for week_num in range(1, 19):  # 18 weeks
            week_start = start_date + timedelta(days=(week_num-1)*7)
            week_end = week_start + timedelta(days=6)
            
            for athlete_id, nome, posicao in athletes:
                # Get PSE data for this athlete and week
                cursor.execute("""
                    SELECT carga_total, time
                    FROM dados_pse 
                    WHERE atleta_id = %s AND DATE(time) >= %s AND DATE(time) <= %s
                    ORDER BY time
                """, (athlete_id, week_start, week_end))
                
                pse_data = cursor.fetchall()
                
                if len(pse_data) >= 3:  # Minimum sessions for metrics
                    loads = [row[0] for row in pse_data]
                    
                    weekly_load = sum(loads)
                    mean_load = np.mean(loads)
                    std_load = np.std(loads)
                    
                    if std_load < 50:
                        std_load = 50
                    
                    monotony = mean_load / std_load
                    strain = weekly_load * monotony
                    
                    # Realistic ACWR with progression
                    base_acwr = 1.0 + (week_num * 0.02)  # Slight increase over season
                    acwr = base_acwr + random.uniform(-0.2, 0.2)
                    acwr = max(0.5, min(2.0, acwr))
                    
                    # Risk assessment
                    risk_monotony = 'green' if monotony < 2.0 else 'yellow' if monotony < 3.0 else 'red'
                    risk_strain = 'green' if strain < 8000 else 'yellow' if strain < 12000 else 'red'
                    risk_acwr = 'green' if 0.8 <= acwr <= 1.5 else 'yellow' if 0.6 <= acwr <= 1.8 else 'red'
                    
                    # Get GPS averages
                    cursor.execute("""
                        SELECT AVG(distancia_total), AVG(velocidade_max), AVG(aceleracoes)
                        FROM dados_gps 
                        WHERE atleta_id = %s AND DATE(time) >= %s AND DATE(time) <= %s
                    """, (athlete_id, week_start, week_end))
                    
                    gps_avg = cursor.fetchone()
                    avg_distance = gps_avg[0] or 5000
                    avg_speed = gps_avg[1] or 25
                    avg_accelerations = gps_avg[2] or 15
                    
                    # Insert metrics
                    cursor.execute("""
                        INSERT INTO metricas_carga (
                            atleta_id, semana_inicio, semana_fim, carga_total_semanal,
                            media_carga, desvio_padrao, dias_treino, monotonia, tensao, acwr,
                            carga_aguda, carga_cronica, variacao_percentual,
                            z_score_carga, z_score_monotonia, z_score_tensao, z_score_acwr,
                            nivel_risco_monotonia, nivel_risco_tensao, nivel_risco_acwr,
                            distancia_total_media, velocidade_max_media, aceleracoes_media, high_speed_distance
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        athlete_id, week_start, week_end,
                        weekly_load, mean_load, std_load, len(pse_data),
                        monotony, strain, acwr, weekly_load, weekly_load * 4, 0.0,
                        0.0, 0.0, 0.0, 0.0,
                        risk_monotony, risk_strain, risk_acwr,
                        avg_distance, avg_speed, avg_accelerations, avg_distance * 0.15
                    ))
        
        conn.commit()
        print(f"   ✅ Weekly metrics calculated")
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM sessoes")
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sessoes WHERE tipo = 'jogo'")
        total_games = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM metricas_carga")
        total_metrics = cursor.fetchone()[0]
        
        print(f"\n📊 COMPLETE SEASON SUMMARY:")
        print(f"   Period: August 17 - December 14, 2025")
        print(f"   Duration: 18 weeks")
        print(f"   Total Sessions: {total_sessions}")
        print(f"   Games: {total_games}")
        print(f"   Weekly Metrics: {total_metrics}")
        print(f"   PSE Records: {pse_count}")
        print(f"   GPS Records: {gps_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if generate_complete_season_data():
        print("\n🎉 COMPLETE SEASON DATA READY!")
        print("   ✅ August 17 - December 14, 2025")
        print("   ✅ 18 weeks of training and games")
        print("   ✅ Realistic opponent data")
        print("   ✅ Complete metrics for all weeks")
        print("\n📊 Refresh your browser for the complete season data!")
    else:
        print("\n❌ Failed to generate season data")
