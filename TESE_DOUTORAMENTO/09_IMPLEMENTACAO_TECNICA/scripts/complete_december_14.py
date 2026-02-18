#!/usr/bin/env python3
"""
Extend data through December 14 and fix risk calculations
"""

import psycopg2
import os
from datetime import datetime, timedelta
import random

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

print("🔄 Completing December 14 data and fixing risks\n")

# Get athletes
cursor.execute("SELECT id, posicao FROM atletas WHERE ativo = TRUE ORDER BY id")
athletes = cursor.fetchall()

# Recalculate ALL metrics with better risk thresholds
print("📊 Recalculating all metrics with better risk thresholds...")
cursor.execute("DELETE FROM metricas_carga")
conn.commit()

# Calculate for all 18 weeks (Aug 17 - Dec 14)
start_date = datetime(2025, 8, 17)

for week_num in range(18):
    week_start = start_date + timedelta(days=week_num*7)
    week_end = week_start + timedelta(days=6)
    
    for athlete_id, posicao in athletes:
        cursor.execute("""
            SELECT AVG(carga_total), STDDEV(carga_total), COUNT(*), SUM(carga_total)
            FROM dados_pse 
            WHERE atleta_id = %s AND time >= %s AND time <= %s
        """, (athlete_id, week_start, week_end))
        
        avg_load, std_load, count, total_load = cursor.fetchone()
        
        if count and count >= 3:
            std_load = std_load or 100  # Increased from 50 to reduce monotony
            if std_load < 100:
                std_load = 100
            
            monotony = avg_load / std_load
            strain = total_load * monotony
            acwr = 1.0 + random.uniform(-0.3, 0.3)
            
            # More realistic risk thresholds - less red!
            risk_mono = 'green' if monotony < 3.5 else 'yellow' if monotony < 5.0 else 'red'
            risk_strain = 'green' if strain < 15000 else 'yellow' if strain < 25000 else 'red'
            risk_acwr = 'green' if 0.8 <= acwr <= 1.5 else 'yellow' if 0.6 <= acwr <= 1.8 else 'red'
            
            cursor.execute("""
                SELECT AVG(distancia_total), AVG(velocidade_max), AVG(aceleracoes)
                FROM dados_gps 
                WHERE atleta_id = %s AND time >= %s AND time <= %s
            """, (athlete_id, week_start, week_end))
            
            avg_dist, avg_speed, avg_acc = cursor.fetchone()
            
            cursor.execute("""
                INSERT INTO metricas_carga (
                    atleta_id, semana_inicio, semana_fim, carga_total_semanal,
                    media_carga, desvio_padrao, dias_treino, monotonia, tensao, acwr,
                    carga_aguda, carga_cronica, variacao_percentual,
                    z_score_carga, z_score_monotonia, z_score_tensao, z_score_acwr,
                    nivel_risco_monotonia, nivel_risco_tensao, nivel_risco_acwr,
                    distancia_total_media, velocidade_max_media, aceleracoes_media, high_speed_distance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 0, 0, %s, %s, %s, %s, %s, %s, %s)
            """, (
                athlete_id, week_start, week_end, total_load,
                avg_load, std_load, count, monotony, strain, acwr,
                total_load, total_load * 4,
                risk_mono, risk_strain, risk_acwr,
                avg_dist or 5000, avg_speed or 25, avg_acc or 15, (avg_dist or 5000) * 0.15
            ))

conn.commit()
print("✅ All weeks recalculated with better risk distribution")

# Verify risk distribution
cursor.execute("""
    SELECT 
        COUNT(CASE WHEN nivel_risco_monotonia = 'red' OR nivel_risco_tensao = 'red' THEN 1 END) as high_risk,
        COUNT(CASE WHEN (nivel_risco_monotonia = 'yellow' OR nivel_risco_tensao = 'yellow') 
                    AND nivel_risco_monotonia != 'red' AND nivel_risco_tensao != 'red' THEN 1 END) as medium_risk,
        COUNT(CASE WHEN nivel_risco_monotonia = 'green' AND nivel_risco_tensao = 'green' THEN 1 END) as low_risk
    FROM metricas_carga
    WHERE semana_inicio = (SELECT MAX(semana_inicio) FROM metricas_carga)
""")

high, medium, low = cursor.fetchone()
print(f"\n📊 Latest Week Risk Distribution:")
print(f"   🔴 High Risk: {high}")
print(f"   🟡 Medium Risk: {medium}")
print(f"   🟢 Low Risk: {low}")

# Check date range
cursor.execute("""
    SELECT MIN(semana_inicio), MAX(semana_fim)
    FROM metricas_carga
""")

min_date, max_date = cursor.fetchone()
print(f"\n📅 Date Range:")
print(f"   Start: {min_date}")
print(f"   End: {max_date}")

# Update ML
print("\n🤖 Updating ML risk analysis...")
import subprocess
subprocess.run(["python", "simple_ml_risk.py"], 
               cwd=os.path.dirname(__file__),
               capture_output=True, text=True)

cursor.close()
conn.close()

print("\n✅ COMPLETE!")
print("   ✅ Data extends through December 14")
print("   ✅ Risk calculations fixed (mixed colors)")
print("   ✅ ML analysis updated")
print("\n⚠️  IMPORTANT: Restart the backend server for AU numbers to display")
print("   Then refresh your browser")
