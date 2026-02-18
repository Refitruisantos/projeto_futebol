"""
Test frontend-backend connection to identify the exact issue
"""

import requests
import json

def test_frontend_backend_connection():
    """Test the exact same calls the frontend would make"""
    
    print("🔍 Testing Frontend-Backend Connection\n")
    
    # Test 1: Check if backend is accessible from frontend perspective
    print("1. Testing backend accessibility...")
    try:
        response = requests.get('http://localhost:8000/api/computer-vision/models/info')
        print(f"   ✅ Backend accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        return False
    
    # Test 2: Test session creation exactly as frontend would
    print("\n2. Testing session creation (frontend style)...")
    session_data = {
        "data": "2026-02-02",
        "tipo": "jogo", 
        "adversario": "FC Paços de Ferreira",
        "jornada": "2",  # Frontend sends as string
        "resultado": "0-1",
        "duracao_min": "90",  # Frontend sends as string
        "local": "casa",
        "competicao": "Liga"
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/sessions',
            json=session_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            session = response.json()
            print(f"   ✅ Session created: ID {session['id']}")
            session_id = session['id']
        else:
            print(f"   ❌ Session creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Session creation error: {e}")
        return False
    
    # Test 3: Test CORS headers
    print("\n3. Testing CORS headers...")
    try:
        response = requests.options('http://localhost:8000/api/sessions')
        print(f"   OPTIONS request: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")
    
    # Test 4: Test video upload endpoint
    print("\n4. Testing video upload endpoint...")
    try:
        # Create a small test file
        test_content = b"fake video content for testing"
        files = {'file': ('test.mp4', test_content, 'video/mp4')}
        data = {
            'session_id': session_id,
            'analysis_type': 'quick',
            'confidence_threshold': '0.5',
            'sample_rate': '10'
        }
        
        response = requests.post(
            'http://localhost:8000/api/computer-vision/upload-video',
            files=files,
            data=data
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Video upload works: {result.get('analysis_id')}")
        else:
            print(f"   ❌ Video upload failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Video upload error: {e}")
    
    # Test 5: Check if frontend can reach backend
    print("\n5. Testing cross-origin request...")
    try:
        response = requests.get(
            'http://localhost:8000/api/sessions',
            headers={
                'Origin': 'http://localhost:5173',
                'Referer': 'http://localhost:5173/'
            }
        )
        print(f"   Cross-origin request: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Cross-origin test error: {e}")
    
    return True

if __name__ == "__main__":
    test_frontend_backend_connection()
