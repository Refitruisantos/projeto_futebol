#!/usr/bin/env python3
"""Check both dashboard API endpoints"""

import requests
import json

print("🔍 Checking dashboard API endpoints...")

# 1. Check team summary endpoint
print("\n1️⃣ Team Summary Endpoint (/metrics/team/summary):")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/summary")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Response successful")
        print(f"   high_risk_athletes: {data.get('high_risk_athletes')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check team dashboard endpoint
print("\n2️⃣ Team Dashboard Endpoint (/metrics/team/dashboard):")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Response successful")
        print("   Keys in response:", list(data.keys()))
        
        # Check for at_risk_athletes
        if 'at_risk_athletes' in data:
            at_risk = data['at_risk_athletes']
            print(f"   at_risk_athletes: {len(at_risk) if isinstance(at_risk, list) else at_risk}")
            if isinstance(at_risk, list) and len(at_risk) > 0:
                print(f"   Sample athlete: {at_risk[0]}")
        else:
            print("   ❌ at_risk_athletes not found in response")
            
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

print("\n3️⃣ Analysis:")
print("   The dashboard component expects:")
print("   - at_risk_athletes: array of athlete objects")
print("   - Each athlete should have: nome, posicao, classificacao")
print("   ")
print("   Current status:")
print("   - Summary endpoint has high_risk_athletes count ✅")
print("   - Dashboard endpoint needs at_risk_athletes array ❓")
