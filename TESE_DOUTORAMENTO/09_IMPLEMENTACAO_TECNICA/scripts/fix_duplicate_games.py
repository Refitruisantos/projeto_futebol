#!/usr/bin/env python3
"""
Fix Duplicate Game Sessions
============================
Remove duplicate games and create realistic unique opponents for each round.
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

print("🔄 Fixing Duplicate Game Sessions\n")

# Portuguese league teams (Primeira Liga)
OPPONENTS = [
    "Sporting CP", "FC Porto", "SL Benfica", "SC Braga",
    "Vitória SC", "Gil Vicente", "Rio Ave", "Casa Pia",
    "Estoril Praia", "Portimonense", "Arouca", "Boavista",
    "Famalicão", "Vizela", "Chaves", "Estrela Amadora"
]

# Delete all games first
print("🗑️  Removing old game sessions...")
cursor.execute("""
    DELETE FROM dados_gps WHERE sessao_id IN (SELECT id FROM sessoes WHERE tipo = 'jogo')
""")
cursor.execute("""
    DELETE FROM dados_pse WHERE sessao_id IN (SELECT id FROM sessoes WHERE tipo = 'jogo')
""")
cursor.execute("""
    DELETE FROM sessoes WHERE tipo = 'jogo'
""")
conn.commit()
print("✅ Old games removed")

# Get athletes
cursor.execute("SELECT id, posicao FROM atletas WHERE ativo = TRUE ORDER BY id")
athletes = cursor.fetchall()

# Create realistic game schedule: ~1 game per week from Aug 17 to Dec 14
print("\n⚽ Creating realistic game schedule...")

start_date = datetime(2025, 8, 17)
end_date = datetime(2025, 12, 14)
current_date = start_date

games_created = []
round_num = 1
opponent_index = 0

while current_date <= end_date:
    # Skip some weeks (not every week has a game)
    if random.random() < 0.65:  # ~65% chance of game each week
        # Games typically on Saturday
        game_date = current_date + timedelta(days=(5 - current_date.weekday()) % 7)
        
        # Ensure we don't go past end date
        if game_date > end_date:
            break
        
        # Alternate home/away
        local = 'casa' if round_num % 2 == 1 else 'fora'
        
        # Get unique opponent
        opponent = OPPONENTS[opponent_index % len(OPPONENTS)]
        opponent_index += 1
        
        # Generate realistic score
        if local == 'casa':
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 3)
        else:
            home_score = random.randint(0, 3)
            away_score = random.randint(0, 4)
        
        resultado = f"{home_score}-{away_score}"
        
        # Create session
        cursor.execute("""
            INSERT INTO sessoes (data, tipo, local, adversario, jornada, resultado, observacoes)
            VALUES (%s, 'jogo', %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            game_date,
            local,
            opponent,
            round_num,
            resultado,
            f"Round {round_num} vs {opponent}"
        ))
        
        session_id = cursor.fetchone()[0]
        games_created.append((session_id, game_date, opponent, round_num, resultado))
        
        round_num += 1
    
    # Move to next week
    current_date += timedelta(days=7)

conn.commit()
print(f"✅ Created {len(games_created)} unique games")

# Add PSE and GPS data for each game
print("\n📊 Adding performance data for games...")

pse_count = 0
gps_count = 0

for session_id, game_date, opponent, round_num, resultado in games_created:
    for athlete_id, posicao in athletes:
        # Game intensity is higher than training
        base_pse = {'GR': 5.0, 'DC': 7.0, 'DL': 7.5, 'MC': 8.0, 'EX': 8.5, 'AV': 8.5}.get(posicao, 7.0)
        pse = max(1, min(10, base_pse + random.uniform(-1.0, 1.0)))
        duracao_min = int(random.choice([90, 90, 90, 60, 45, 30]))  # Some players play less
        load = pse * duracao_min
        
        cursor.execute("""
            INSERT INTO dados_pse (atleta_id, sessao_id, pse, duracao_min, carga_total, time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (athlete_id, session_id, pse, duracao_min, load, game_date))
        pse_count += 1
        
        # GPS data - higher values for games
        dist = 9000 + random.uniform(-2000, 2000)
        speed = 30 + random.uniform(-5, 5)
        acc = 25 + random.uniform(-5, 5)
        spr = 15 + random.uniform(-5, 5)
        
        cursor.execute("""
            INSERT INTO dados_gps (atleta_id, sessao_id, distancia_total, velocidade_max, aceleracoes, sprints, time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (athlete_id, session_id, dist, speed, acc, int(spr), game_date))
        gps_count += 1

conn.commit()
print(f"✅ Added {pse_count} PSE records and {gps_count} GPS records")

# Recalculate metrics
print("\n📈 Recalculating weekly metrics...")
cursor.execute("DELETE FROM metricas_carga")
conn.commit()

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
            std_load = std_load or 100
            if std_load < 100:
                std_load = 100
            
            monotony = avg_load / std_load
            strain = total_load * monotony
            acwr = 1.0 + random.uniform(-0.3, 0.3)
            
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
print("✅ Metrics recalculated")

# Show sample of games
print("\n⚽ SAMPLE GAME SCHEDULE:")
print(f"{'Date':<12} | {'Opponent':<20} | {'Round':<6} | {'Score':<6} | {'Location'}")
print("-" * 70)
for _, game_date, opponent, round_num, resultado in games_created[:10]:
    local = 'Home' if games_created.index((_, game_date, opponent, round_num, resultado)) % 2 == 0 else 'Away'
    print(f"{game_date.strftime('%Y-%m-%d'):<12} | {opponent:<20} | {round_num:<6} | {resultado:<6} | {local}")

print(f"\n✅ COMPLETE!")
print(f"   Total unique games: {len(games_created)}")
print(f"   Date range: {games_created[0][1].strftime('%Y-%m-%d')} to {games_created[-1][1].strftime('%Y-%m-%d')}")
print(f"   Unique opponents used: {len(set([g[2] for g in games_created]))}")

cursor.close()
conn.close()

print("\n📊 Refresh your browser to see the corrected sessions!")
