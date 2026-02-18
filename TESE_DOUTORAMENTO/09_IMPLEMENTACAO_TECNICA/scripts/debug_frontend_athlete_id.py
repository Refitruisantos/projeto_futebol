#!/usr/bin/env python3
"""Debug which athlete ID is causing the 500 error in the frontend"""

import requests
import json

# Test different athlete IDs that might be accessed from the frontend
test_athlete_ids = [251, 255, 256, 257, 258, 259, 260, 270, 280, 290]

print("🔍 Testing Comprehensive Profile API for Different Athletes\n")

for athlete_id in test_athlete_ids:
    try:
        print(f"Testing athlete {athlete_id}...")
        response = requests.get(f"http://localhost:8000/api/metrics/athletes/{athlete_id}/comprehensive-profile")
        
        if response.status_code == 200:
            data = response.json()
            wellness_count = len(data.get('wellness_data', []))
            physical_count = len(data.get('physical_evaluations', []))
            sessions_count = len(data.get('recent_sessions', []))
            print(f"   ✅ SUCCESS - Wellness: {wellness_count}, Physical: {physical_count}, Sessions: {sessions_count}")
        elif response.status_code == 404:
            print(f"   ⚠️  404 - Athlete not found")
        elif response.status_code == 500:
            print(f"   ❌ 500 ERROR - {response.text[:200]}")
            # This is the problematic athlete - let's investigate further
            print(f"   🔍 Investigating athlete {athlete_id} error...")
            
            # Check if athlete exists in database
            try:
                athlete_check = requests.get(f"http://localhost:8000/api/athletes/{athlete_id}")
                if athlete_check.status_code == 200:
                    athlete_data = athlete_check.json()
                    print(f"      Athlete exists: {athlete_data.get('data', {}).get('nome_completo', 'Unknown')}")
                else:
                    print(f"      Athlete check failed: {athlete_check.status_code}")
            except:
                print(f"      Could not check athlete existence")
        else:
            print(f"   ❓ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception for athlete {athlete_id}: {str(e)}")

print("\n🎯 Summary:")
print("   • Look for the athlete ID that shows '❌ 500 ERROR'")
print("   • This is likely the athlete the frontend is trying to load")
print("   • The error details will help identify the specific issue")
