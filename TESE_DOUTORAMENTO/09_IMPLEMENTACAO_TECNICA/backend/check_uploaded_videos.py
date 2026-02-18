"""
Check what videos have already been uploaded and their status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection

def check_uploaded_videos():
    """Check all video analyses in the database"""
    
    db = DatabaseConnection()
    
    try:
        print("🔍 Checking uploaded videos and analyses...\n")
        
        # Get all video analyses
        analyses = db.execute_query("""
            SELECT 
                va.analysis_id,
                va.session_id,
                va.video_path,
                va.analysis_type,
                va.status,
                va.created_at,
                va.started_at,
                va.completed_at,
                va.processing_time_seconds,
                va.error_message,
                s.adversario,
                s.data as session_date,
                s.tipo as session_type
            FROM video_analysis va
            LEFT JOIN sessoes s ON va.session_id = s.id
            ORDER BY va.created_at DESC
        """)
        
        if not analyses:
            print("❌ No videos have been uploaded yet")
            return
        
        print(f"📊 Found {len(analyses)} video analysis records:\n")
        
        for i, analysis in enumerate(analyses, 1):
            print(f"🎬 Video Analysis #{i}")
            print(f"   Analysis ID: {analysis[0]}")
            print(f"   Session ID: {analysis[1]} ({analysis[10] or 'Unknown'} - {analysis[11] or 'Unknown'})")
            print(f"   Video Path: {analysis[2]}")
            print(f"   Analysis Type: {analysis[3]}")
            print(f"   Status: {analysis[4]}")
            print(f"   Created: {analysis[5]}")
            
            if analysis[6]:  # started_at
                print(f"   Started: {analysis[6]}")
            if analysis[7]:  # completed_at
                print(f"   Completed: {analysis[7]}")
            if analysis[8]:  # processing_time_seconds
                print(f"   Processing Time: {analysis[8]:.1f} seconds ({analysis[8]/60:.1f} minutes)")
            if analysis[9]:  # error_message
                print(f"   Error: {analysis[9]}")
            
            # Check if video file still exists
            video_path = analysis[2]
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                print(f"   File Status: ✅ Exists ({file_size / (1024*1024):.1f} MB)")
            else:
                print(f"   File Status: ❌ Missing")
            
            print()
        
        # Get summary statistics
        print("📈 Summary Statistics:")
        
        status_counts = db.execute_query("""
            SELECT status, COUNT(*) as count
            FROM video_analysis
            GROUP BY status
            ORDER BY count DESC
        """)
        
        for status, count in status_counts:
            print(f"   {status}: {count}")
        
        # Get metrics if available
        metrics_count = db.execute_query("SELECT COUNT(*) FROM video_metrics")[0][0]
        detections_count = db.execute_query("SELECT COUNT(*) FROM video_detections")[0][0]
        
        print(f"\n📊 Database Records:")
        print(f"   Video Metrics: {metrics_count}")
        print(f"   Video Detections: {detections_count}")
        
        # Check for completed analyses with results
        completed_analyses = db.execute_query("""
            SELECT va.analysis_id, va.session_id, s.adversario, vm.ball_visibility_percentage, vm.avg_players_detected
            FROM video_analysis va
            LEFT JOIN sessoes s ON va.session_id = s.id
            LEFT JOIN video_metrics vm ON va.analysis_id = vm.analysis_id
            WHERE va.status = 'completed'
            ORDER BY va.completed_at DESC
        """)
        
        if completed_analyses:
            print(f"\n🎯 Completed Analyses ({len(completed_analyses)}):")
            for analysis in completed_analyses:
                analysis_id, session_id, adversario, ball_vis, avg_players = analysis
                print(f"   {adversario or f'Session {session_id}'}: Ball {ball_vis or 0:.1f}%, Players {avg_players or 0:.1f}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_uploaded_videos()
