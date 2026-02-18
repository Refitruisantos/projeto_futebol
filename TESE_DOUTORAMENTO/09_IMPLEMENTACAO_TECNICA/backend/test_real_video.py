"""
Test video upload with the user's actual video file
"""

import requests
import json
import os
import sys

def test_with_real_video():
    """Test with the user's actual video file"""
    
    video_path = r"C:\Users\sorai\Downloads\J2 FC Paços de Ferreira 0 x 1 GDC - Equipa Técnica FCPF (720p, h264).mp4"
    
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    file_size = os.path.getsize(video_path)
    print(f"📹 Found video file: {os.path.basename(video_path)}")
    print(f"📊 File size: {file_size / (1024*1024):.1f} MB")
    
    # Step 1: Create session
    print("\n📝 Creating session...")
    session_data = {
        "data": "2026-02-02",
        "tipo": "jogo",
        "adversario": "FC Paços de Ferreira",
        "jornada": 2,
        "resultado": "0-1",
        "duracao_min": 90,
        "local": "casa",
        "competicao": "Liga"
    }
    
    try:
        response = requests.post('http://localhost:8000/api/sessions', json=session_data)
        print(f"Session creation status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Session creation failed: {response.text}")
            return False
        
        session = response.json()
        session_id = session['id']
        print(f"✅ Session created: ID {session_id}")
        
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return False
    
    # Step 2: Upload video
    print(f"\n🎬 Uploading video to session {session_id}...")
    
    try:
        with open(video_path, 'rb') as video_file:
            files = {
                'file': (os.path.basename(video_path), video_file, 'video/mp4')
            }
            data = {
                'session_id': session_id,
                'analysis_type': 'quick',  # Use quick for testing
                'confidence_threshold': 0.5,
                'sample_rate': 10  # Sample every 10th frame for speed
            }
            
            print("📤 Uploading... (this may take a while for large files)")
            response = requests.post(
                'http://localhost:8000/api/computer-vision/upload-video',
                files=files,
                data=data,
                timeout=300  # 5 minute timeout
            )
            
            print(f"Upload status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Video upload successful!")
                print(f"   Analysis ID: {result.get('analysis_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                
                # Check analysis status
                analysis_id = result.get('analysis_id')
                if analysis_id:
                    print(f"\n🔍 Checking analysis status...")
                    status_response = requests.get(f'http://localhost:8000/api/computer-vision/analysis/{analysis_id}')
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   Current status: {status_data.get('status')}")
                        print(f"   Created: {status_data.get('created_at')}")
                
                return True
            else:
                print(f"❌ Video upload failed: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ Upload timed out - file may be too large")
        return False
    except Exception as e:
        print(f"❌ Video upload error: {e}")
        return False

def check_server_status():
    """Check if backend server is running"""
    try:
        response = requests.get('http://localhost:8000/api/computer-vision/models/info', timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend server issue: {response.status_code}")
            return False
    except:
        print("❌ Cannot connect to backend server")
        return False

if __name__ == "__main__":
    print("🧪 Testing Video Upload with Real File\n")
    
    # Check server first
    if not check_server_status():
        print("\n💡 Make sure backend server is running:")
        print("   cd backend")
        print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Test with real video
    success = test_with_real_video()
    
    if success:
        print("\n🎉 Video upload test completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Check the 'Análise de Vídeo' tab in your web interface")
        print("   2. Wait for analysis to complete (may take several minutes)")
        print("   3. View results and generate annotated video")
    else:
        print("\n❌ Video upload test failed!")
