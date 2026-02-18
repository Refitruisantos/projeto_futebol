#!/usr/bin/env python3
"""
Test upload functionality with corrected files
"""
import requests
from pathlib import Path

def test_upload():
    """Test uploading a GPS file via API"""
    
    # Test file
    test_file = Path("rounds/jornada25_day1_recovery.csv")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        print("🧪 Testing GPS file upload...")
        
        # Prepare upload
        url = "http://localhost:8000/api/ingest/catapult"
        params = {
            'jornada': 25,
            'session_date': '2025-03-24'
        }
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/csv')}
            
            response = requests.post(url, files=files, params=params, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Records inserted: {result.get('inserted')}/{result.get('total_rows')}")
            print(f"   Errors: {len(result.get('errors', []))}")
            
            if result.get('errors'):
                print("   Error details:")
                for error in result.get('errors', [])[:3]:
                    print(f"     - {error}")
            
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("🧪 TESTING UPLOAD FUNCTIONALITY")
    print("=" * 40)
    
    if test_upload():
        print("\n🎉 Upload test successful!")
        print("📤 Ready for manual upload practice!")
    else:
        print("\n❌ Upload test failed")
        print("Please check backend server and try again")

if __name__ == "__main__":
    main()
