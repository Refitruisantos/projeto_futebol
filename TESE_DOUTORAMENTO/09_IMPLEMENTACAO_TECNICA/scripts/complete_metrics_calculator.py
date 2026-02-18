#!/usr/bin/env python3
"""
Complete Metrics Calculator - All Athletes & Weeks
====================================================

This version calculates metrics for ALL athletes and ALL weeks of data.
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta
import numpy as np

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

def calculate_all_metrics():
    """Calculate metrics for all athletes and all weeks"""
    
    print("🔄 Calculating metrics for ALL athletes and weeks...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing metrics
        cursor.execute("DELETE FROM metricas_carga")
        conn.commit()
        print("   Cleared existing metrics")
        
        # Get ALL active athletes
        cursor.execute("SELECT id, nome_completo, posicao FROM atletas WHERE ativo = TRUE ORDER BY nome_completo")
        athletes = cursor.fetchall()
        print(f"   Processing ALL {len(athletes)} athletes")
        
        # Get all sessions and group by week
        cursor.execute("""
            SELECT id, data, tipo, duracao_min 
            FROM sessoes 
            ORDER BY data
        """)
        sessions = cursor.fetchall()
        
        # Group sessions by week (Monday start)
        weeks = {}
        for session in sessions:
            session_id, session_date, session_type, duration = session
            week_start = session_date - timedelta(days=session_date.weekday())
            
            if week_start not in weeks:
                weeks[week_start] = []
            weeks[week_start].append({
                'id': session_id,
                'date': session_date,
                'type': session_type,
                'duration': duration
            })
        
        print(f"   Found {len(weeks)} weeks of data")
        
        metrics_count = 0
        
        # Process each athlete
        for athlete_id, nome, posicao in athletes:
            print(f"\n   📊 {nome} ({posicao}) - ID: {athlete_id}")
            
            athlete_metrics = 0
            
            # Process each week
            for week_start, week_sessions in weeks.items():
                try:
                    # Get PSE data for this athlete and week
                    session_ids = [s['id'] for s in week_sessions]
                    
                    cursor.execute("""
                        SELECT pse, duracao_min, carga_total, sessao_id, time
                        FROM dados_pse 
                        WHERE atleta_id = %s AND sessao_id = ANY(%s)
                        ORDER BY time
                    """, (athlete_id, session_ids))
                    
                    pse_data = cursor.fetchall()
                    
                    if not pse_data:
                        continue
                    
                    # Calculate metrics
                    loads = [row[2] for row in pse_data if row[2] and row[2] > 0]
                    if not loads:
                        continue
                    
                    weekly_load = sum(loads)
                    mean_load = np.mean(loads)
                    std_load = np.std(loads)
                    monotony = mean_load / std_load if std_load > 0 else 1.0
                    strain = weekly_load * monotonia
                    
                    # ACWR calculation (simplified)
                    if len(loads) >= 3:
                        recent_loads = loads[:min(3, len(loads))]
                        chronic_loads = loads
                        acute_avg = np.mean(recent_loads)
                        chronic_avg = np.mean(chronic_loads)
                        acwr = acute_avg / chronic_avg if chronic_avg > 0 else 1.0
                    else:
                        acwr = 1.0
                    
                    # Risk assessments
                    risk_monotony_val = 'green' if monotony < 1.5 else 'yellow' if monotony < 2.0 else 'red'
                    risk_strain_val = 'green' if strain < 5000 else 'yellow' if strain < 10000 else 'red'
                    risk_acwr_val = 'green' if 0.8 <= acwr <= 1.3 else 'yellow' if 0.6 <= acwr <= 1.5 else 'red'
                    
                    # Get GPS averages
                    cursor.execute("""
                        SELECT AVG(distancia_total), AVG(velocidade_max), AVG(aceleracoes)
                        FROM dados_gps 
                        WHERE atleta_id = %s AND sessao_id = ANY(%s)
                    """, (athlete_id, session_ids))
                    
                    gps_avg = cursor.fetchone()
                    avg_distance = gps_avg[0] or 0
                    avg_speed_max = gps_avg[1] or 0
                    avg_accelerations = gps_avg[2] or 0
                    
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
                        risk_monotony_val, risk_strain_val, risk_acwr_val
                    ))
                    
                    athlete_metrics += 1
                    metrics_count += 1
                    
                except Exception as e:
                    print(f"      ⚠️ Week {week_start}: {e}")
                    continue
            
            # Commit after each athlete
            conn.commit()
            print(f"      ✅ {athlete_metrics} weeks calculated")
        
        print(f"\n✅ Total: {metrics_count} athlete-week metrics calculated")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if calculate_all_metrics():
        print("\n🚀 All athletes and weeks processed!")
        print("   Dashboard should show complete data now.")
    else:
        print("\n❌ Failed to calculate metrics")
