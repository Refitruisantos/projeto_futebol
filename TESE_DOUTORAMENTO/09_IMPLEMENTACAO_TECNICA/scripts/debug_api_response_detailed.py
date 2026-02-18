#!/usr/bin/env python3
"""Debug detailed API response to see exact data structure"""

import requests
import json

ATHLETE_ID = 251  # From the URL shown in browser

print("🔍 Detailed API Response Analysis\n")

try:
    response = requests.get(f"http://localhost:8000/api/metrics/athletes/{ATHLETE_ID}/comprehensive-profile")
    
    if response.status_code == 200:
        data = response.json()
        
        print("📊 WELLNESS DATA:")
        wellness_data = data.get('wellness_data', [])
        print(f"   Count: {len(wellness_data)}")
        if wellness_data:
            print(f"   Sample record: {json.dumps(wellness_data[0], indent=2, default=str)}")
        else:
            print("   ❌ No wellness data found")
            
        print("\n🏋️ PHYSICAL EVALUATIONS:")
        physical_evals = data.get('physical_evaluations', [])
        print(f"   Count: {len(physical_evals)}")
        if physical_evals:
            print(f"   Sample record: {json.dumps(physical_evals[0], indent=2, default=str)}")
        else:
            print("   ❌ No physical evaluations found")
            
        print("\n📈 WELLNESS TRENDS:")
        wellness_trends = data.get('wellness_trends')
        if wellness_trends:
            print(f"   Trends: {json.dumps(wellness_trends, indent=2, default=str)}")
        else:
            print("   ❌ No wellness trends found")
            
        print("\n⚠️ RISK ASSESSMENT:")
        risk_assessment = data.get('risk_assessment')
        if risk_assessment:
            print(f"   Risk data: {json.dumps(risk_assessment, indent=2, default=str)}")
        else:
            print("   ❌ No risk assessment found")
            
        print("\n🎯 RECENT SESSIONS:")
        recent_sessions = data.get('recent_sessions', [])
        print(f"   Count: {len(recent_sessions)}")
        if recent_sessions:
            print(f"   Sample session: {json.dumps(recent_sessions[0], indent=2, default=str)}")
            
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
