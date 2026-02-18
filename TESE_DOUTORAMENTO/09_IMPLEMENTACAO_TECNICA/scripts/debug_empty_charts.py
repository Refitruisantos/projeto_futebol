#!/usr/bin/env python3
"""Debug why charts are empty and decelerations show dashes"""

import requests
import json

print("🔍 Debugging empty charts and missing data...")

# 1. Test the comprehensive profile API directly
print("\n1️⃣ Testing comprehensive profile API for athlete 255...")

try:
    response = requests.get("http://localhost:8000/api/metrics/athletes/255/comprehensive-profile")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ API Response successful")
        
        # Check load chart data
        load_chart_data = data.get('load_chart_data', [])
        print(f"\n📊 Load Chart Data: {len(load_chart_data)} records")
        if load_chart_data:
            print("   Sample load data:")
            for i, record in enumerate(load_chart_data[:3]):
                print(f"     {i+1}. Week: {record.get('week')}, Acute: {record.get('acute_load')}, Chronic: {record.get('chronic_load')}")
        else:
            print("   ❌ No load chart data found")
        
        # Check wellness data
        wellness_data = data.get('wellness_data', [])
        print(f"\n💤 Wellness Data: {len(wellness_data)} records")
        if wellness_data:
            print("   Sample wellness data:")
            for i, record in enumerate(wellness_data[:3]):
                print(f"     {i+1}. Date: {record.get('data')}, Score: {record.get('wellness_score')}")
        else:
            print("   ❌ No wellness data found")
        
        # Check sessions data
        sessions_data = data.get('recent_sessions', [])
        print(f"\n⚽ Sessions Data: {len(sessions_data)} records")
        if sessions_data:
            print("   Sample session data:")
            for i, record in enumerate(sessions_data[:3]):
                print(f"     {i+1}. Date: {record.get('data')}, Type: {record.get('tipo')}")
                print(f"         Decelerations: {record.get('avg_decelerations')}")
                print(f"         High Decelerations: {record.get('avg_high_decelerations')}")
                print(f"         Player Load: {record.get('avg_player_load')}")
        else:
            print("   ❌ No sessions data found")
            
    else:
        print(f"   ❌ API Error: {response.status_code}")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check database directly for athlete 255
print("\n2️⃣ Checking database directly for athlete 255...")

import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Check if athlete 255 exists
    cursor.execute("SELECT id, nome_completo FROM atletas WHERE id = 255")
    athlete = cursor.fetchone()
    if athlete:
        print(f"   ✅ Athlete found: {athlete[1]} (ID: {athlete[0]})")
    else:
        print("   ❌ Athlete 255 not found in database")
        cursor.execute("SELECT id, nome_completo FROM atletas WHERE ativo = TRUE LIMIT 5")
        athletes = cursor.fetchall()
        print("   Available athletes:")
        for aid, name in athletes:
            print(f"     - {aid}: {name}")
    
    # Check load metrics for athlete 255
    cursor.execute("""
        SELECT COUNT(*) FROM metricas_carga WHERE atleta_id = 255
    """)
    load_count = cursor.fetchone()[0]
    print(f"   Load metrics records: {load_count}")
    
    # Check wellness data for athlete 255
    cursor.execute("""
        SELECT COUNT(*) FROM dados_wellness WHERE atleta_id = 255
    """)
    wellness_count = cursor.fetchone()[0]
    print(f"   Wellness records: {wellness_count}")
    
    # Check GPS data for athlete 255
    cursor.execute("""
        SELECT COUNT(*), 
               COUNT(player_load) as with_player_load,
               COUNT(desaceleracoes) as with_decelerations,
               COUNT(num_desaceleracoes_altas) as with_high_decelerations
        FROM dados_gps WHERE atleta_id = 255
    """)
    gps_stats = cursor.fetchone()
    print(f"   GPS records: {gps_stats[0]}")
    print(f"   With player load: {gps_stats[1]}")
    print(f"   With decelerations: {gps_stats[2]}")
    print(f"   With high decelerations: {gps_stats[3]}")
    
    # Check sessions for athlete 255
    cursor.execute("""
        SELECT COUNT(DISTINCT s.id)
        FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id
        WHERE dg.atleta_id = 255
    """)
    session_count = cursor.fetchone()[0]
    print(f"   Sessions with GPS data: {session_count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

print("\n3️⃣ Diagnosis:")
print("   If athlete 255 doesn't exist, that's the problem")
print("   If data counts are 0, we need to generate data for athlete 255")
print("   If API returns empty arrays, there's a backend query issue")
print("   If decelerations are NULL, we need to populate that column")
