#!/usr/bin/env python3
"""Test API endpoints to see what data is being returned"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("🔍 Testing API Endpoints\n")

# Test 1: Dashboard summary
print("1️⃣ Testing /api/metrics/team/dashboard")
try:
    response = requests.get(f"{BASE_URL}/api/metrics/team/dashboard")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: ✅ {response.status_code}")
        print(f"   Week: {data.get('current_week', 'N/A')}")
        print(f"   Total Athletes: {data.get('total_athletes', 'N/A')}")
        print(f"   Risk Distribution: {data.get('risk_distribution', {})}")
        print(f"   Keys returned: {list(data.keys())}")
    else:
        print(f"   Status: ❌ {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Top 5 athletes
print("\n2️⃣ Testing /api/metrics/athletes/top5")
try:
    response = requests.get(f"{BASE_URL}/api/metrics/athletes/top5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: ✅ {response.status_code}")
        print(f"   Athletes returned: {len(data)}")
        if data:
            print("\n   Sample athlete data:")
            athlete = data[0]
            print(f"   - Nome: {athlete.get('nome_completo', 'N/A')}")
            print(f"   - Numero (AU): {athlete.get('numero_camisola', 'N/A')}")
            print(f"   - Load: {athlete.get('carga_total_semanal', 'N/A')}")
            print(f"   - All keys: {list(athlete.keys())}")
    else:
        print(f"   Status: ❌ {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Athletes at risk
print("\n3️⃣ Testing /api/metrics/athletes/at-risk")
try:
    response = requests.get(f"{BASE_URL}/api/metrics/athletes/at-risk")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: ✅ {response.status_code}")
        print(f"   Athletes at risk: {len(data)}")
        if data:
            print("\n   Sample risk athlete:")
            athlete = data[0]
            print(f"   - Nome: {athlete.get('nome_completo', 'N/A')}")
            print(f"   - Position: {athlete.get('posicao', 'N/A')}")
            print(f"   - Risk levels: {athlete.get('nivel_risco_monotonia', 'N/A')}")
    else:
        print(f"   Status: ❌ {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: GPS velocity data
print("\n4️⃣ Testing /api/metrics/gps/velocity")
try:
    response = requests.get(f"{BASE_URL}/api/metrics/gps/velocity")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: ✅ {response.status_code}")
        print(f"   Athletes with velocity: {len(data) if isinstance(data, list) else 'N/A'}")
    else:
        print(f"   Status: ❌ {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: Player load averages
print("\n5️⃣ Testing /api/metrics/team/player-load")
try:
    response = requests.get(f"{BASE_URL}/api/metrics/team/player-load")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: ✅ {response.status_code}")
        print(f"   Average load: {data.get('avg_load', 'N/A')}")
    else:
        print(f"   Status: ❌ {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*50)
print("API Testing Complete")
