"""
Test video upload functionality directly
"""

import requests
import json
import sys
import os

def test_session_creation():
    """Test creating a session first"""
    
    session_data = {
        "data": "2026-02-02",
        "tipo": "jogo",
        "adversario": "Moreirense FC",
        "jornada": 10,
        "resultado": "0-3",
        "duracao_min": 90,
        "local": "casa",
        "competicao": "Liga"
    }
    
    try:
        response = requests.post('http://localhost:8000/api/sessions', json=session_data)
        print(f"Session creation status: {response.status_code}")
        
        if response.status_code == 200:
            session = response.json()
            print(f"✅ Session created: ID {session['id']}")
            return session['id']
        else:
            print(f"❌ Session creation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return None

def test_video_upload_endpoint(session_id):
    """Test video upload endpoint directly"""
    
    # Create a small test file
    test_file_path = "test_video.mp4"
    with open(test_file_path, 'wb') as f:
        f.write(b"fake video content for testing")
    
    try:
        files = {'file': ('test_video.mp4', open(test_file_path, 'rb'), 'video/mp4')}
        data = {
            'session_id': session_id,
            'analysis_type': 'quick',
            'confidence_threshold': 0.5,
            'sample_rate': 5
        }
        
        response = requests.post(
            'http://localhost:8000/api/computer-vision/upload-video',
            files=files,
            data=data
        )
        
        print(f"Video upload status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Video upload successful: {json.dumps(result, indent=2)}")
            return result.get('analysis_id')
        else:
            print(f"❌ Video upload failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Video upload error: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_endpoints():
    """Test all endpoints"""
    
    print("🧪 Testing Video Upload Workflow\n")
    
    # Test 1: Check if server is running
    try:
        response = requests.get('http://localhost:8000/api/computer-vision/models/info')
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server issue")
            return
    except:
        print("❌ Cannot connect to backend server")
        return
    
    # Test 2: Create a session
    print("\n📝 Testing session creation...")
    session_id = test_session_creation()
    
    if not session_id:
        print("❌ Cannot proceed without session")
        return
    
    # Test 3: Upload video
    print(f"\n🎬 Testing video upload for session {session_id}...")
    analysis_id = test_video_upload_endpoint(session_id)
    
    if analysis_id:
        print(f"✅ Video upload workflow completed successfully!")
        print(f"   Session ID: {session_id}")
        print(f"   Analysis ID: {analysis_id}")
    else:
        print("❌ Video upload workflow failed")

if __name__ == "__main__":
    test_endpoints()
