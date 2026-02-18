"""
Check what actual data we have from video analyses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection
import json

def check_analysis_data():
    """Check what data we have from completed analyses"""
    
    db = DatabaseConnection()
    
    try:
        print("📊 Checking Video Analysis Data\n")
        
        # Get all completed analyses with their results
        print("1. Getting completed analyses with results...")
        analyses = db.query_to_dict("""
            SELECT analysis_id, session_id, video_path, analysis_type,
                   status, results, processing_time_seconds,
                   created_at, completed_at
            FROM video_analysis 
            WHERE status = 'completed' AND results IS NOT NULL
            ORDER BY completed_at DESC
            LIMIT 5
        """)
        
        print(f"   Found {len(analyses)} completed analyses with results\n")
        
        for i, analysis in enumerate(analyses, 1):
            print(f"Analysis {i}: {analysis['analysis_id'][:8]}...")
            print(f"   Session: {analysis['session_id']}")
            print(f"   Type: {analysis['analysis_type']}")
            print(f"   Processing time: {analysis['processing_time_seconds']} seconds")
            print(f"   Completed: {analysis['completed_at']}")
            
            # Parse and display results
            if analysis['results']:
                if isinstance(analysis['results'], str):
                    results = json.loads(analysis['results'])
                else:
                    results = analysis['results']
                
                print(f"   📈 Results:")
                print(f"     Total frames: {results.get('total_frames', 'N/A')}")
                print(f"     Ball detections: {results.get('ball_detections', 'N/A')}")
                print(f"     Player detections: {results.get('player_detections', 'N/A')}")
                print(f"     Ball visibility: {results.get('ball_visibility_percentage', 'N/A')}%")
                print(f"     Avg players per frame: {results.get('avg_players_detected', 'N/A')}")
                print(f"     Confidence score: {results.get('avg_confidence_score', 'N/A')}")
                
                # Check for additional metrics
                if 'detection_timeline' in results:
                    print(f"     Timeline data: Available")
                if 'player_positions' in results:
                    print(f"     Player positions: Available")
                if 'ball_trajectory' in results:
                    print(f"     Ball trajectory: Available")
            else:
                print(f"   ❌ No results data")
            
            print()
        
        # Check if we have any video metrics data
        print("2. Checking video metrics table...")
        try:
            metrics = db.query_to_dict("""
                SELECT vm.analysis_id, vm.ball_visibility_percentage,
                       vm.avg_players_detected, vm.avg_confidence_score,
                       va.session_id
                FROM video_metrics vm
                JOIN video_analysis va ON vm.analysis_id = va.analysis_id
                LIMIT 5
            """)
            
            if metrics:
                print(f"   Found {len(metrics)} entries in video_metrics table:")
                for metric in metrics:
                    print(f"     - {metric['analysis_id'][:8]}... | Session {metric['session_id']} | Ball: {metric['ball_visibility_percentage']}%")
            else:
                print("   No entries in video_metrics table")
                
        except Exception as e:
            print(f"   Video metrics table error: {e}")
        
        # Check for the specific session 362 analysis
        print("\n3. Checking Session 362 analysis (your uploaded video)...")
        session_362 = db.query_to_dict("""
            SELECT analysis_id, results, processing_time_seconds, completed_at
            FROM video_analysis 
            WHERE session_id = 362 AND status = 'completed'
        """)
        
        if session_362:
            analysis = session_362[0]
            print(f"   ✅ Found your video analysis: {analysis['analysis_id'][:8]}...")
            
            if analysis['results']:
                if isinstance(analysis['results'], str):
                    results = json.loads(analysis['results'])
                else:
                    results = analysis['results']
                
                print(f"   🎬 Your Video Results:")
                print(f"     📊 Total frames processed: {results.get('total_frames', 'N/A')}")
                print(f"     ⚽ Ball detected in: {results.get('ball_detections', 'N/A')} frames")
                print(f"     👥 Player detections: {results.get('player_detections', 'N/A')} total")
                print(f"     📈 Ball visibility: {results.get('ball_visibility_percentage', 'N/A')}%")
                print(f"     🏃 Average players per frame: {results.get('avg_players_detected', 'N/A')}")
                print(f"     🎯 Detection confidence: {results.get('avg_confidence_score', 'N/A')}")
                print(f"     ⏱️ Processing time: {analysis['processing_time_seconds']} seconds")
                
                return results
            else:
                print(f"   ❌ No results data for your video")
        else:
            print(f"   ❌ No completed analysis found for session 362")
        
        return None
        
    except Exception as e:
        print(f"❌ Error checking analysis data: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    results = check_analysis_data()
    if results:
        print(f"\n✅ Your video analysis data is available and ready to display!")
    else:
        print(f"\n❌ No analysis data found to display.")
