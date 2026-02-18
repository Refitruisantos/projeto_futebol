#!/usr/bin/env python3
"""
Upload PSE simulation data to the football analytics system
"""
import requests
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
SIMULATION_DIR = Path("simulation_data")

# PSE files to upload
pse_files = [
    {"file": "Jogo6_monday_pse.csv", "date": "2025-01-20"},
    {"file": "Jogo6_tuesday_pse.csv", "date": "2025-01-21"},
    {"file": "Jogo6_wednesday_pse.csv", "date": "2025-01-22"},
    {"file": "Jogo6_thursday_pse.csv", "date": "2025-01-23"},
    {"file": "Jogo6_friday_pse.csv", "date": "2025-01-24"},
    {"file": "Jogo6_saturday_pse.csv", "date": "2025-01-25"},
]

def upload_pse_file(file_info):
    """Upload a single PSE file"""
    file_path = SIMULATION_DIR / file_info["file"]
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📤 Uploading {file_info['file']}...")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_info["file"], f, 'text/csv')}
            data = {
                'session_date': file_info["date"]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/ingest/pse",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('inserted', 'N/A')} records inserted")
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
    """Upload all simulation PSE files"""
    print("🚀 Starting PSE data upload...")
    print(f"📁 Looking for files in: {SIMULATION_DIR.absolute()}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/athletes/", timeout=5)
        print("✅ Backend server is responding")
    except:
        print("❌ Backend server not responding - start it first!")
        return
    
    success_count = 0
    total_files = len(pse_files)
    
    for file_info in pse_files:
        if upload_pse_file(file_info):
            success_count += 1
        print("-" * 50)
    
    print(f"📊 Upload Summary: {success_count}/{total_files} PSE files uploaded successfully")
    
    if success_count == total_files:
        print("🎉 All PSE simulation data uploaded successfully!")
        print("\n📈 Complete simulation week is now ready!")
        print("1. GPS data: ✅ Imported")
        print("2. PSE data: ✅ Imported")
        print("3. Dashboard: Ready at http://localhost:5173")
        print("4. Advanced scoring: Ready to implement")
    else:
        print("⚠️  Some PSE files failed to upload. Check the errors above.")

if __name__ == "__main__":
    main()
