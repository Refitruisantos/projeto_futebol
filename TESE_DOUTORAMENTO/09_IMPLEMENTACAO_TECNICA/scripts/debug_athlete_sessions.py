#!/usr/bin/env python3
"""Debug athlete session data loading issue"""

import psycopg2
import os
import requests

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

print("🔍 Debugging Athlete Session Data Loading\n")

ATHLETE_ID = 251  # From the URL in the image

# 1. Check if athlete exists
print("1️⃣ Checking athlete existence:")
cursor.execute("SELECT id, nome_completo, posicao FROM atletas WHERE id = %s", (ATHLETE_ID,))
athlete = cursor.fetchone()
if athlete:
    print(f"   ✅ Athlete found: {athlete[1]} ({athlete[2]})")
else:
    print(f"   ❌ Athlete {ATHLETE_ID} not found")
    cursor.close()
    conn.close()
    exit()

# 2. Check sessions for this athlete in dados_pse
print("\n2️⃣ Checking PSE data for athlete:")
cursor.execute("""
    SELECT COUNT(*) as pse_sessions,
           MIN(s.data) as earliest,
           MAX(s.data) as latest
    FROM dados_pse dp
    JOIN sessoes s ON dp.sessao_id = s.id
    WHERE dp.atleta_id = %s
""", (ATHLETE_ID,))
pse_stats = cursor.fetchone()
print(f"   PSE sessions: {pse_stats[0]}")
if pse_stats[0] > 0:
    print(f"   Date range: {pse_stats[1]} to {pse_stats[2]}")

# 3. Check sessions for this athlete in dados_gps
print("\n3️⃣ Checking GPS data for athlete:")
cursor.execute("""
    SELECT COUNT(*) as gps_sessions,
           MIN(s.data) as earliest,
           MAX(s.data) as latest
    FROM dados_gps dg
    JOIN sessoes s ON dg.sessao_id = s.id
    WHERE dg.atleta_id = %s
""", (ATHLETE_ID,))
gps_stats = cursor.fetchone()
print(f"   GPS sessions: {gps_stats[0]}")
if gps_stats[0] > 0:
    print(f"   Date range: {gps_stats[1]} to {gps_stats[2]}")

# 4. Check what the athlete metrics API returns
print("\n4️⃣ Testing athlete metrics API:")
try:
    response = requests.get(f"http://localhost:8000/api/athletes/{ATHLETE_ID}/metrics/7")
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('sessions', [])
        print(f"   ✅ API returned {len(sessions)} sessions")
        if sessions:
            print(f"   Sample session: {sessions[0].get('data')} - {sessions[0].get('tipo')}")
    else:
        print(f"   ❌ API error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ API request failed: {str(e)}")

# 5. Check comprehensive profile API
print("\n5️⃣ Testing comprehensive profile API:")
try:
    response = requests.get(f"http://localhost:8000/api/metrics/athletes/{ATHLETE_ID}/comprehensive-profile")
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('recent_sessions', [])
        print(f"   ✅ Comprehensive API returned {len(sessions)} recent sessions")
        if sessions:
            print(f"   Sample session: {sessions[0].get('data')} - {sessions[0].get('tipo')}")
    else:
        print(f"   ❌ Comprehensive API error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Comprehensive API request failed: {str(e)}")

# 6. Sample recent sessions from database
print("\n6️⃣ Sample recent sessions from database:")
cursor.execute("""
    SELECT DISTINCT s.id, s.data, s.tipo, 
           COUNT(dp.atleta_id) as has_pse,
           COUNT(dg.atleta_id) as has_gps
    FROM sessoes s
    LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
    LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
    WHERE s.data >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY s.id, s.data, s.tipo
    HAVING COUNT(dp.atleta_id) > 0 OR COUNT(dg.atleta_id) > 0
    ORDER BY s.data DESC
    LIMIT 10
""", (ATHLETE_ID, ATHLETE_ID))

recent_sessions = cursor.fetchall()
print(f"   Found {len(recent_sessions)} sessions with data for this athlete:")
for session in recent_sessions:
    print(f"     {session[1]} | {session[2]} | PSE: {session[3]} | GPS: {session[4]}")

cursor.close()
conn.close()

print("\n📊 Summary:")
print(f"   • Athlete {ATHLETE_ID} exists in database")
print(f"   • PSE sessions: {pse_stats[0]}")
print(f"   • GPS sessions: {gps_stats[0]}")
print(f"   • Recent sessions with data: {len(recent_sessions)}")
print("\n🎯 Issue likely in:")
print("   1. API endpoint not returning data correctly")
print("   2. Frontend not processing API response")
print("   3. Athlete ID mismatch between frontend and backend")
