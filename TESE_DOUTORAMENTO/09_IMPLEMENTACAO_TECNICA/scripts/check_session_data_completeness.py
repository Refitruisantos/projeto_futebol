#!/usr/bin/env python3
"""Check session data completeness to understand missing fields"""

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

print("🔍 Checking Session Data Completeness\n")

# Check sessions table structure and data
print("1️⃣ Sessions table structure:")
cursor.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'sessoes' 
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()
for col, dtype, nullable in columns:
    print(f"   {col}: {dtype} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")

print("\n2️⃣ Sample sessions data:")
cursor.execute("""
    SELECT 
        id, data, tipo, training_type, duracao_min, 
        adversario, jornada, resultado, observacoes
    FROM sessoes 
    ORDER BY data DESC 
    LIMIT 10
""")
sessions = cursor.fetchall()
for session in sessions:
    print(f"   ID {session[0]}: {session[1]} | {session[2]} | training_type={session[3]} | duration={session[4]} | adversario={session[5]} | jornada={session[6]} | resultado={session[7]}")

print("\n3️⃣ Data completeness statistics:")
cursor.execute("""
    SELECT 
        COUNT(*) as total_sessions,
        COUNT(training_type) as has_training_type,
        COUNT(duracao_min) as has_duration,
        COUNT(adversario) as has_adversario,
        COUNT(jornada) as has_jornada,
        COUNT(resultado) as has_resultado,
        COUNT(CASE WHEN tipo = 'jogo' THEN 1 END) as total_games,
        COUNT(CASE WHEN tipo = 'treino' THEN 1 END) as total_training
    FROM sessoes
""")
stats = cursor.fetchone()
print(f"   Total sessions: {stats[0]}")
print(f"   Has training_type: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
print(f"   Has duration: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
print(f"   Has adversario: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
print(f"   Has jornada: {stats[4]} ({stats[4]/stats[0]*100:.1f}%)")
print(f"   Has resultado: {stats[5]} ({stats[5]/stats[0]*100:.1f}%)")
print(f"   Games: {stats[6]}, Training: {stats[7]}")

print("\n4️⃣ Wellness data availability:")
cursor.execute("""
    SELECT 
        COUNT(*) as total_wellness_records,
        COUNT(DISTINCT atleta_id) as athletes_with_wellness,
        MIN(data) as earliest_wellness,
        MAX(data) as latest_wellness
    FROM dados_wellness
""")
wellness_stats = cursor.fetchone()
print(f"   Total wellness records: {wellness_stats[0]}")
print(f"   Athletes with wellness data: {wellness_stats[1]}")
print(f"   Date range: {wellness_stats[2]} to {wellness_stats[3]}")

print("\n5️⃣ Recent wellness data sample:")
cursor.execute("""
    SELECT 
        a.nome_completo,
        dw.data,
        dw.wellness_score,
        dw.wellness_status
    FROM dados_wellness dw
    JOIN atletas a ON dw.atleta_id = a.id
    ORDER BY dw.data DESC
    LIMIT 5
""")
wellness_sample = cursor.fetchall()
for name, date, score, status in wellness_sample:
    print(f"   {name}: {date} | Score: {score} | Status: {status}")

cursor.close()
conn.close()

print("\n📊 Summary:")
print("   • Check if training_type column exists and has data")
print("   • Verify duration field is populated")
print("   • Confirm wellness data is being generated")
print("   • Identify missing game metadata (adversario, jornada, resultado)")
