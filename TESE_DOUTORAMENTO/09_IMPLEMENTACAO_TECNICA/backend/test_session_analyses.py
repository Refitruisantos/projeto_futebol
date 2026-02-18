"""
Test session analyses endpoints to see why existing sessions aren't loading
"""

import requests

def test_session_analyses():
    """Test session analyses endpoints"""
    
    print("🔍 Testing session analyses endpoints...\n")
    
    # Test 1: Check what sessions exist
    print("1. Checking existing sessions...")
    try:
        response = requests.get('http://localhost:8000/api/sessions/')
        if response.status_code == 200:
            sessions = response.json()
            print(f"   ✅ Found {len(sessions)} sessions")
            
            # Show recent sessions
            for session in sessions[:5]:
                print(f"     - Session {session['id']}: {session.get('adversario', 'N/A')} ({session['data']})")
        else:
            print(f"   ❌ Sessions API error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Sessions request failed: {e}")
        return
    
    # Test 2: Check analyses for session 362 (the one we uploaded to)
    print(f"\n2. Checking analyses for session 362...")
    try:
        response = requests.get('http://localhost:8000/api/computer-vision/session/362/analyses')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            analyses = response.json()
            print(f"   ✅ Found {len(analyses)} analyses for session 362:")
            for analysis in analyses:
                print(f"     - {analysis['analysis_id'][:8]}... | {analysis['status']} | {analysis.get('created_at', 'N/A')}")
        else:
            print(f"   ❌ Session 362 analyses error: {response.text}")
    except Exception as e:
        print(f"   ❌ Session 362 analyses request failed: {e}")
    
    # Test 3: Check all analyses to see what sessions they're linked to
    print(f"\n3. Checking all analyses and their session links...")
    try:
        # This endpoint might not exist, let's check
        response = requests.get('http://localhost:8000/api/computer-vision/analyses')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            analyses = response.json()
            print(f"   ✅ Found {len(analyses)} total analyses:")
            for analysis in analyses:
                session_id = analysis.get('session_id', 'None')
                print(f"     - {analysis['analysis_id'][:8]}... | Session {session_id} | {analysis['status']}")
        else:
            print(f"   ❌ All analyses endpoint error: {response.text}")
    except Exception as e:
        print(f"   ❌ All analyses request failed: {e}")
    
    # Test 4: Check the specific completed analysis
    analysis_id = "3f0ac8ec-c329-4a55-b1a7-8ed5c1ce5ee0"
    print(f"\n4. Checking specific completed analysis {analysis_id[:8]}...")
    try:
        response = requests.get(f'http://localhost:8000/api/computer-vision/analysis/{analysis_id}')
        if response.status_code == 200:
            analysis = response.json()
            print(f"   ✅ Analysis details:")
            print(f"     Status: {analysis['status']}")
            print(f"     Session ID: {analysis.get('session_id', 'None')}")
            print(f"     Results: {analysis.get('results', {})}")
            print(f"     Created: {analysis.get('created_at', 'N/A')}")
            print(f"     Completed: {analysis.get('completed_at', 'N/A')}")
        else:
            print(f"   ❌ Analysis details error: {response.text}")
    except Exception as e:
        print(f"   ❌ Analysis details request failed: {e}")

if __name__ == "__main__":
    test_session_analyses()
