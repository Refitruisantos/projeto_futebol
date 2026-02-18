#!/usr/bin/env python3
"""Debug why decelerations still show dashes in frontend"""

import requests
import json

print("🔍 Debugging deceleration display issue...")

# 1. Test the API response directly
print("\n1️⃣ Testing comprehensive profile API response...")

try:
    response = requests.get("http://localhost:8000/api/metrics/athletes/255/comprehensive-profile")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check sessions data structure
        sessions = data.get('recent_sessions', [])
        print(f"   Found {len(sessions)} sessions")
        
        if sessions:
            print("\n📊 Sample session data structure:")
            sample = sessions[0]
            
            # Print all available keys
            print("   Available fields:")
            for key, value in sample.items():
                print(f"     {key}: {value}")
            
            # Check specifically for deceleration fields
            deceleration_fields = [
                'avg_decelerations', 'desaceleracoes', 'avg_desaceleracoes',
                'decelerations', 'deceleration_count'
            ]
            
            print(f"\n   Checking deceleration fields:")
            for field in deceleration_fields:
                if field in sample:
                    print(f"     ✅ {field}: {sample[field]}")
                else:
                    print(f"     ❌ {field}: NOT FOUND")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check the backend query directly
print("\n2️⃣ Checking backend sessions query...")

import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Test the exact query used in the backend
    cursor.execute("""
        SELECT DISTINCT
            s.id,
            s.data,
            s.tipo,
            s.adversario,
            s.dificuldade_adversario,
            s.jornada,
            s.resultado,
            AVG(dg.distancia_total) as avg_distance,
            AVG(dg.velocidade_max) as avg_max_speed,
            AVG(dg.velocidade_media) as avg_avg_speed,
            AVG(dg.sprints) as avg_sprints,
            AVG(dg.aceleracoes) as avg_accelerations,
            AVG(dg.desaceleracoes) as avg_decelerations,
            AVG(dg.player_load) as avg_player_load,
            AVG(dg.num_desaceleracoes_altas) as avg_high_decelerations,
            AVG(dg.desaceleracao_maxima) as avg_max_deceleration,
            AVG(dp.pse) as avg_pse_load,
            COUNT(DISTINCT dp.atleta_id) as pse_records,
            COUNT(DISTINCT dg.atleta_id) as gps_records
        FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
        WHERE s.data >= %s
        AND (dg.atleta_id = %s OR dp.atleta_id = %s)
        GROUP BY s.id, s.data, s.tipo, s.adversario, s.dificuldade_adversario, s.jornada, s.resultado
        ORDER BY s.data DESC
        LIMIT 3
    """, (255, 255, '2025-08-01', 255, 255))
    
    results = cursor.fetchall()
    print(f"   Query returned {len(results)} sessions")
    
    if results:
        print("\n   Sample query results:")
        columns = [desc[0] for desc in cursor.description]
        
        for i, result in enumerate(results):
            print(f"\n   Session {i+1}:")
            for j, value in enumerate(result):
                if 'deceleration' in columns[j].lower():
                    print(f"     {columns[j]}: {value} ⭐")
                elif j < 10:  # Show first 10 columns
                    print(f"     {columns[j]}: {value}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

print("\n3️⃣ Diagnosis:")
print("   If avg_decelerations is NULL in query results, the JOIN is not working")
print("   If avg_decelerations has values but API shows None, there's a backend issue")
print("   If API shows values but frontend shows dashes, it's a frontend mapping issue")
