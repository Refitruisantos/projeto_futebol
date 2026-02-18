#!/usr/bin/env python3
"""
Calculate Weekly Metrics from Imported Data
============================================

This script calculates the advanced training load metrics from the imported
GPS and PSE data and stores them in the metricas_carga table.

Usage:
    python simple_metrics_calculator.py
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys
import numpy as np

def get_db_connection():
    """Get direct database connection"""
    try:
        # Load environment variables
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

def calculate_weekly_metrics():
    """Calculate weekly training load metrics"""
    
    print("🔄 Calculating weekly metrics...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing metrics
        cursor.execute("DELETE FROM metricas_carga")
        print("   Cleared existing metrics")
        
        # Get all athletes
        cursor.execute("SELECT id, jogador_id, nome_completo FROM atletas WHERE ativo = TRUE")
        athletes = cursor.fetchall()
        print(f"   Found {len(athletes)} active athletes")
        
        # Get all sessions grouped by week
        cursor.execute("""
            SELECT id, data, tipo, duracao_min 
            FROM sessoes 
            ORDER BY data
        """)
        sessions = cursor.fetchall()
        print(f"   Found {len(sessions)} sessions")
        
        # Group sessions by week
        weeks = {}
        for session in sessions:
            session_id, session_date, session_type, duration = session
            # Calculate week start (Monday)
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
        
        metrics_calculated = 0
        
        # Calculate metrics for each athlete and week
        for athlete_id, jogador_id, nome in athletes:
            print(f"\n   📊 Processing athlete: {nome} (ID: {athlete_id})")
            
            for week_start, week_sessions in weeks.items():
                try:
                    # Get PSE data for this athlete and week
                    session_ids = [s['id'] for s in week_sessions]
                    
                    if not session_ids:
                        continue
                    
                    cursor.execute("""
                        SELECT pse, duracao_min, carga_total, time
                        FROM dados_pse 
                        WHERE atleta_id = %s AND sessao_id = ANY(%s)
                        ORDER BY time
                    """, (athlete_id, session_ids))
                    
                    pse_data = cursor.fetchall()
                    
                    if not pse_data:
                        continue
                    
                    # Calculate weekly metrics
                    pse_values = [row[0] for row in pse_data]
                    durations = [row[1] for row in pse_data]
                    loads = [row[2] for row in pse_data]
                    
                    # Basic metrics
                    weekly_load = sum(loads)
                    mean_load = np.mean(loads) if loads else 0
                    std_load = np.std(loads) if loads else 0
                    
                    # Monotony = mean daily load / std deviation
                    monotony = mean_load / std_load if std_load > 0 else 0
                    
                    # Strain = weekly load × monotony
                    strain = weekly_load * monotony
                    
                    # ACWR (Acute:Chronic Work Ratio) - simplified
                    # Use 3-day average vs 21-day average
                    if len(pse_data) >= 7:
                        recent_loads = loads[:3]  # Last 3 sessions
                        chronic_loads = loads  # All sessions
                        acute_avg = np.mean(recent_loads) if recent_loads else 0
                        chronic_avg = np.mean(chronic_loads) if chronic_loads else 1
                        acwr = acute_avg / chronic_avg if chronic_avg > 0 else 1
                    else:
                        acwr = 1.0
                    
                    # Training days
                    training_days = len(pse_data)
                    
                    # Number of sessions
                    num_sessions = len(week_sessions)
                    
                    # Risk categories (simplified)
                    risk_monotony = 'green' if monotony < 1.5 else 'yellow' if monotony < 2.0 else 'red'
                    risk_strain = 'green' if strain < 5000 else 'yellow' if strain < 10000 else 'red'
                    risk_acwr = 'green' if 0.8 <= acwr <= 1.3 else 'yellow' if 0.6 <= acwr <= 1.5 else 'red'
                    
                    # Overall risk
                    risk_count = sum([
                        risk_monotony == 'red',
                        risk_strain == 'red', 
                        risk_acwr == 'red'
                    ])
                    risk_overall = 'green' if risk_count == 0 else 'yellow' if risk_count == 1 else 'red'
                    
                    # Get GPS averages for the week
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
                            monotonia, tensao, acwr, dias_treino, num_sessoes,
                            distancia_total_media, velocidade_max_media, aceleracoes_media,
                            risco_monotonia, risco_tensao, risco_acwr, risco_geral,
                            data_criacao
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        athlete_id, week_start, week_start + timedelta(days=6),
                        weekly_load, monotony, strain, acwr, training_days, num_sessions,
                        avg_distance, avg_speed_max, avg_accelerations,
                        risk_monotony, risk_strain, risk_acwr, risk_overall,
                        datetime.now()
                    ))
                    
                    metrics_calculated += 1
                    
                except Exception as e:
                    print(f"      ⚠️ Error calculating metrics for week {week_start}: {e}")
                    continue
        
        # Commit all changes
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ METRICS CALCULATION SUMMARY")
        print("="*60)
        print(f"   Athletes processed: {len(athletes)}")
        print(f"   Weeks analyzed: {len(weeks)}")
        print(f"   Metrics calculated: {metrics_calculated}")
        print("="*60)
        print("\n🎯 Weekly metrics successfully calculated!")
        print("\n📊 Next step: Check the dashboard")
        print("   Refresh your browser to see the data!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error calculating metrics: {str(e)}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = calculate_weekly_metrics()
    if success:
        print("\n🚀 Dashboard is now ready with data!")
    else:
        print("\n❌ Metrics calculation failed. Check error messages above.")
        sys.exit(1)
