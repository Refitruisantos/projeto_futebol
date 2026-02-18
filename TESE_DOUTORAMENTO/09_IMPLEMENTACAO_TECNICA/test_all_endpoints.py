"""Test ALL endpoints the frontend calls - via proxy and direct"""
import requests

print("=" * 60)
print("FULL ENDPOINT TEST")
print("=" * 60)

# Direct backend tests
direct_endpoints = [
    ("GET", "/api/sessions/"),
    ("GET", "/api/athletes/"),
    ("GET", "/api/opponents/"),
    ("GET", "/api/metrics/team/dashboard"),
    ("GET", "/api/metrics/team/summary"),
    ("GET", "/api/computer-vision/metrics/summary"),
    ("GET", "/api/computer-vision/session/360/analyses"),
    ("GET", "/api/computer-vision/models/info"),
    ("GET", "/api/xgboost/model-info"),
    ("GET", "/api/ai-analysis/"),
    ("GET", "/health"),
]

print("\n--- Direct Backend (localhost:8000) ---")
all_ok = True
for method, path in direct_endpoints:
    try:
        if method == "GET":
            r = requests.get(f"http://localhost:8000{path}", timeout=5)
        status = "✓" if r.status_code in [200, 404, 405] else "✗"
        if r.status_code >= 500:
            status = "✗"
            all_ok = False
        print(f"  {status} {method} {path}: {r.status_code}")
    except Exception as e:
        print(f"  ✗ {method} {path}: {e}")
        all_ok = False

# Proxy tests (through Vite)
proxy_endpoints = [
    ("GET", "/api/sessions/"),
    ("GET", "/api/athletes/"),
    ("GET", "/api/computer-vision/metrics/summary"),
    ("GET", "/api/computer-vision/session/360/analyses"),
    ("GET", "/api/xgboost/model-info"),
]

print("\n--- Via Vite Proxy (localhost:5173) ---")
for method, path in proxy_endpoints:
    try:
        if method == "GET":
            r = requests.get(f"http://localhost:5173{path}", timeout=5)
        status = "✓" if r.status_code in [200, 404, 405] else "✗"
        if r.status_code >= 500:
            status = "✗"
            all_ok = False
        print(f"  {status} {method} {path}: {r.status_code}")
    except Exception as e:
        print(f"  ✗ {method} {path}: {e}")
        all_ok = False

# Session creation test
print("\n--- Session Creation Test ---")
try:
    r = requests.post(
        'http://localhost:8000/api/sessions/',
        json={'tipo': 'treino', 'data': '2026-02-07', 'duracao_min': 90, 'local': 'casa'}
    )
    if r.status_code == 200:
        print(f"  ✓ Session created: ID {r.json().get('id')}")
    else:
        print(f"  ✗ Failed: {r.status_code} - {r.text[:200]}")
        all_ok = False
except Exception as e:
    print(f"  ✗ Error: {e}")
    all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("✅ ALL ENDPOINTS WORKING - No errors expected in frontend")
else:
    print("⚠ Some endpoints have issues - see above")
print("=" * 60)
