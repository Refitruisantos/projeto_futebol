"""
Monitor all incoming requests to debug frontend issues
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import json
import time

class RequestMonitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        print(f"\n🔍 [{time.strftime('%H:%M:%S')}] {request.method} {request.url}")
        print(f"   Headers: {dict(request.headers)}")
        
        # Try to read body for POST requests
        if request.method == "POST":
            try:
                body = await request.body()
                if body:
                    if request.headers.get("content-type", "").startswith("application/json"):
                        try:
                            json_body = json.loads(body)
                            print(f"   JSON Body: {json_body}")
                        except:
                            print(f"   Body (first 200 chars): {body[:200]}")
                    else:
                        print(f"   Body size: {len(body)} bytes")
                        print(f"   Content-Type: {request.headers.get('content-type', 'unknown')}")
            except Exception as e:
                print(f"   Error reading body: {e}")
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            print(f"   ✅ Response: {response.status_code} ({process_time:.3f}s)")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            print(f"   ❌ Error: {e} ({process_time:.3f}s)")
            raise

# Import the main app
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

# Add monitoring middleware
app.add_middleware(RequestMonitorMiddleware)

if __name__ == "__main__":
    print("🔍 Starting FastAPI with request monitoring...")
    print("📋 This will show all requests from the frontend")
    print("🎯 Try uploading your video now and watch the logs\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
