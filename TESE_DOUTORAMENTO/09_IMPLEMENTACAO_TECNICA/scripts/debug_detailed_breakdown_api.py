#!/usr/bin/env python3
"""Debug why detailed breakdown is not showing in API response"""

import requests
import json

print("🔍 Debugging detailed breakdown API response...")

# 1. Test the comprehensive profile API
print("\n1️⃣ Testing comprehensive profile API for athlete 248...")

try:
    response = requests.get("http://localhost:8000/api/metrics/athletes/248/comprehensive-profile")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check sessions data for difficulty fields
        sessions = data.get('recent_sessions', [])
        print(f"   Found {len(sessions)} sessions")
        
        if sessions:
            print("\n📊 Checking difficulty fields in sessions:")
            for i, session in enumerate(sessions[:3]):
                print(f"\n   Session {i+1} ({session.get('data')}):")
                print(f"     adversario: {session.get('adversario')}")
                print(f"     dificuldade_adversario: {session.get('dificuldade_adversario')}")
                print(f"     difficulty_explanation: {session.get('difficulty_explanation')}")
                print(f"     difficulty_breakdown: {session.get('difficulty_breakdown')}")
                
                if session.get('difficulty_breakdown'):
                    print(f"     ✅ Breakdown found (length: {len(session.get('difficulty_breakdown'))})")
                else:
                    print(f"     ❌ No breakdown data")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check database directly
print("\n2️⃣ Checking database for detailed breakdown data...")

import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Check if detailed_breakdown column exists and has data
    cursor.execute("""
        SELECT opponent_name, overall_rating, 
               CASE WHEN detailed_breakdown IS NOT NULL THEN 'HAS DATA' ELSE 'NULL' END as breakdown_status,
               LENGTH(detailed_breakdown) as breakdown_length
        FROM opponent_difficulty_details
        ORDER BY overall_rating DESC
    """)
    
    results = cursor.fetchall()
    print(f"   Found {len(results)} opponents in database:")
    
    for name, rating, status, length in results:
        print(f"     {name} ({rating}/5): {status} ({length} chars)")
    
    # Check a specific breakdown
    cursor.execute("""
        SELECT detailed_breakdown 
        FROM opponent_difficulty_details 
        WHERE opponent_name = 'FC Porto'
    """)
    
    breakdown_result = cursor.fetchone()
    if breakdown_result and breakdown_result[0]:
        print(f"\n   Sample breakdown for FC Porto:")
        print(f"   {breakdown_result[0][:200]}...")
    else:
        print(f"\n   ❌ No breakdown data for FC Porto")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

print("\n3️⃣ Diagnosis:")
print("   If breakdown_status shows NULL, data wasn't saved properly")
print("   If API doesn't return difficulty_breakdown, backend query needs fixing")
print("   If frontend shows fallback text, tooltip update didn't work")
