"""
Debug video visualization endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection
import json

def debug_video_endpoints():
    """Debug the video visualization endpoint errors"""
    
    db = DatabaseConnection()
    
    try:
        print("🔍 Debugging Video Visualization Endpoints\n")
        
        # Check the specific analysis IDs from the error
        analysis_ids = [
            'fda66774-282c-480b-8951-9c62462e6d8c',
            'abea9630-bb2e-4977-886d-7517a92f2e53'
        ]
        
        for analysis_id in analysis_ids:
            print(f"Analysis ID: {analysis_id}")
            
            # Get analysis data
            analysis = db.query_to_dict("""
                SELECT analysis_id, video_path, results, status, session_id
                FROM video_analysis 
                WHERE analysis_id = %s
            """, (analysis_id,))
            
            if analysis:
                analysis = analysis[0]
                print(f"   ✅ Found in database")
                print(f"   Status: {analysis['status']}")
                print(f"   Session: {analysis['session_id']}")
                print(f"   Video path: {analysis['video_path']}")
                
                # Check if video file exists
                if analysis['video_path']:
                    if os.path.exists(analysis['video_path']):
                        print(f"   ✅ Video file exists")
                        
                        # Check file size
                        file_size = os.path.getsize(analysis['video_path'])
                        print(f"   File size: {file_size} bytes")
                        
                        # Try to read with OpenCV
                        try:
                            import cv2
                            cap = cv2.VideoCapture(analysis['video_path'])
                            if cap.isOpened():
                                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                                fps = cap.get(cv2.CAP_PROP_FPS)
                                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                
                                print(f"   ✅ Video readable by OpenCV")
                                print(f"   Frames: {frame_count}, FPS: {fps}, Size: {width}x{height}")
                                
                                # Try to read first frame
                                ret, frame = cap.read()
                                if ret:
                                    print(f"   ✅ First frame readable")
                                else:
                                    print(f"   ❌ Cannot read first frame")
                                
                                cap.release()
                            else:
                                print(f"   ❌ Video not readable by OpenCV")
                        except Exception as e:
                            print(f"   ❌ OpenCV error: {e}")
                    else:
                        print(f"   ❌ Video file does not exist")
                        print(f"   Path: {analysis['video_path']}")
                else:
                    print(f"   ❌ No video path in database")
                
                # Check results
                if analysis['results']:
                    if isinstance(analysis['results'], str):
                        try:
                            results = json.loads(analysis['results'])
                            print(f"   ✅ Results JSON parseable")
                        except:
                            print(f"   ❌ Results JSON not parseable")
                    else:
                        print(f"   ✅ Results already parsed")
                else:
                    print(f"   ❌ No results data")
            else:
                print(f"   ❌ Not found in database")
            
            print()
        
        # Check if video_visualization router is imported correctly
        print("Checking video visualization imports...")
        try:
            from routers.video_visualization import router
            print("   ✅ video_visualization router imported successfully")
        except Exception as e:
            print(f"   ❌ Import error: {e}")
        
        # Check tactical analyzer imports
        try:
            from computer_vision.tactical_analyzer import TacticalAnalyzer, VideoTacticalVisualizer
            print("   ✅ TacticalAnalyzer imported successfully")
        except Exception as e:
            print(f"   ❌ TacticalAnalyzer import error: {e}")
        
        # Test basic functionality
        try:
            analyzer = TacticalAnalyzer()
            print("   ✅ TacticalAnalyzer instantiated successfully")
        except Exception as e:
            print(f"   ❌ TacticalAnalyzer instantiation error: {e}")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_video_endpoints()
