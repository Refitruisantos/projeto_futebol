#!/usr/bin/env python3
"""Diagnose chart data issues in dashboard"""

import requests
import psycopg2

print("🔍 Diagnosing chart data issues...")

# 1. Check dashboard API data for charts
print("\n1️⃣ Checking dashboard API chart data...")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check athletes_overview for chart data
        athletes_overview = data.get('athletes_overview', [])
        print(f"   Found {len(athletes_overview)} athletes in overview")
        
        if len(athletes_overview) > 0:
            sample_athlete = athletes_overview[0]
            print("   Sample athlete data structure:")
            for key, value in sample_athlete.items():
                print(f"     {key}: {value}")
                
            # Check for missing fields needed by charts
            required_fields = ['nome_completo', 'distancia_total_media', 'velocidade_max_media', 'weekly_load']
            missing_fields = []
            
            for field in required_fields:
                if field not in sample_athlete or sample_athlete[field] is None:
                    missing_fields.append(field)
                    
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
            else:
                print("   ✅ All required fields present")
        else:
            print("   ❌ No athletes in overview")
            
        # Check top_load_athletes
        top_load = data.get('top_load_athletes', [])
        print(f"\n   Top load athletes: {len(top_load)}")
        if len(top_load) > 0:
            print(f"   Sample: {top_load[0].get('nome_completo')} - {top_load[0].get('weekly_load')} AU")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check database for GPS data completeness
print("\n2️⃣ Checking database GPS data for charts...")
try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Check GPS data availability
    cursor.execute("""
        SELECT 
            a.nome_completo,
            COUNT(g.id) as gps_sessions,
            AVG(g.distancia_total) as avg_distance,
            AVG(g.velocidade_max) as avg_max_speed,
            AVG(g.aceleracoes) as avg_accelerations
        FROM atletas a
        LEFT JOIN dados_gps g ON g.atleta_id = a.id
        WHERE a.ativo = TRUE
        GROUP BY a.id, a.nome_completo
        ORDER BY avg_distance DESC NULLS LAST
        LIMIT 10
    """)
    
    gps_results = cursor.fetchall()
    print(f"   Found GPS data for {len(gps_results)} athletes:")
    
    for nome, sessions, distance, speed, accel in gps_results[:5]:
        print(f"     - {nome}: {sessions} sessions")
        print(f"       Distance: {distance:.0f}m, Speed: {speed:.1f}km/h" if distance and speed else "       No GPS data")
    
    # Check load metrics
    cursor.execute("""
        SELECT 
            a.nome_completo,
            mc.carga_total_semanal
        FROM atletas a
        LEFT JOIN metricas_carga mc ON mc.atleta_id = a.id
        WHERE a.ativo = TRUE
        ORDER BY mc.carga_total_semanal DESC NULLS LAST
        LIMIT 5
    """)
    
    load_results = cursor.fetchall()
    print(f"\n   Load data for top athletes:")
    
    for nome, carga in load_results:
        print(f"     - {nome}: {carga:.0f} AU" if carga else f"     - {nome}: No load data")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

print("\n3️⃣ Issues Identified:")
print("   1. Chart components may not be receiving proper data structure")
print("   2. API may not be providing all required fields for charts")
print("   3. Frontend chart components may have incorrect data mapping")
print("   4. Missing athlete names and values in chart displays")

print("\n🔧 Next steps:")
print("   1. Check frontend chart components code")
print("   2. Ensure API provides all required chart data")
print("   3. Fix data mapping between API and chart components")
print("   4. Add proper athlete names and values to charts")
