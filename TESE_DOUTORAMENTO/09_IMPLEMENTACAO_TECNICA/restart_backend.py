#!/usr/bin/env python3
"""
Restart backend server to apply fixes
"""
import subprocess
import sys
import time
import requests
from pathlib import Path

def kill_existing_servers():
    """Kill existing Python/uvicorn processes"""
    try:
        # Kill uvicorn processes
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                      capture_output=True, text=True)
        print("🔄 Stopped existing backend processes")
        time.sleep(2)
    except Exception as e:
        print(f"Note: {e}")

def start_backend():
    """Start the backend server"""
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        print("🚀 Starting backend server...")
        
        # Start uvicorn server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=backend_dir)
        
        # Wait a moment for server to start
        time.sleep(5)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8000/api/ingest/history", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully!")
                print("🌐 Server running at: http://localhost:8000")
                return True
            else:
                print(f"⚠️ Server responded with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def main():
    print("🔧 Restarting Backend Server")
    print("=" * 40)
    
    # Kill existing processes
    kill_existing_servers()
    
    # Start new backend
    if start_backend():
        print("\n🎉 Backend server restarted successfully!")
        print("📤 Ready for GPS file uploads")
        print("🔗 Frontend should now work at: http://localhost:5173")
    else:
        print("\n❌ Failed to restart backend server")
        print("Please check for errors and try manual restart")

if __name__ == "__main__":
    main()
