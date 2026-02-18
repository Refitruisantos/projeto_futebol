"""
Debug the video upload endpoint to see what's happening
"""

import requests
import os

def test_video_upload_endpoint():
    """Test the video upload endpoint directly"""
    
    print("🔍 Testing video upload endpoint...\n")
    
    # First create a session
    session_data = {
        "data": "2026-02-02",
        "tipo": "jogo",
        "adversario": "FC Paços de Ferreira Test",
        "jornada": 1,
        "resultado": "0-1",
        "duracao_min": 90,
        "local": "casa",
        "competicao": "Liga"
    }
    
    print("1. Creating test session...")
    try:
        response = requests.post('http://localhost:8000/api/sessions', json=session_data)
        if response.status_code == 200:
            session = response.json()
            session_id = session['id']
            print(f"   ✅ Session created: ID {session_id}")
        else:
            print(f"   ❌ Session creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Session creation error: {e}")
        return
    
    # Test video upload with a small test file
    print("\n2. Testing video upload...")
    
    # Create a small test video file
    test_video_content = b"fake video content for testing upload endpoint"
    test_file_path = "test_upload.mp4"
    
    try:
        with open(test_file_path, 'wb') as f:
            f.write(test_video_content)
        
        with open(test_file_path, 'rb') as video_file:
            files = {'file': ('test_upload.mp4', video_file, 'video/mp4')}
            data = {
                'session_id': session_id,
                'analysis_type': 'quick',
                'confidence_threshold': '0.5',
                'sample_rate': '10'
            }
            
            print(f"   Uploading to session {session_id}...")
            response = requests.post(
                'http://localhost:8000/api/computer-vision/upload-video',
                files=files,
                data=data
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Upload successful!")
                print(f"   Analysis ID: {result.get('analysis_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                
                # Check if it's in the database
                print("\n3. Checking database...")
                from check_uploaded_videos import check_uploaded_videos
                check_uploaded_videos()
                
                return result.get('analysis_id')
            else:
                print(f"   ❌ Upload failed: {response.text}")
                
                # Check if it's a CORS issue
                print("\n   Checking CORS headers...")
                print(f"   Response headers: {dict(response.headers)}")
                
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            try:
                os.remove(test_file_path)
            except:
                pass
    
    # Test with the user's actual video file if it exists
    user_video_path = r"C:\Users\sorai\Downloads\J2 FC Paços de Ferreira 0 x 1 GDC - Equipa Técnica FCPF (720p, h264).mp4"
    
    if os.path.exists(user_video_path):
        print(f"\n4. Testing with user's actual video file...")
        print(f"   File: {os.path.basename(user_video_path)}")
        print(f"   Size: {os.path.getsize(user_video_path) / (1024*1024):.1f} MB")
        
        try:
            with open(user_video_path, 'rb') as video_file:
                files = {'file': (os.path.basename(user_video_path), video_file, 'video/mp4')}
                data = {
                    'session_id': session_id,
                    'analysis_type': 'quick',
                    'confidence_threshold': '0.5',
                    'sample_rate': '10'
                }
                
                print("   Uploading user's video...")
                response = requests.post(
                    'http://localhost:8000/api/computer-vision/upload-video',
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout for large file
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ User video upload successful!")
                    print(f"   Analysis ID: {result.get('analysis_id')}")
                    return result.get('analysis_id')
                else:
                    print(f"   ❌ User video upload failed: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ User video upload error: {e}")
    else:
        print(f"\n4. User video file not found at: {user_video_path}")

if __name__ == "__main__":
    analysis_id = test_video_upload_endpoint()
    if analysis_id:
        print(f"\n🎯 Analysis ID for monitoring: {analysis_id}")
        print("You can use this ID to test the computer vision monitor!")
