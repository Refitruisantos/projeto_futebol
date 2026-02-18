#!/usr/bin/env python3
"""Test physical evaluations API and data availability"""

import requests
import psycopg2
import os

# Test database connection first
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

print("🏋️ Testing Physical Evaluations System\n")

# 1. Check if physical evaluations table exists and has data
print("1️⃣ Checking physical evaluations table:")
cursor.execute("""
    SELECT COUNT(*) as total_evaluations,
           COUNT(DISTINCT atleta_id) as athletes_with_evaluations,
           MIN(data_avaliacao) as earliest_eval,
           MAX(data_avaliacao) as latest_eval
    FROM avaliacoes_fisicas
""")
eval_stats = cursor.fetchone()
print(f"   Total evaluations: {eval_stats[0]}")
print(f"   Athletes with evaluations: {eval_stats[1]}")
print(f"   Date range: {eval_stats[2]} to {eval_stats[3]}")

# 2. Sample physical evaluation data
print("\n2️⃣ Sample physical evaluation data:")
cursor.execute("""
    SELECT 
        a.nome_completo,
        af.data_avaliacao,
        af.sprint_35m_seconds,
        af.test_5_0_5_seconds,
        af.cmj_height_cm,
        af.vo2_max_ml_kg_min,
        af.percentile_speed,
        af.percentile_power,
        af.percentile_endurance
    FROM avaliacoes_fisicas af
    JOIN atletas a ON af.atleta_id = a.id
    ORDER BY af.data_avaliacao DESC
    LIMIT 5
""")
sample_evals = cursor.fetchall()
for eval_data in sample_evals:
    name, date, sprint, agility, cmj, vo2, speed_pct, power_pct, endurance_pct = eval_data
    print(f"   {name}: {date} | 35m={sprint}s | CMJ={cmj}cm | VO2={vo2} | Speed%={speed_pct}")

# 3. Test API endpoints
print("\n3️⃣ Testing API endpoints:")
BASE_URL = "http://localhost:8000/api/metrics"

# Test comprehensive profile for athlete 241
try:
    response = requests.get(f"{BASE_URL}/athletes/241/comprehensive-profile")
    if response.status_code == 200:
        data = response.json()
        physical_evals = data.get('physical_evaluations', [])
        print(f"   ✅ Comprehensive profile API: {len(physical_evals)} physical evaluations")
        if physical_evals:
            latest = physical_evals[0]
            print(f"      Latest eval: {latest.get('data_avaliacao')} | CMJ: {latest.get('cmj_height_cm')}cm")
        else:
            print("      ❌ No physical evaluations in comprehensive profile")
    else:
        print(f"   ❌ Comprehensive profile API error: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Backend server not running")
except Exception as e:
    print(f"   ❌ API test error: {str(e)}")

cursor.close()
conn.close()

print("\n📊 Physical Evaluations Status:")
if eval_stats[0] > 0:
    print(f"   ✅ Physical evaluations exist ({eval_stats[0]} records)")
    print(f"   ✅ {eval_stats[1]} athletes have evaluation data")
else:
    print("   ❌ No physical evaluation data found")
    print("   🔧 Need to run create_wellness_system.py script")

print("\n🎯 Next Steps:")
print("   1. Ensure backend server is running")
print("   2. Test comprehensive profile API in browser")
print("   3. Add physical tests display to frontend")
print("   4. Create mock data if evaluations are missing")
