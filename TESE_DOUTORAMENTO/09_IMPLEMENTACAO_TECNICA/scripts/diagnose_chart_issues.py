#!/usr/bin/env python3
"""Diagnose dashboard chart issues"""

import requests
import psycopg2

print("🔍 Diagnosing dashboard chart issues...")

# 1. Check what the frontend is receiving vs what should be displayed
print("\n1️⃣ Testing team summary API response...")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/summary")
    
    if response.status_code == 200:
        data = response.json()
        print("   API Response:")
        print(f"     avg_accelerations: {data.get('avg_accelerations')}")
        print(f"     avg_decelerations: {data.get('avg_decelerations')}")
        print(f"     avg_sprints: {data.get('avg_sprints')}")
        print(f"     avg_high_speed_distance: {data.get('avg_high_speed_distance')}")
        print(f"     high_risk_athletes: {data.get('high_risk_athletes')}")
        
        # Compare with what's shown in dashboard
        dashboard_values = {
            'accelerations': 19,
            'decelerations': 20, 
            'sprints': 11,
            'high_speed_distance': 695
        }
        
        print("\n   Comparison (API vs Dashboard):")
        api_acc = data.get('avg_accelerations', 0)
        api_dec = data.get('avg_decelerations', 0)
        api_spr = data.get('avg_sprints', 0)
        api_hsd = data.get('avg_high_speed_distance', 0)
        
        print(f"     Accelerations: API={api_acc:.1f} vs Dashboard={dashboard_values['accelerations']} {'✅' if abs(api_acc - dashboard_values['accelerations']) < 1 else '❌'}")
        print(f"     Decelerations: API={api_dec:.1f} vs Dashboard={dashboard_values['decelerations']} {'✅' if abs(api_dec - dashboard_values['decelerations']) < 1 else '❌'}")
        print(f"     Sprints: API={api_spr:.1f} vs Dashboard={dashboard_values['sprints']} {'✅' if abs(api_spr - dashboard_values['sprints']) < 1 else '❌'}")
        print(f"     High Speed Distance: API={api_hsd:.0f} vs Dashboard={dashboard_values['high_speed_distance']} {'✅' if abs(api_hsd - dashboard_values['high_speed_distance']) < 50 else '❌'}")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check database values directly
print("\n2️⃣ Checking database calculations...")
try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Check GPS averages
    cursor.execute("""
        SELECT 
            ROUND(AVG(aceleracoes)::numeric, 1) as avg_accelerations,
            ROUND(AVG(desaceleracoes)::numeric, 1) as avg_decelerations,
            ROUND(AVG(sprints)::numeric, 1) as avg_sprints,
            ROUND(AVG(dist_19_8_kmh)::numeric, 0) as avg_high_speed_distance,
            COUNT(*) as total_records
        FROM dados_gps g
        JOIN atletas a ON g.atleta_id = a.id
        WHERE a.ativo = TRUE
    """)
    
    db_result = cursor.fetchone()
    print(f"   Database Direct Query:")
    print(f"     Accelerations: {db_result[0]}")
    print(f"     Decelerations: {db_result[1]}")
    print(f"     Sprints: {db_result[2]}")
    print(f"     High Speed Distance: {db_result[3]}")
    print(f"     Total Records: {db_result[4]}")
    
    # Check risk assessment
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT r.atleta_id) as high_risk_count
        FROM risk_assessment r
        JOIN atletas a ON r.atleta_id = a.id
        WHERE a.ativo = TRUE 
        AND (r.injury_risk_category = 'Alto' OR r.injury_risk_category = 'very_high')
    """)
    
    risk_result = cursor.fetchone()
    print(f"\n   High Risk Athletes (Database): {risk_result[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

# 3. Check if there's a caching issue or frontend calculation problem
print("\n3️⃣ Potential Issues:")
print("   - Frontend may be caching old values")
print("   - Dashboard calculations may be using different query")
print("   - Risk display component may not be reading high_risk_athletes field")
print("   - Values might be rounded differently in frontend")

print("\n🔧 Next steps:")
print("   1. Check frontend dashboard component code")
print("   2. Verify API endpoint being called by frontend")
print("   3. Fix risk athletes display component")
print("   4. Clear browser cache and refresh")
