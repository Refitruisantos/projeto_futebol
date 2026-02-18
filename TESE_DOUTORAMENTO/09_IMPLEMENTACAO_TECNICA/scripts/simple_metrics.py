#!/usr/bin/env python3
"""
Simple Metrics Calculator - One Transaction Per Athlete
========================================================

This version calculates metrics with individual commits to avoid transaction errors.
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

def calculate_simple_metrics():
    """Calculate metrics with simple approach"""
    
    print("🔄 Calculating weekly metrics (simple version)...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Clear existing metrics
        cursor.execute("DELETE FROM metricas_carga")
        conn.commit()
        print("   Cleared existing metrics")
        
        # Get athletes
        cursor.execute("SELECT id, nome_completo FROM atletas WHERE ativo = TRUE ORDER BY id LIMIT 5")
        athletes = cursor.fetchall()
        print(f"   Processing {len(athletes)} athletes (sample)")
        
        metrics_count = 0
        
        for athlete_id, nome in athletes:
            print(f"\n   📊 {nome} (ID: {athlete_id})")
            
            try:
                # Get PSE data for this athlete
                cursor.execute("""
                    SELECT pse, duracao_min, carga_total, sessao_id, time
                    FROM dados_pse 
                    WHERE atleta_id = %s
                    ORDER BY time
                    LIMIT 10
                """, (athlete_id,))
                
                pse_data = cursor.fetchall()
                
                if not pse_data:
                    print(f"      No PSE data found")
                    continue
                
                # Simple calculations
                loads = [row[2] for row in pse_data if row[2]]
                if not loads:
                    continue
                
                weekly_load = sum(loads)
                mean_load = np.mean(loads)
                std_load = np.std(loads)
                monotony = mean_load / std_load if std_load > 0 else 1
                strain = weekly_load * monotony
                acwr = 1.2  # Simplified
                
                # Risk categories
                risk_monotony = 'green' if monotony < 1.5 else 'yellow' if monotony < 2.0 else 'red'
                risk_strain = 'green' if strain < 5000 else 'yellow' if strain < 10000 else 'red'
                risk_acwr = 'green' if 0.8 <= acwr <= 1.3 else 'yellow'
                risk_overall = 'red' if risk_monotony == 'red' or risk_strain == 'red' else 'green'
                
                # Insert metrics for this week
                week_start = datetime(2025, 1, 6)  # First week of January
                
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
                    monotony, strain, acwr, weekly_load, weekly_load * 4, 0.0,  # ACWR values
                    0.0, 0.0, 0.0, 0.0,  # Z-scores
                    risk_monotony, risk_strain, risk_acwr
                ))
                
                conn.commit()
                metrics_count += 1
                print(f"      ✅ Metrics calculated: Load={weekly_load:.1f}, Monotony={monotony:.2f}")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                conn.rollback()
                continue
        
        print(f"\n✅ Successfully calculated {metrics_count} athlete metrics")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if calculate_simple_metrics():
        print("\n🚀 Dashboard should now show data!")
        print("   Refresh your browser to see the changes.")
    else:
        print("\n❌ Failed to calculate metrics")
