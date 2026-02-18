"""
Test script to verify session creation is working
"""

import requests
import psycopg2
from datetime import datetime

def test_database_connection():
    """Test if PostgreSQL is running and accessible"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            dbname='futebol_analytics',
            user='postgres',
            password='postgres',
            host='localhost'
        )
        print("✓ Database connection successful")
        
        # Check if sessoes table exists
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessoes")
        count = cur.fetchone()[0]
        print(f"✓ Found {count} existing sessions in database")
        
        # Check constraint
        cur.execute("""
            SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
            FROM pg_constraint 
            WHERE conrelid = 'sessoes'::regclass AND conname = 'sessoes_local_check'
        """)
        constraint = cur.fetchone()
        if constraint:
            print(f"✓ Constraint: {constraint[0]}")
            print(f"  Definition: {constraint[1]}")
        else:
            print("⚠ No sessoes_local_check constraint found")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_api_server():
    """Test if FastAPI server is running"""
    print("\n" + "=" * 60)
    print("Testing API Server")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✓ API server is running")
            return True
        else:
            print(f"✗ API server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API server: {e}")
        return False

def test_session_creation():
    """Test session creation via API"""
    print("\n" + "=" * 60)
    print("Testing Session Creation")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Session with local=None",
            "data": {
                "tipo": "Treino",
                "data": datetime.now().strftime("%Y-%m-%d"),
                "duracao_min": 90,
                "local": None
            }
        },
        {
            "name": "Session with local='Casa'",
            "data": {
                "tipo": "Jogo",
                "data": datetime.now().strftime("%Y-%m-%d"),
                "duracao_min": 90,
                "local": "Casa",
                "adversario": "Test Opponent"
            }
        },
        {
            "name": "Session with local='Fora'",
            "data": {
                "tipo": "Jogo",
                "data": datetime.now().strftime("%Y-%m-%d"),
                "duracao_min": 90,
                "local": "Fora",
                "adversario": "Test Opponent 2"
            }
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        try:
            response = requests.post(
                'http://localhost:8000/api/sessions/',
                json=test_case['data'],
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"  ✓ Success! Status: {response.status_code}")
                result = response.json()
                print(f"  Session ID: {result.get('id')}")
                success_count += 1
            else:
                print(f"  ✗ Failed with status {response.status_code}")
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Results: {success_count}/{len(test_cases)} tests passed")
    print(f"{'=' * 60}")
    
    return success_count == len(test_cases)

def main():
    print("\n" + "=" * 60)
    print("SESSION CREATION TEST SUITE")
    print("=" * 60)
    
    # Run tests
    db_ok = test_database_connection()
    api_ok = test_api_server()
    
    if db_ok and api_ok:
        session_ok = test_session_creation()
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Database: {'✓ OK' if db_ok else '✗ FAILED'}")
        print(f"API Server: {'✓ OK' if api_ok else '✗ FAILED'}")
        print(f"Session Creation: {'✓ OK' if session_ok else '✗ FAILED'}")
        print("=" * 60)
        
        if session_ok:
            print("\n✓ All tests passed! Session creation is working.")
        else:
            print("\n✗ Some tests failed. Check errors above.")
    else:
        print("\n✗ Cannot run session tests - database or API server not available")
        print("\nPlease:")
        if not db_ok:
            print("  1. Start PostgreSQL database")
        if not api_ok:
            print("  2. Start FastAPI server (python -m uvicorn main:app --reload)")

if __name__ == "__main__":
    main()
