"""
Executable script to manually process video analyses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from database import DatabaseConnection

def process_all_queued_analyses():
    """Process all queued video analyses"""
    
    db = DatabaseConnection()
    
    try:
        print("🎬 Processing Video Analyses - Executable Script\n")
        
        # Get all queued analyses
        print("1. Finding queued analyses...")
        queued = db.query_to_dict("""
            SELECT analysis_id, session_id, video_path, analysis_type, created_at
            FROM video_analysis 
            WHERE status = 'queued'
            ORDER BY created_at ASC
        """)
        
        if not queued:
            print("   ✅ No queued analyses found")
            return
        
        print(f"   Found {len(queued)} queued analyses:")
        for analysis in queued:
            session_info = f"Session {analysis['session_id']}" if analysis['session_id'] else "No session"
            print(f"     - {analysis['analysis_id'][:8]}... | {session_info} | {analysis['analysis_type']}")
        
        # Process each analysis
        print(f"\n2. Processing analyses...")
        
        for i, analysis in enumerate(queued, 1):
            analysis_id = analysis['analysis_id']
            print(f"\n   Processing {i}/{len(queued)}: {analysis_id[:8]}...")
            
            try:
                # Call the manual processing endpoint
                response = requests.post(f'http://localhost:8000/api/computer-vision/analysis/{analysis_id}/process')
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Completed successfully!")
                    print(f"     Ball detections: {result['results']['ball_detections']}")
                    print(f"     Player detections: {result['results']['player_detections']}")
                    print(f"     Ball visibility: {result['results']['ball_visibility_percentage']}%")
                else:
                    print(f"   ❌ Failed: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error processing {analysis_id[:8]}: {e}")
        
        # Show final status
        print(f"\n3. Final status check...")
        completed = db.query_to_dict("""
            SELECT COUNT(*) as count FROM video_analysis WHERE status = 'completed'
        """)
        
        queued_remaining = db.query_to_dict("""
            SELECT COUNT(*) as count FROM video_analysis WHERE status = 'queued'
        """)
        
        print(f"   ✅ Completed analyses: {completed[0]['count']}")
        print(f"   ⏳ Queued analyses: {queued_remaining[0]['count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

def process_specific_analysis(analysis_id):
    """Process a specific analysis by ID"""
    
    print(f"🎯 Processing specific analysis: {analysis_id[:8]}...\n")
    
    try:
        response = requests.post(f'http://localhost:8000/api/computer-vision/analysis/{analysis_id}/process')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis {analysis_id[:8]} completed successfully!")
            print(f"   Ball detections: {result['results']['ball_detections']}")
            print(f"   Player detections: {result['results']['player_detections']}")
            print(f"   Ball visibility: {result['results']['ball_visibility_percentage']}%")
            print(f"   Avg players per frame: {result['results']['avg_players_detected']}")
            print(f"   Confidence score: {result['results']['avg_confidence_score']}")
            return True
        else:
            print(f"❌ Failed to process analysis: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing analysis: {e}")
        return False

def show_analysis_status():
    """Show current status of all analyses"""
    
    db = DatabaseConnection()
    
    try:
        print("📊 Current Analysis Status\n")
        
        # Get status summary
        status_summary = db.query_to_dict("""
            SELECT status, COUNT(*) as count
            FROM video_analysis
            GROUP BY status
            ORDER BY count DESC
        """)
        
        print("Status Summary:")
        for status in status_summary:
            print(f"   {status['status']}: {status['count']}")
        
        # Get recent analyses
        print(f"\nRecent Analyses:")
        recent = db.query_to_dict("""
            SELECT analysis_id, session_id, status, created_at, completed_at
            FROM video_analysis
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        for analysis in recent:
            session_info = f"Session {analysis['session_id']}" if analysis['session_id'] else "No session"
            completed_info = f" | Completed: {analysis['completed_at']}" if analysis['completed_at'] else ""
            print(f"   - {analysis['analysis_id'][:8]}... | {session_info} | {analysis['status']}{completed_info}")
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🎬 Video Analysis Processor")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            show_analysis_status()
        elif command == "process":
            if len(sys.argv) > 2:
                # Process specific analysis
                analysis_id = sys.argv[2]
                process_specific_analysis(analysis_id)
            else:
                # Process all queued
                process_all_queued_analyses()
        else:
            print("Usage:")
            print("  python process_video_analysis.py status          - Show analysis status")
            print("  python process_video_analysis.py process         - Process all queued analyses")
            print("  python process_video_analysis.py process <id>    - Process specific analysis")
    else:
        print("Available commands:")
        print("  status  - Show current analysis status")
        print("  process - Process all queued analyses")
        print("\nExample:")
        print("  python process_video_analysis.py process")
        print("  python process_video_analysis.py status")
