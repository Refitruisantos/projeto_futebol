#!/usr/bin/env python3
"""
Upload simulation data to the football analytics system
"""
import requests
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
SIMULATION_DIR = Path("simulation_data")

# GPS files to upload
gps_files = [
    {"file": "jornada_6_monday_recovery.csv", "date": "2025-01-20", "jornada": 6},
    {"file": "jornada_6_tuesday_technical.csv", "date": "2025-01-21", "jornada": 6},
    {"file": "jornada_6_wednesday_tactical.csv", "date": "2025-01-22", "jornada": 6},
    {"file": "jornada_6_thursday_physical.csv", "date": "2025-01-23", "jornada": 6},
    {"file": "jornada_6_friday_prematch.csv", "date": "2025-01-24", "jornada": 6},
    {"file": "jornada_6_saturday_match.csv", "date": "2025-01-25", "jornada": 6},
]

def upload_gps_file(file_info):
    """Upload a single GPS file"""
    file_path = SIMULATION_DIR / file_info["file"]
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📤 Uploading {file_info['file']}...")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_info["file"], f, 'text/csv')}
            data = {
                'jornada': file_info["jornada"],
                'session_date': file_info["date"]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ingest/catapult",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['inserted']} records inserted")
                if result.get('errors'):
                    print(f"⚠️  Warnings: {len(result['errors'])} errors")
                    for error in result['errors'][:3]:  # Show first 3 errors
                        print(f"   - {error}")
                return True
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Upload all simulation GPS files"""
    print("🚀 Starting GPS data upload...")
    print(f"📁 Looking for files in: {SIMULATION_DIR.absolute()}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/athletes/", timeout=5)
        print("✅ Backend server is responding")
    except:
        print("❌ Backend server not responding - start it first!")
        return
    
    success_count = 0
    total_files = len(gps_files)
    
    for file_info in gps_files:
        if upload_gps_file(file_info):
            success_count += 1
        print("-" * 50)
    
    print(f"📊 Upload Summary: {success_count}/{total_files} files uploaded successfully")
    
    if success_count == total_files:
        print("🎉 All simulation data uploaded successfully!")
        print("\n📈 Next steps:")
        print("1. Check your dashboard at http://localhost:5173")
        print("2. Verify data in Sessions page")
        print("3. Test the new scoring system")
    else:
        print("⚠️  Some files failed to upload. Check the errors above.")

if __name__ == "__main__":
    main()
