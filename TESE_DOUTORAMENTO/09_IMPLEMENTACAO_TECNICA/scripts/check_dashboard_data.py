#!/usr/bin/env python3
"""Check what data the dashboard should be seeing"""

import psycopg2
import os
from datetime import datetime

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

print("🔍 DASHBOARD DATA CHECK\n")

# Check sessions by week
cursor.execute("""
    SELECT DATE(semana_inicio) as week, COUNT(*) as athletes, 
           AVG(carga_total_semanal) as avg_load
    FROM metricas_carga
    GROUP BY semana_inicio
    ORDER BY semana_inicio
""")

print("📅 WEEKS WITH METRICS:")
weeks = cursor.fetchall()
for week, count, avg_load in weeks:
    print(f"   {week}: {count} athletes, avg load {avg_load:.0f}")

print(f"\n   Total weeks: {len(weeks)}")

# Check current week data
cursor.execute("""
    SELECT a.id, a.nome_completo, a.numero_camisola, a.posicao,
           mc.carga_total_semanal, mc.monotonia, mc.nivel_risco_monotonia
    FROM metricas_carga mc
    JOIN atletas a ON mc.atleta_id = a.id
    WHERE mc.semana_inicio = (SELECT MAX(semana_inicio) FROM metricas_carga)
    ORDER BY mc.carga_total_semanal DESC
    LIMIT 5
""")

print("\n🏆 TOP 5 ATHLETES (Latest Week):")
top5 = cursor.fetchall()
for athlete_id, nome, numero, posicao, load, monotony, risk in top5:
    print(f"   {numero:2d} | {nome:20s} | {posicao:3s} | Load: {load:.0f} | Risk: {risk}")

# Check GPS velocity data
cursor.execute("""
    SELECT COUNT(*) as total, 
           COUNT(velocidade_max) as with_velocity,
           AVG(velocidade_max) as avg_velocity
    FROM dados_gps
    WHERE velocidade_max IS NOT NULL
""")

gps_check = cursor.fetchone()
print(f"\n📊 GPS DATA:")
print(f"   Total GPS records: {gps_check[0]}")
print(f"   Records with velocity: {gps_check[1]}")
print(f"   Average velocity: {gps_check[2]:.1f if gps_check[2] else 0} km/h")

# Check athlete numbers
cursor.execute("""
    SELECT COUNT(*) as total,
           COUNT(CASE WHEN numero_camisola IS NOT NULL THEN 1 END) as with_numbers
    FROM atletas WHERE ativo = TRUE
""")

athlete_check = cursor.fetchone()
print(f"\n👥 ATHLETES:")
print(f"   Total active: {athlete_check[0]}")
print(f"   With jersey numbers: {athlete_check[1]}")

# Check sessions date range
cursor.execute("""
    SELECT MIN(data) as first_session, MAX(data) as last_session, COUNT(*) as total
    FROM sessoes
""")

session_range = cursor.fetchone()
print(f"\n📆 SESSION DATE RANGE:")
print(f"   First: {session_range[0]}")
print(f"   Last: {session_range[1]}")
print(f"   Total: {session_range[2]}")

# Check games with opponents
cursor.execute("""
    SELECT COUNT(*) as total_games,
           COUNT(CASE WHEN adversario IS NOT NULL THEN 1 END) as with_opponent
    FROM sessoes WHERE tipo = 'jogo'
""")

game_check = cursor.fetchone()
print(f"\n⚽ GAMES:")
print(f"   Total games: {game_check[0]}")
print(f"   With opponent data: {game_check[1]}")

cursor.close()
conn.close()
