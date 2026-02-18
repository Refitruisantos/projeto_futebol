#!/usr/bin/env python3
"""Check which sessions have GPS/PSE data"""

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

print("🔍 Checking Session Data Coverage\n")

# Check which sessions have data
cursor.execute("""
    SELECT 
        s.data,
        s.tipo,
        COUNT(DISTINCT g.atleta_id) as gps_athletes,
        COUNT(DISTINCT p.atleta_id) as pse_athletes
    FROM sessoes s
    LEFT JOIN dados_gps g ON g.sessao_id = s.id
    LEFT JOIN dados_pse p ON p.sessao_id = s.id
    GROUP BY s.id, s.data, s.tipo
    ORDER BY s.data
    LIMIT 50
""")

print("📊 First 50 Sessions Data Coverage:")
print(f"{'Date':<12} | {'Type':<8} | GPS | PSE")
print("-" * 45)

sessions_without_data = []
for data, tipo, gps, pse in cursor.fetchall():
    print(f"{str(data):<12} | {tipo:<8} | {gps:3} | {pse:3}")
    if gps == 0 and pse == 0:
        sessions_without_data.append((data, tipo))

if sessions_without_data:
    print(f"\n❌ Sessions without data: {len(sessions_without_data)}")
    for data, tipo in sessions_without_data[:10]:
        print(f"   {data} | {tipo}")
else:
    print("\n✅ All sessions have GPS or PSE data")

# Check total sessions vs sessions with data
cursor.execute("SELECT COUNT(*) FROM sessoes")
total_sessions = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(DISTINCT s.id)
    FROM sessoes s
    LEFT JOIN dados_gps g ON g.sessao_id = s.id
    LEFT JOIN dados_pse p ON p.sessao_id = s.id
    WHERE g.id IS NOT NULL OR p.id IS NOT NULL
""")
sessions_with_data = cursor.fetchone()[0]

print(f"\n📈 Summary:")
print(f"   Total sessions: {total_sessions}")
print(f"   Sessions with data: {sessions_with_data}")
print(f"   Sessions without data: {total_sessions - sessions_with_data}")

cursor.close()
conn.close()
