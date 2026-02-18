#!/usr/bin/env python3
"""Create simulation data using correct column names from existing table"""

import psycopg2
import random
import numpy as np
from datetime import datetime, date, timedelta
import os

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

print("🏗️ Criando dados de simulação completos com colunas corretas...")

# 1. Add deceleration columns to GPS data if not exists
print("\n1️⃣ Adicionando colunas de desaceleração aos dados GPS...")
try:
    cursor.execute("""
        ALTER TABLE dados_gps 
        ADD COLUMN IF NOT EXISTS num_desaceleracoes_altas INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS desaceleracao_maxima DECIMAL(5,2) DEFAULT 0.0,
        ADD COLUMN IF NOT EXISTS desaceleracao_media DECIMAL(5,2) DEFAULT 0.0
    """)
    print("   ✅ Colunas de desaceleração adicionadas")
except Exception as e:
    print(f"   ⚠️ Erro ao adicionar colunas: {e}")

# 2. Update existing GPS data with deceleration values
print("\n2️⃣ Atualizando dados GPS existentes com desacelerações...")
cursor.execute("SELECT atleta_id, sessao_id FROM dados_gps LIMIT 100")  # Limit for faster execution
gps_records = cursor.fetchall()

for record in gps_records:
    atleta_id, sessao_id = record
    
    # Generate realistic deceleration data
    num_high_decel = random.randint(15, 45)
    max_decel = round(random.uniform(3.5, 8.2), 2)
    avg_decel = round(random.uniform(1.8, 3.5), 2)
    
    cursor.execute("""
        UPDATE dados_gps 
        SET num_desaceleracoes_altas = %s,
            desaceleracao_maxima = %s,
            desaceleracao_media = %s
        WHERE atleta_id = %s AND sessao_id = %s
    """, (num_high_decel, max_decel, avg_decel, atleta_id, sessao_id))

print(f"   ✅ {len(gps_records)} registros GPS atualizados com dados de desaceleração")

# 3. Enhanced wellness data with detailed sleep tracking
print("\n3️⃣ Melhorando dados de wellness com rastreamento detalhado do sono...")

# Add sleep tracking columns if not exists
try:
    cursor.execute("""
        ALTER TABLE dados_wellness 
        ADD COLUMN IF NOT EXISTS tempo_cama TIME,
        ADD COLUMN IF NOT EXISTS tempo_adormecer TIME,
        ADD COLUMN IF NOT EXISTS num_despertares INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS eficiencia_sono DECIMAL(5,2) DEFAULT 0.0,
        ADD COLUMN IF NOT EXISTS sono_profundo_min INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS sono_rem_min INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS ranking_wellness INTEGER DEFAULT 1
    """)
    print("   ✅ Colunas de sono detalhado adicionadas")
except Exception as e:
    print(f"   ⚠️ Erro ao adicionar colunas de sono: {e}")

# Update wellness records with detailed sleep data (limit for faster execution)
cursor.execute("SELECT id, sleep_hours, wellness_score FROM dados_wellness LIMIT 100")
wellness_records = cursor.fetchall()

for record in wellness_records:
    wellness_id, sleep_hours, wellness_score = record
    
    # Generate realistic sleep data with proper time format
    bedtime_hour = random.randint(22, 23)
    bedtime_min = random.randint(0, 59)
    bedtime = f"{bedtime_hour:02d}:{bedtime_min:02d}:00"
    
    sleep_onset_delay = random.randint(5, 30)
    total_bedtime_min = bedtime_hour * 60 + bedtime_min + sleep_onset_delay
    
    if total_bedtime_min >= 24 * 60:
        total_bedtime_min -= 24 * 60
    
    sleep_onset_hour = total_bedtime_min // 60
    sleep_onset_min = total_bedtime_min % 60
    sleep_onset = f"{sleep_onset_hour:02d}:{sleep_onset_min:02d}:00"
    
    num_awakenings = random.randint(0, 4)
    sleep_efficiency = round(random.uniform(75, 95), 2)
    
    total_sleep_min = int(sleep_hours * 60) if sleep_hours else 480
    deep_sleep_min = int(total_sleep_min * random.uniform(0.15, 0.25))
    rem_sleep_min = int(total_sleep_min * random.uniform(0.20, 0.30))
    
    if wellness_score:
        ranking = max(1, min(20, int(21 - (wellness_score * 3))))
    else:
        ranking = random.randint(10, 15)
    
    cursor.execute("""
        UPDATE dados_wellness 
        SET tempo_cama = %s,
            tempo_adormecer = %s,
            num_despertares = %s,
            eficiencia_sono = %s,
            sono_profundo_min = %s,
            sono_rem_min = %s,
            ranking_wellness = %s
        WHERE id = %s
    """, (bedtime, sleep_onset, num_awakenings, sleep_efficiency, 
          deep_sleep_min, rem_sleep_min, ranking, wellness_id))

print(f"   ✅ {len(wellness_records)} registros de wellness atualizados com dados detalhados de sono")

# 4. Update existing opponent data with correct column names
print("\n4️⃣ Atualizando dados de adversários existentes...")

