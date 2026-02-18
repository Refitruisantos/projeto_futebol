#!/usr/bin/env python3
"""Create comprehensive simulation data including opponent data, decelerations, and sleep tracking - FINAL VERSION"""

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

print("🏗️ Criando dados de simulação completos...")

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

# 2. Update existing GPS data with deceleration values (using composite key)
print("\n2️⃣ Atualizando dados GPS existentes com desacelerações...")
cursor.execute("SELECT atleta_id, sessao_id FROM dados_gps")
gps_records = cursor.fetchall()

for record in gps_records:
    atleta_id, sessao_id = record
    
    # Generate realistic deceleration data
    num_high_decel = random.randint(15, 45)  # High decelerations per session
    max_decel = round(random.uniform(3.5, 8.2), 2)  # Max deceleration m/s²
    avg_decel = round(random.uniform(1.8, 3.5), 2)  # Average deceleration m/s²
    
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

# Update existing wellness records with detailed sleep data
cursor.execute("SELECT id, sleep_hours, wellness_score FROM dados_wellness")
wellness_records = cursor.fetchall()

for record in wellness_records:
    wellness_id, sleep_hours, wellness_score = record
    
    # Generate realistic sleep data with proper time format
    bedtime_hour = random.randint(22, 23)  # Fixed: only 22 or 23 to avoid 24:xx
    bedtime_min = random.randint(0, 59)
    bedtime = f"{bedtime_hour:02d}:{bedtime_min:02d}:00"
    
    sleep_onset_delay = random.randint(5, 30)  # Minutes to fall asleep
    total_bedtime_min = bedtime_hour * 60 + bedtime_min + sleep_onset_delay
    
    # Handle hour overflow properly
    if total_bedtime_min >= 24 * 60:
        total_bedtime_min -= 24 * 60  # Next day
    
    sleep_onset_hour = total_bedtime_min // 60
    sleep_onset_min = total_bedtime_min % 60
    sleep_onset = f"{sleep_onset_hour:02d}:{sleep_onset_min:02d}:00"
    
    num_awakenings = random.randint(0, 4)
    sleep_efficiency = round(random.uniform(75, 95), 2)
    
    # Sleep stages based on total sleep time
    total_sleep_min = int(sleep_hours * 60) if sleep_hours else 480
    deep_sleep_min = int(total_sleep_min * random.uniform(0.15, 0.25))  # 15-25% deep sleep
    rem_sleep_min = int(total_sleep_min * random.uniform(0.20, 0.30))   # 20-30% REM sleep
    
    # Wellness ranking (1-20 based on wellness score)
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

# 4. Enhanced opponent data with comprehensive team information
print("\n4️⃣ Criando dados completos de adversários...")

# Portuguese teams with realistic data
teams_data = [
    {"nome": "FC Porto", "ranking": 2, "pontos_ultimos_5": 12, "gols_por_jogo": 2.1, "estilo": "Ofensivo", "casa_fator": 1.3},
    {"nome": "SL Benfica", "ranking": 3, "pontos_ultimos_5": 10, "gols_por_jogo": 1.9, "estilo": "Equilibrado", "casa_fator": 1.2},
    {"nome": "Sporting CP", "ranking": 1, "pontos_ultimos_5": 13, "gols_por_jogo": 2.3, "estilo": "Ofensivo", "casa_fator": 1.4},
    {"nome": "SC Braga", "ranking": 4, "pontos_ultimos_5": 9, "gols_por_jogo": 1.7, "estilo": "Defensivo", "casa_fator": 1.1},
    {"nome": "Vitória SC", "ranking": 8, "pontos_ultimos_5": 6, "gols_por_jogo": 1.3, "estilo": "Contra-ataque", "casa_fator": 1.0},
    {"nome": "Rio Ave FC", "ranking": 12, "pontos_ultimos_5": 4, "gols_por_jogo": 1.1, "estilo": "Defensivo", "casa_fator": 0.9},
    {"nome": "Portimonense", "ranking": 16, "pontos_ultimos_5": 2, "gols_por_jogo": 0.8, "estilo": "Defensivo", "casa_fator": 0.8},
    {"nome": "Moreirense FC", "ranking": 14, "pontos_ultimos_5": 3, "gols_por_jogo": 0.9, "estilo": "Defensivo", "casa_fator": 0.8},
    {"nome": "Boavista FC", "ranking": 10, "pontos_ultimos_5": 5, "gols_por_jogo": 1.2, "estilo": "Equilibrado", "casa_fator": 0.9},
    {"nome": "CD Tondela", "ranking": 18, "pontos_ultimos_5": 1, "gols_por_jogo": 0.7, "estilo": "Defensivo", "casa_fator": 0.7}
]

