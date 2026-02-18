#!/usr/bin/env python3
"""Check if all sessions have proper week labels"""

import psycopg2
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

print("🔍 Checking Week Labels\n")

# Check sessions with jornada field
cursor.execute("""
    SELECT 
        data,
        tipo,
        jornada,
        observacoes
    FROM sessoes
    WHERE tipo = 'treino'
    ORDER BY data
    LIMIT 30
""")

print("📋 First 30 Training Sessions:")
print(f"{'Date':<12} | {'Jornada':<8} | Observacoes")
print("-" * 50)
for data, tipo, jornada, obs in cursor.fetchall():
    jornada_str = str(jornada) if jornada else 'NULL'
    obs_str = str(obs)[:25] if obs else 'NULL'
    print(f"{str(data):<12} | {jornada_str:<8} | {obs_str}")

# Check if jornada field exists and is populated
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(jornada) as with_jornada,
        COUNT(observacoes) as with_obs
    FROM sessoes
    WHERE tipo = 'treino'
""")

total, with_jornada, with_obs = cursor.fetchone()
print(f"\n📊 Training Sessions:")
print(f"   Total: {total}")
print(f"   With jornada: {with_jornada}")
print(f"   With observacoes: {with_obs}")

# Check games
cursor.execute("""
    SELECT data, jornada, adversario
    FROM sessoes
    WHERE tipo = 'jogo'
    ORDER BY data
""")

print(f"\n⚽ Game Sessions:")
print(f"{'Date':<12} | {'Round':<6} | Opponent")
print("-" * 50)
for data, jornada, adversario in cursor.fetchall():
    print(f"{str(data):<12} | {jornada:<6} | {adversario}")

cursor.close()
conn.close()
