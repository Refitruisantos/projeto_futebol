"""
Test the CV API status endpoint that the frontend is calling
"""

import requests

def test_cv_api_endpoints():
    """Test the CV API endpoints the frontend uses"""
    
    print("🔍 Testing CV API endpoints...\n")
    
    # Test the specific analysis ID from the monitor
    analysis_id = "3f0ac8ec-c329-4a55-b1a7-8ed5c1ce5ee0"
    
    print(f"1. Testing analysis status endpoint for {analysis_id[:8]}...")
    try:
        response = requests.get(f'http://localhost:8000/api/computer-vision/analysis/{analysis_id}')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Response:")
            print(f"     Analysis ID: {data.get('analysis_id', 'N/A')}")
            print(f"     Status: {data.get('status', 'N/A')}")
            print(f"     Session ID: {data.get('session_id', 'N/A')}")
            print(f"     Error: {data.get('error_message', 'None')}")
            print(f"     Created: {data.get('created_at', 'N/A')}")
            print(f"     Completed: {data.get('completed_at', 'N/A')}")
            return data
        else:
            print(f"   ❌ API Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None
    
    print(f"\n2. Testing session analyses endpoint...")
    try:
        # Test getting analyses for session 362 (from the upload)
        response = requests.get('http://localhost:8000/api/computer-vision/session/362/analyses')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} analyses for session 362:")
            for analysis in data:
                print(f"     - {analysis.get('analysis_id', 'N/A')[:8]}... | {analysis.get('status', 'N/A')}")
        else:
            print(f"   ❌ Session analyses error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Session analyses request failed: {e}")
    
    print(f"\n3. Testing all sessions analyses...")
    try:
        # Test getting all analyses
        response = requests.get('http://localhost:8000/api/computer-vision/session/all/analyses')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data)} total analyses:")
            for analysis in data:
                print(f"     - {analysis.get('analysis_id', 'N/A')[:8]}... | Session {analysis.get('session_id', 'N/A')} | {analysis.get('status', 'N/A')}")
        else:
            print(f"   ❌ All analyses error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ All analyses request failed: {e}")

if __name__ == "__main__":
    test_cv_api_endpoints()