# Create or update analise_adversarios table
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analise_adversarios (
            id SERIAL PRIMARY KEY,
            nome_adversario VARCHAR(100) NOT NULL,
            ranking_liga INTEGER,
            pontos_ultimos_5_jogos INTEGER,
            gols_por_jogo DECIMAL(3,1),
            estilo_jogo VARCHAR(50),
            fator_casa DECIMAL(3,1),
            dificuldade_casa DECIMAL(3,1),
            dificuldade_fora DECIMAL(3,1),
            pressao_intensidade VARCHAR(20),
            posse_bola_media DECIMAL(5,2),
            pontos_fortes TEXT,
            pontos_fracos TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ Tabela analise_adversarios criada/verificada")
except Exception as e:
    print(f"   ⚠️ Erro na tabela adversários: {e}")

# Clear existing data and insert fresh opponent data
cursor.execute("DELETE FROM analise_adversarios")

# Insert opponent data
for team in teams_data:
    # Calculate difficulty ratings
    difficulty_home = round(5 - (team["ranking"] - 1) * 0.2 + team["casa_fator"], 1)
    difficulty_away = round(difficulty_home - 0.5, 1)
    
    # Ensure ratings stay within 0-5 range
    difficulty_home = max(0.5, min(5.0, difficulty_home))
    difficulty_away = max(0.5, min(5.0, difficulty_away))
    
    # Determine pressure intensity
    if team["estilo"] == "Ofensivo":
        pressure = "Alta"
        possession = round(random.uniform(55, 65), 2)
    elif team["estilo"] == "Defensivo":
        pressure = "Baixa"
        possession = round(random.uniform(35, 45), 2)
    else:
        pressure = "Média"
        possession = round(random.uniform(45, 55), 2)
    
    # Generate strengths and weaknesses in Portuguese
    if team["estilo"] == "Ofensivo":
        strengths = "Ataque rápido, criatividade no terço final, pressão alta"
        weaknesses = "Vulnerável ao contra-ataque, defesa exposta"
    elif team["estilo"] == "Defensivo":
        strengths = "Organização defensiva, disciplina tática, bolas paradas"
        weaknesses = "Falta de criatividade, dependência de contra-ataques"
    else:
        strengths = "Equilíbrio tático, versatilidade, meio-campo forte"
        weaknesses = "Falta de especialização, inconsistência"
    
    cursor.execute("""
        INSERT INTO analise_adversarios 
        (nome_adversario, ranking_liga, pontos_ultimos_5_jogos, gols_por_jogo, 
         estilo_jogo, fator_casa, dificuldade_casa, dificuldade_fora, 
         pressao_intensidade, posse_bola_media, pontos_fortes, pontos_fracos)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (team["nome"], team["ranking"], team["pontos_ultimos_5"], team["gols_por_jogo"],
          team["estilo"], team["casa_fator"], difficulty_home, difficulty_away,
          pressure, possession, strengths, weaknesses))

print(f"   ✅ {len(teams_data)} equipas adversárias adicionadas à base de dados")

# 5. Update sessions with proper opponent data
print("\n5️⃣ Atualizando sessões com dados de adversários...")

# Get game sessions and update them with opponent data
cursor.execute("SELECT id FROM sessoes WHERE tipo = 'jogo'")
game_sessions = cursor.fetchall()

for session in game_sessions:
    session_id = session[0]
    opponent = random.choice(teams_data)
    
    # Get opponent difficulty from analise_adversarios
    cursor.execute("""
        SELECT dificuldade_casa, dificuldade_fora 
        FROM analise_adversarios 
        WHERE nome_adversario = %s
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
print("   • Pontos fortes e fracos das equipas em português")
print("   • Sessões de jogo com adversários e dificuldade")
print("\n🔄 Reinicie o backend para ver os novos dados")
