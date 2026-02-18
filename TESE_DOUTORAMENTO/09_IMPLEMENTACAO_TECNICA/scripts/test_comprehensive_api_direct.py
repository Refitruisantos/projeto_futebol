#!/usr/bin/env python3
"""Test comprehensive profile API directly to identify the 500 error"""

import requests
import json

BASE_URL = "http://localhost:8000/api/metrics"
ATHLETE_ID = 255  # André Lopes from the image

print("🔍 Testing Comprehensive Profile API Directly\n")

try:
    print(f"Testing: {BASE_URL}/athletes/{ATHLETE_ID}/comprehensive-profile")
    response = requests.get(f"{BASE_URL}/athletes/{ATHLETE_ID}/comprehensive-profile")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response successful!")
        
        # Check data structure
        print(f"Response keys: {list(data.keys())}")
        
        if 'wellness_data' in data:
            print(f"Wellness records: {len(data['wellness_data'])}")
        else:
            print("❌ No wellness_data in response")
            
        if 'physical_evaluations' in data:
            print(f"Physical evaluations: {len(data['physical_evaluations'])}")
        else:
            print("❌ No physical_evaluations in response")
            
    else:
        print(f"❌ API Error: {response.status_code}")
        print("Response text:", response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("❌ Connection Error: Backend server not running")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Also test if backend is running at all
try:
    health_response = requests.get("http://localhost:8000/health")
    print(f"\nHealth check: {health_response.status_code}")
except:
    print("\n❌ Backend server appears to be down")
    print("Start backend with: python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
