"""
Debug session creation API to find validation issues
"""

import requests
import json

def test_session_creation():
    """Test session creation with different data combinations"""
    
    # Test 1: Minimal required data
    minimal_data = {
        "data": "2026-02-02",
        "tipo": "jogo",
        "duracao_min": 90,
        "local": "casa"
    }
    
    print("🧪 Testing minimal session data...")
    try:
        response = requests.post('http://localhost:8000/api/sessions', json=minimal_data)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print(f"Success: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Full data as used in working test
    full_data = {
        "data": "2026-02-02",
        "tipo": "jogo",
        "adversario": "FC Paços de Ferreira",
        "jornada": 2,
        "resultado": "0-1",
        "duracao_min": 90,
        "local": "casa",
        "competicao": "Liga"
    }
    
    print("\n🧪 Testing full session data...")
    try:
        response = requests.post('http://localhost:8000/api/sessions', json=full_data)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print(f"Success: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 3: Check what the frontend might be sending
    frontend_data = {
        "data": "2026-02-02",
        "tipo": "jogo",
        "adversario": "FC Paços de Ferreira",
        "jornada": "2",  # String instead of int
        "resultado": "0-1",
        "duracao_min": "90",  # String instead of int
        "local": "casa",
        "competicao": "Liga"
    }
    
    print("\n🧪 Testing frontend-style data (strings)...")
    try:
        response = requests.post('http://localhost:8000/api/sessions', json=frontend_data)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print(f"Success: {response.json()}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_session_creation()
