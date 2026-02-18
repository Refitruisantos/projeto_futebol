"""Test if Computer Vision endpoints are working"""
import sys
sys.path.insert(0, 'backend')

from main import app, CV_AVAILABLE
import requests

print("=" * 60)
print("Computer Vision Endpoint Test")
print("=" * 60)

print(f"\n1. CV_AVAILABLE flag: {CV_AVAILABLE}")

print("\n2. Registered routes with 'computer-vision':")
cv_routes = [route.path for route in app.routes if 'computer-vision' in route.path]
if cv_routes:
    for route in cv_routes:
        print(f"   - {route}")
else:
    print("   ⚠ No computer-vision routes found!")

print("\n3. Testing live endpoints:")
endpoints = [
    "/api/computer-vision/metrics/summary",
    "/api/computer-vision/session/360/analyses",
    "/api/computer-vision/models/info"
]

for endpoint in endpoints:
    try:
        r = requests.get(f"http://localhost:8000{endpoint}", timeout=2)
        status = "✓" if r.status_code == 200 else "✗"
        print(f"   {status} {endpoint}: {r.status_code}")
    except Exception as e:
        print(f"   ✗ {endpoint}: Error - {e}")

print("\n4. Testing session creation:")
try:
    r = requests.post(
        'http://localhost:8000/api/sessions/',
        json={'tipo': 'treino', 'data': '2026-02-07', 'duracao_min': 90}
    )
    if r.status_code in [200, 201]:
        print(f"   ✓ Session creation works: {r.status_code}")
        print(f"   Session ID: {r.json().get('id')}")
    else:
        print(f"   ✗ Session creation failed: {r.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
