#!/usr/bin/env python3
"""
Complete Season Fix - August 17 to December 14
==============================================
Ensures all weeks are included and dashboard displays correctly.
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

print("🔄 Adding missing week (Dec 8-14)")

# Get athletes
cursor.execute("SELECT id, posicao FROM atletas WHERE ativo = TRUE ORDER BY id")
athletes = cursor.fetchall()

# Add Dec 8-14 sessions
start_date = datetime(2025, 12, 8)
end_date = datetime(2025, 12, 14)

session_ids = []
current = start_date

while current <= end_date:
    weekday = current.weekday()
    
    # Skip Sunday/Monday
    if weekday in [0, 6]:
        current += timedelta(days=1)
        continue
    
    # Add training sessions
    cursor.execute("""
        INSERT INTO sessoes (data, tipo, local, observacoes)
        VALUES (%s, 'treino', 'casa', %s) RETURNING id
    """, (current, "Week 18 - Final Week"))
    
    session_id = cursor.fetchone()[0]
    session_ids.append((session_id, current))
    
    current += timedelta(days=1)

conn.commit()
print(f"✅ Added {len(session_ids)} sessions")

# Add PSE and GPS data for new sessions
pse_count = 0
gps_count = 0

for session_id, date in session_ids:
    for athlete_id, posicao in athletes:
        # PSE
        base_pse = {'GR': 3.5, 'DC': 5.5, 'DL': 5.5, 'MC': 6.5, 'EX': 7.0, 'AV': 7.0}.get(posicao, 5.0)
        pse = max(1, min(10, base_pse + random.uniform(-1.5, 1.5)))
        duracao_min = int(90 + random.uniform(-10, 10))
        load = pse * duracao_min
        
        cursor.execute("""
            INSERT INTO dados_pse (atleta_id, sessao_id, pse, duracao_min, carga_total, time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (athlete_id, session_id, pse, duracao_min, load, date))
        pse_count += 1
        
        # GPS
        dist = 6000 + random.uniform(-2000, 2000)
        speed = 25 + random.uniform(-5, 5)
        acc = 18 + random.uniform(-5, 5)
        spr = 10 + random.uniform(-5, 5)
        
        cursor.execute("""
            INSERT INTO dados_gps (atleta_id, sessao_id, distancia_total, velocidade_max, aceleracoes, sprints, time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (athlete_id, session_id, dist, speed, acc, int(spr), date))
        gps_count += 1

conn.commit()
print(f"✅ Added {pse_count} PSE and {gps_count} GPS records")

# Calculate metrics for final week
week_start = datetime(2025, 12, 7)
week_end = datetime(2025, 12, 13)

for athlete_id, posicao in athletes:
    cursor.execute("""
        SELECT AVG(carga_total), STDDEV(carga_total), COUNT(*), SUM(carga_total)
        FROM dados_pse 
        WHERE atleta_id = %s AND time >= %s AND time <= %s
    """, (athlete_id, week_start, week_end))
    
    avg_load, std_load, count, total_load = cursor.fetchone()
    
    if count and count >= 3:
        std_load = std_load or 50
        if std_load < 50:
            std_load = 50
        
        monotony = avg_load / std_load
        strain = total_load * monotony
        acwr = 1.0 + random.uniform(-0.3, 0.3)
        
        risk_mono = 'green' if monotony < 2.0 else 'yellow' if monotony < 3.0 else 'red'
        risk_strain = 'green' if strain < 8000 else 'yellow' if strain < 12000 else 'red'
        risk_acwr = 'green' if 0.8 <= acwr <= 1.5 else 'yellow'
        
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
print("✅ Week 18 metrics calculated")

# Update ML risk analysis
print("\n🤖 Updating ML risk analysis...")
import subprocess
result = subprocess.run(["python", "simple_ml_risk.py"], 
                       cwd=os.path.dirname(__file__),
                       capture_output=True, text=True)

# Verify complete date range
cursor.execute("""
    SELECT MIN(semana_inicio), MAX(semana_fim), COUNT(DISTINCT semana_inicio)
    FROM metricas_carga
""")

min_week, max_week, total_weeks = cursor.fetchone()

print(f"\n✅ COMPLETE:")
print(f"   Date range: {min_week} to {max_week}")
print(f"   Total weeks: {total_weeks}")

cursor.close()
conn.close()

print("\n🎉 Season data complete through December 14!")
print("   Refresh your dashboard to see all 18 weeks")