# Portuguese teams with realistic data
teams_data = [
    {"nome": "FC Porto", "ranking": 2, "pontos_ultimos_5": 12, "gols_casa": 2.1, "gols_fora": 1.8, "estilo": "Ofensivo"},
    {"nome": "SL Benfica", "ranking": 3, "pontos_ultimos_5": 10, "gols_casa": 1.9, "gols_fora": 1.6, "estilo": "Equilibrado"},
    {"nome": "Sporting CP", "ranking": 1, "pontos_ultimos_5": 13, "gols_casa": 2.3, "gols_fora": 2.0, "estilo": "Ofensivo"},
    {"nome": "SC Braga", "ranking": 4, "pontos_ultimos_5": 9, "gols_casa": 1.7, "gols_fora": 1.4, "estilo": "Defensivo"},
    {"nome": "Vitória SC", "ranking": 8, "pontos_ultimos_5": 6, "gols_casa": 1.3, "gols_fora": 1.0, "estilo": "Contra-ataque"},
    {"nome": "Rio Ave FC", "ranking": 12, "pontos_ultimos_5": 4, "gols_casa": 1.1, "gols_fora": 0.8, "estilo": "Defensivo"},
    {"nome": "Portimonense", "ranking": 16, "pontos_ultimos_5": 2, "gols_casa": 0.8, "gols_fora": 0.5, "estilo": "Defensivo"},
    {"nome": "Moreirense FC", "ranking": 14, "pontos_ultimos_5": 3, "gols_casa": 0.9, "gols_fora": 0.6, "estilo": "Defensivo"},
    {"nome": "Boavista FC", "ranking": 10, "pontos_ultimos_5": 5, "gols_casa": 1.2, "gols_fora": 0.9, "estilo": "Equilibrado"},
    {"nome": "CD Tondela", "ranking": 18, "pontos_ultimos_5": 1, "gols_casa": 0.7, "gols_fora": 0.4, "estilo": "Defensivo"}
]

# Update existing records with enhanced data
for team in teams_data:
    # Calculate difficulty ratings (0-5 scale)
    difficulty_home = round(5 - (team["ranking"] - 1) * 0.2, 1)
    difficulty_away = round(difficulty_home - 0.5, 1)
    
    # Ensure ratings stay within 0-5 range
    difficulty_home = max(0.5, min(5.0, difficulty_home))
    difficulty_away = max(0.5, min(5.0, difficulty_away))
    
    # Determine pressure intensity and possession
    if team["estilo"] == "Ofensivo":
        pressure = "Alta"
        possession = round(random.uniform(55, 65), 2)
    elif team["estilo"] == "Defensivo":
        pressure = "Baixa"
        possession = round(random.uniform(35, 45), 2)
    else:
        pressure = "Média"
        possession = round(random.uniform(45, 55), 2)
    
    # Goals conceded (inverse relationship with defensive strength)
    goals_conceded_home = round(random.uniform(0.5, 1.5), 1)
    goals_conceded_away = round(random.uniform(0.8, 2.0), 1)
    
    # Update existing record using correct column name 'nome_equipa'
    cursor.execute("""
        UPDATE analise_adversarios 
        SET ranking_liga = %s,
            pontos_ultimos_5_jogos = %s,
            golos_marcados_casa = %s,
            golos_sofridos_casa = %s,
            golos_marcados_fora = %s,
            golos_sofridos_fora = %s,
            posse_bola_media = %s,
            passes_certos_percentagem = %s,
            finalizacoes_por_jogo = %s,
            estilo_jogo = %s,
            intensidade_pressao = %s,
            dificuldade_casa = %s,
            dificuldade_fora = %s,
            ultima_atualizacao = CURRENT_TIMESTAMP
        WHERE nome_equipa = %s
    """, (team["ranking"], team["pontos_ultimos_5"], team["gols_casa"], goals_conceded_home,
          team["gols_fora"], goals_conceded_away, possession, 
          round(random.uniform(75, 90), 1), round(random.uniform(8, 15), 1),
          team["estilo"], pressure, difficulty_home, difficulty_away, team["nome"]))

print(f"   ✅ {len(teams_data)} equipas adversárias atualizadas na base de dados")

# 5. Update sessions with proper opponent data
print("\n5️⃣ Atualizando sessões com dados de adversários...")

# Get game sessions and update them with opponent data
cursor.execute("SELECT id FROM sessoes WHERE tipo = 'jogo'")
game_sessions = cursor.fetchall()

for session in game_sessions:
    session_id = session[0]
    opponent = random.choice(teams_data)
    
    # Get opponent difficulty from analise_adversarios using correct column name
    cursor.execute("""
        SELECT dificuldade_casa, dificuldade_fora 
        FROM analise_adversarios 
        WHERE nome_equipa = %s
    """, (opponent["nome"],))
    
    difficulty_data = cursor.fetchone()
    if difficulty_data:
        # Randomly choose home or away
        is_home = random.choice([True, False])
        difficulty = difficulty_data[0] if is_home else difficulty_data[1]
    else:
        difficulty = round(random.uniform(1.0, 5.0), 1)
    
    cursor.execute("""
        UPDATE sessoes 
        SET adversario = %s, dificuldade_adversario = %s
        WHERE id = %s
    """, (opponent["nome"], difficulty, session_id))

print(f"   ✅ {len(game_sessions)} sessões de jogo atualizadas com dados de adversários")

# Commit all changes
conn.commit()
cursor.close()
conn.close()

print("\n✅ Simulação completa de dados criada com sucesso!")
print("📊 Dados incluídos:")
print("   • Desacelerações detalhadas nos dados GPS")
print("   • Rastreamento completo do sono (tempo na cama, eficiência, fases)")
print("   • Rankings de wellness para hover (1-20)")
print("   • Análise completa de adversários com dificuldade 0-5")
print("   • Dados táticos (estilo de jogo, pressão, posse de bola)")
print("   • Sessões de jogo com adversários e dificuldade")
print("\n🔄 Reinicie o backend para ver os novos dados")
