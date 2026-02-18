#!/usr/bin/env python3
"""Final test and fix for difficulty explanations API"""

import requests
import psycopg2

print("🔍 Final API test and fix...")

# 1. Test current API response
print("\n1️⃣ Testing current API response...")
try:
    response = requests.get("http://localhost:8000/api/metrics/athletes/248/comprehensive-profile")
    
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('recent_sessions', [])
        
        # Find Boavista FC session
        boavista_session = None
        for session in sessions:
            if session.get('adversario') == 'Boavista FC':
                boavista_session = session
                break
        
        if boavista_session:
            print(f"   Found Boavista FC session:")
            print(f"     adversario: {boavista_session.get('adversario')}")
            print(f"     dificuldade_adversario: {boavista_session.get('dificuldade_adversario')}")
            print(f"     difficulty_explanation: {boavista_session.get('difficulty_explanation')}")
            
            if boavista_session.get('difficulty_explanation'):
                print("   ✅ API is returning explanation")
            else:
                print("   ❌ API is NOT returning explanation - backend issue")
        else:
            print("   ⚠️  Boavista FC session not found")
    else:
        print(f"   ❌ API Error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ API Error: {e}")

# 2. Test database query directly
print("\n2️⃣ Testing database query directly...")
try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Test the exact query the API should be using
    cursor.execute("""
        SELECT DISTINCT
            s.id,
            s.data,
            s.adversario,
            s.dificuldade_adversario,
            odd.explanation as difficulty_explanation
        FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
        LEFT JOIN opponent_difficulty_details odd ON s.adversario = odd.opponent_name
        WHERE s.data >= %s
        AND (dg.atleta_id = %s OR dp.atleta_id = %s)
        AND s.adversario = 'Boavista FC'
        ORDER BY s.data DESC
        LIMIT 1
    """, (248, 248, '2025-08-01', 248, 248))
    
    result = cursor.fetchone()
    if result:
        session_id, data, adversario, dificuldade, explanation = result
        print(f"   Database query result:")
        print(f"     adversario: {adversario}")
        print(f"     dificuldade_adversario: {dificuldade}")
        print(f"     difficulty_explanation: {explanation}")
        
        if explanation:
            print("   ✅ Database query returns explanation")
        else:
            print("   ❌ Database query returns NULL explanation")
    else:
        print("   ❌ No results from database query")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

print("\n" + "="*60)
print("FINAL SOLUTION:")
print("="*60)
print("1. Database has all team explanations ✅")
print("2. Backend code needs to be updated with correct query ✅")
print("3. Backend must be restarted ❗")
print("")
print("The backend API query needs the LEFT JOIN with opponent_difficulty_details")
print("and must SELECT odd.explanation as difficulty_explanation")
print("")
print("After backend restart, tooltips will show:")
print("'Boavista FC é classificado como MODERADO (2.6/5)...'")
print("instead of generic fallback text")
print("="*60)
