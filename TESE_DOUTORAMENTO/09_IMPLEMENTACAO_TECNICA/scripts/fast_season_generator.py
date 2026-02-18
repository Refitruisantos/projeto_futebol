#!/usr/bin/env python3
"""
Fast Season Generator - Optimized for Speed
==========================================
Generates August 17 - December 14 data quickly using batch inserts.
"""

import psycopg2
import os
from datetime import datetime, timedelta
import random

def get_db_connection():
    try:
        load_dotenv = __import__('dotenv').load_dotenv
        load_dotenv()
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5433'),
            database=os.getenv('DB_NAME', 'futebol_tese'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'desporto.20')
        )
    except:
        return psycopg2.connect(
            host='localhost', port='5433', database='futebol_tese',
            user='postgres', password='desporto.20'
        )

print("🚀 Fast Season Generator")
print("Period: August 17 - December 14, 2025\n")

conn = get_db_connection()
cursor = conn.cursor()

# Get athletes
cursor.execute("SELECT id, posicao FROM atletas WHERE ativo = TRUE ORDER BY id")
athletes = cursor.fetchall()
print(f"✅ {len(athletes)} athletes loaded")

# Generate date range
start = datetime(2025, 8, 17)
end = datetime(2025, 12, 14)
dates = []
current = start

opponents = [
    "Sporting CP", "FC Porto", "Benfica", "Braga", "Vitória SC",
    "Moreirense", "Famalicão", "Gil Vicente", "Portimonense", "Estoril",
    "Arouca", "Boavista", "Casa Pia", "Estrela", "Farense"
]

game_num = 0
while current <= end:
    week = ((current - start).days // 7) + 1
    weekday = current.weekday()
    
    # Skip Sunday/Monday
    if weekday in [0, 6]:
        current += timedelta(days=1)
        continue
    
    # Friday/Saturday = games (alternating weeks)
    if weekday in [4, 5] and week % 2 == (1 if weekday == 4 else 0):
        dates.append((current, 'jogo', week, game_num))
        game_num += 1
    elif weekday in [1, 2, 3, 4]:  # Training days
        dates.append((current, 'treino', week, None))
    
    current += timedelta(days=1)

print(f"✅ {len(dates)} sessions planned")

# Batch insert sessions
session_ids = []
for date, tipo, week, game_idx in dates:
    if tipo == 'jogo' and game_idx is not None:
        opp = opponents[game_idx % len(opponents)]
        cursor.execute("""
            INSERT INTO sessoes (data, tipo, adversario, local, resultado, competicao, jornada, observacoes)
            VALUES (%s, 'jogo', %s, %s, %s, 'Liga Portugal', %s, %s) RETURNING id
        """, (date, opp, random.choice(['casa', 'fora']), f"{random.randint(0,3)}-{random.randint(0,3)}", 
              game_idx + 1, f"Round {game_idx + 1} vs {opp}"))
    else:
        cursor.execute("""
            INSERT INTO sessoes (data, tipo, local, observacoes)
            VALUES (%s, 'treino', 'casa', %s) RETURNING id
        """, (date, f"Week {week}"))
    
    session_ids.append((cursor.fetchone()[0], date, tipo, week))

conn.commit()
print(f"✅ {len(session_ids)} sessions inserted")

# Batch insert PSE and GPS data
print("⏳ Generating athlete data...")
pse_values = []
gps_values = []

for session_id, date, tipo, week in session_ids:
    for athlete_id, posicao in athletes:
        # PSE data
        base_pse = {'GR': 3.5, 'DC': 5.5, 'DL': 5.5, 'MC': 6.5, 'EX': 7.0, 'AV': 7.0}.get(posicao, 5.0)
        pse = max(1, min(10, base_pse + random.uniform(-1.5, 1.5)))
        duracao_min = int(90 + random.uniform(-10, 10))
        load = pse * duracao_min
        
        pse_values.append((athlete_id, session_id, pse, duracao_min, load, date))
        
        # GPS data
        if tipo == 'jogo':
            dist, speed, acc, spr = 10000, 30, 30, 20
        else:
            dist, speed, acc, spr = 6000, 25, 18, 10
        
        dist += random.uniform(-2000, 2000)
        speed += random.uniform(-5, 5)
        acc += random.uniform(-5, 5)
        spr += random.uniform(-5, 5)
        
        gps_values.append((athlete_id, session_id, dist, speed, acc, spr, date))

# Batch insert
cursor.executemany("""
    INSERT INTO dados_pse (atleta_id, sessao_id, pse, duracao_min, carga_total, time)
    VALUES (%s, %s, %s, %s, %s, %s)
""", pse_values)

cursor.executemany("""
    INSERT INTO dados_gps (atleta_id, sessao_id, distancia_total, velocidade_max, aceleracoes, sprints, time)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", gps_values)

conn.commit()
print(f"✅ {len(pse_values)} PSE records")
print(f"✅ {len(gps_values)} GPS records")

# Calculate weekly metrics
print("⏳ Calculating metrics...")
for week in range(1, 19):
    week_start = start + timedelta(days=(week-1)*7)
    week_end = week_start + timedelta(days=6)
    
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
print("✅ Weekly metrics calculated")

# Run ML risk analysis
cursor.execute("SELECT COUNT(*) FROM metricas_carga")
metrics_count = cursor.fetchone()[0]

print(f"\n📊 COMPLETE:")
print(f"   Sessions: {len(session_ids)}")
print(f"   Games: {game_num}")
print(f"   PSE: {len(pse_values)}")
print(f"   GPS: {len(gps_values)}")
print(f"   Metrics: {metrics_count}")

cursor.close()
conn.close()

print("\n🎉 Season data ready! Running ML risk analysis...")

# Run ML analysis
import subprocess
subprocess.run(["python", "simple_ml_risk.py"], cwd=os.path.dirname(__file__))
