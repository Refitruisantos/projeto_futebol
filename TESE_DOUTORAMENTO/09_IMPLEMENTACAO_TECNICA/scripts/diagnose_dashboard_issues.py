#!/usr/bin/env python3
"""Diagnose dashboard data issues"""

import requests
import psycopg2
import json

print("🔍 Diagnosing dashboard data issues...")

# 1. Test team summary API
print("\n1️⃣ Testing team summary API...")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/summary")
    
    if response.status_code == 200:
        data = response.json()
        print("   Team Summary API Response:")
        for key, value in data.items():
            print(f"     {key}: {value}")
        
        # Check for missing or zero values
        issues = []
        if not data.get('avg_high_speed_distance') or data.get('avg_high_speed_distance') == 0:
            issues.append("avg_high_speed_distance is missing/zero")
        if not data.get('total_athletes') or data.get('total_athletes') == 0:
            issues.append("total_athletes is missing/zero")
        
        if issues:
            print(f"   ❌ Issues found: {', '.join(issues)}")
        else:
            print("   ✅ API response looks good")
            
    else:
        print(f"   ❌ API Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check database directly
print("\n2️⃣ Checking database data directly...")
try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Check GPS data completeness
    cursor.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN dist_19_8_kmh IS NOT NULL AND dist_19_8_kmh > 0 THEN 1 END) as high_speed_records,
            COUNT(CASE WHEN aceleracoes IS NOT NULL AND aceleracoes > 0 THEN 1 END) as acceleration_records,
            COUNT(CASE WHEN desaceleracoes IS NOT NULL AND desaceleracoes > 0 THEN 1 END) as deceleration_records,
            COUNT(CASE WHEN sprints IS NOT NULL AND sprints > 0 THEN 1 END) as sprint_records,
            AVG(dist_19_8_kmh) as avg_high_speed_dist,
            AVG(aceleracoes) as avg_accelerations,
            AVG(desaceleracoes) as avg_decelerations,
            AVG(sprints) as avg_sprints
        FROM dados_gps
    """)
    
    gps_stats = cursor.fetchone()
    print(f"   GPS Data Statistics:")
    print(f"     Total GPS records: {gps_stats[0]}")
    print(f"     High speed distance records: {gps_stats[1]} ({gps_stats[1]/gps_stats[0]*100:.1f}%)")
    print(f"     Acceleration records: {gps_stats[2]} ({gps_stats[2]/gps_stats[0]*100:.1f}%)")
    print(f"     Deceleration records: {gps_stats[3]} ({gps_stats[3]/gps_stats[0]*100:.1f}%)")
    print(f"     Sprint records: {gps_stats[4]} ({gps_stats[4]/gps_stats[0]*100:.1f}%)")
    print(f"     Avg high speed distance: {gps_stats[5]:.1f}m" if gps_stats[5] else "     Avg high speed distance: NULL")
    
    # Check risk assessment data
    cursor.execute("""
        SELECT 
            COUNT(*) as total_assessments,
            COUNT(CASE WHEN nivel_risco = 'Alto' THEN 1 END) as high_risk,
            COUNT(CASE WHEN nivel_risco = 'Médio' THEN 1 END) as medium_risk,
            COUNT(CASE WHEN nivel_risco = 'Baixo' THEN 1 END) as low_risk
        FROM risk_assessment
    """)
    
    risk_stats = cursor.fetchone()
    print(f"\n   Risk Assessment Statistics:")
    print(f"     Total risk assessments: {risk_stats[0]}")
    print(f"     High risk athletes: {risk_stats[1]}")
    print(f"     Medium risk athletes: {risk_stats[2]}")
    print(f"     Low risk athletes: {risk_stats[3]}")
    
    # Check active athletes
    cursor.execute("""
        SELECT 
            COUNT(*) as total_athletes,
            COUNT(CASE WHEN ativo = TRUE THEN 1 END) as active_athletes
        FROM atletas
    """)
    
    athlete_stats = cursor.fetchone()
    print(f"\n   Athlete Statistics:")
    print(f"     Total athletes: {athlete_stats[0]}")
    print(f"     Active athletes: {athlete_stats[1]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

print("\n3️⃣ Diagnosis Summary:")
print("   - Check if high speed distance data exists in GPS records")
print("   - Verify risk assessment calculations are working")
print("   - Ensure team summary API query is correct")
print("   - Validate all GPS metrics have proper data")
