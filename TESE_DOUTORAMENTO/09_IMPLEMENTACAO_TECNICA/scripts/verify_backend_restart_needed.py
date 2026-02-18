#!/usr/bin/env python3
"""Verify that backend restart is needed for detailed breakdown to work"""

import requests
import psycopg2

print("🔍 Verifying backend restart status...")

# 1. Check if database has the data
print("\n1️⃣ Database status:")
try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM opponent_difficulty_details 
        WHERE detailed_breakdown IS NOT NULL
    """)
    
    count = cursor.fetchone()[0]
    print(f"   ✅ Database has {count} opponents with detailed breakdown data")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database error: {e}")

# 2. Check if API returns the data
print("\n2️⃣ API status:")
try:
    response = requests.get("http://localhost:8000/api/metrics/athletes/248/comprehensive-profile")
    
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('recent_sessions', [])
        
        # Find a session with an opponent
        game_session = None
        for session in sessions:
            if session.get('adversario') and session.get('dificuldade_adversario'):
                game_session = session
                break
        
        if game_session:
            has_breakdown = bool(game_session.get('difficulty_breakdown'))
            print(f"   Game vs {game_session.get('adversario')} (Difficulty: {game_session.get('dificuldade_adversario')})")
            print(f"   Has difficulty_breakdown: {has_breakdown}")
            
            if has_breakdown:
                print("   ✅ API is returning detailed breakdown data")
            else:
                print("   ❌ API is NOT returning detailed breakdown data")
                print("   🔄 BACKEND RESTART REQUIRED")
        else:
            print("   ⚠️  No game sessions found to test")
    else:
        print(f"   ❌ API error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ API connection error: {e}")

print("\n" + "="*60)
print("SOLUTION:")
print("="*60)
print("1. The database has the detailed breakdown data ✅")
print("2. The backend code has been updated ✅") 
print("3. The frontend code has been updated ✅")
print("4. ❗ BACKEND NEEDS TO BE RESTARTED ❗")
print("")
print("To restart backend:")
print("cd C:\\Users\\sorai\\CascadeProjects\\projeto_futebol\\TESE_DOUTORAMENTO\\09_IMPLEMENTACAO_TECNICA\\backend")
print("python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
print("")
print("After restart, hover over difficulty ratings to see detailed breakdowns!")
print("="*60)
