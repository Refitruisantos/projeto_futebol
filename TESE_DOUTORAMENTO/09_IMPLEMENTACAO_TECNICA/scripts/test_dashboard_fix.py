#!/usr/bin/env python3
"""Test dashboard fix for at-risk athletes"""

import requests
import json

print("🧪 Testing dashboard fix...")

# Test the team dashboard endpoint
print("\n1️⃣ Testing team dashboard endpoint...")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Response successful")
        
        # Check at_risk_athletes
        at_risk = data.get('at_risk_athletes', [])
        print(f"   at_risk_athletes count: {len(at_risk)}")
        
        if len(at_risk) > 0:
            print("   ✅ At-risk athletes found!")
            print("   Sample athletes:")
            for i, athlete in enumerate(at_risk[:3]):
                print(f"     {i+1}. {athlete.get('nome')} ({athlete.get('posicao')}) - {athlete.get('classificacao')}")
        else:
            print("   ❌ No at-risk athletes returned")
            
        # Check other key fields
        print(f"\n   Other dashboard data:")
        print(f"     athletes_overview: {len(data.get('athletes_overview', []))} athletes")
        print(f"     top_load_athletes: {len(data.get('top_load_athletes', []))} athletes")
        print(f"     risk_summary: {data.get('risk_summary', {})}")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

print("\n2️⃣ Expected frontend behavior:")
print("   - Dashboard should show athlete names in 'Atletas em Risco' section")
print("   - Instead of 'Nenhum atleta em risco', it should list actual athletes")
print("   - Each athlete should show: name, position, risk classification")

print("\n🔄 Next steps:")
print("   1. Restart backend if needed")
print("   2. Refresh dashboard page")
print("   3. Check 'Atletas em Risco' section shows actual athletes")
