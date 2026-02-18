"""
Script to check your Boavista video analysis status and results
Run this to see the current status of your analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
import json
from datetime import datetime

def check_boavista_analysis():
    """Check the status of Boavista video analysis"""
    
    db = get_db()
    
    print("🔍 Searching for Boavista video analysis...\n")
    
    # Find Boavista sessions with video analysis
    query = """
    SELECT 
        s.id as session_id,
        s.data as session_date,
        s.adversario as opponent,
        s.tipo as session_type,
        va.analysis_id,
        va.status,
        va.analysis_type,
        va.confidence_threshold,
        va.sample_rate,
        va.created_at as upload_time,
        va.started_at,
        va.completed_at,
        va.processing_time_seconds,
        va.error_message,
        va.video_path
    FROM sessoes s
    JOIN video_analysis va ON s.id = va.session_id
    WHERE s.adversario ILIKE '%boavista%' 
       OR s.adversario ILIKE '%boa vista%'
    ORDER BY va.created_at DESC;
    """
    
    analyses = db.query_to_dict(query)
    
    if not analyses:
        print("❌ No Boavista video analyses found.")
        print("   Make sure you:")
        print("   1. Created a session with 'Boavista' as opponent")
        print("   2. Uploaded a video file")
        print("   3. The analysis was submitted successfully")
        return
    
    print(f"✅ Found {len(analyses)} Boavista video analysis(es):\n")
    
    for i, analysis in enumerate(analyses, 1):
        print(f"📹 Analysis #{i}")
        print(f"   Session ID: {analysis['session_id']}")
        print(f"   Session Date: {analysis['session_date']}")
        print(f"   Opponent: {analysis['opponent']}")
        print(f"   Analysis ID: {analysis['analysis_id']}")
        print(f"   Status: {get_status_emoji(analysis['status'])} {analysis['status'].upper()}")
        print(f"   Analysis Type: {analysis['analysis_type']}")
        print(f"   Confidence: {analysis['confidence_threshold']}")
        print(f"   Sample Rate: Every {analysis['sample_rate']} frame(s)")
        print(f"   Uploaded: {analysis['upload_time']}")
        
        if analysis['started_at']:
            print(f"   Started: {analysis['started_at']}")
        
        if analysis['completed_at']:
            print(f"   Completed: {analysis['completed_at']}")
            
        if analysis['processing_time_seconds']:
            minutes = analysis['processing_time_seconds'] / 60
            print(f"   Processing Time: {minutes:.1f} minutes ({analysis['processing_time_seconds']:.1f} seconds)")
        
        if analysis['error_message']:
            print(f"   ❌ Error: {analysis['error_message']}")
            
        print(f"   Video Path: {analysis['video_path']}")
        
        # If completed, show detailed results
        if analysis['status'] == 'completed':
            show_analysis_results(db, analysis['analysis_id'])
        
        print("-" * 60)

def get_status_emoji(status):
    """Get emoji for analysis status"""
    status_emojis = {
        'queued': '🟡',
        'processing': '🔵', 
        'completed': '🟢',
        'failed': '🔴'
    }
    return status_emojis.get(status, '⚪')

def show_analysis_results(db, analysis_id):
    """Show detailed results for completed analysis"""
    
    print(f"\n   📊 ANALYSIS RESULTS:")
    
    # Get metrics
    metrics_query = """
    SELECT * FROM video_metrics 
    WHERE analysis_id = %s
    """
    
    metrics = db.query_to_dict(metrics_query, (analysis_id,))
    
    if metrics:
        m = metrics[0]
        print(f"   🎯 Ball Visibility: {m['ball_visibility_percentage']:.1f}%")
        print(f"   👥 Avg Players Detected: {m['avg_players_detected']:.1f}")
        print(f"   ⚽ Ball Tracking Quality: {m['ball_tracking_quality']}")
        print(f"   🏃 Ball Activity Level: {m['ball_activity_level']}")
        print(f"   📈 Overall Quality: {m['overall_quality_score']}")
        print(f"   📊 Video Coverage: {m['video_coverage_percentage']:.1f}%")
        
        print(f"\n   🏟️ POSSESSION BY ZONES:")
        print(f"   Left Third: {m['possession_left_third_percentage']:.1f}%")
        print(f"   Center Third: {m['possession_center_third_percentage']:.1f}%") 
        print(f"   Right Third: {m['possession_right_third_percentage']:.1f}%")
    
    # Get detection counts
    detections_query = """
    SELECT 
        object_class,
        COUNT(*) as total_detections,
        ROUND(AVG(confidence), 2) as avg_confidence,
        ROUND(MIN(confidence), 2) as min_confidence,
        ROUND(MAX(confidence), 2) as max_confidence
    FROM video_detections 
    WHERE analysis_id = %s
    GROUP BY object_class
    ORDER BY total_detections DESC;
    """
    
    detections = db.query_to_dict(detections_query, (analysis_id,))
    
    if detections:
        print(f"\n   🎯 DETECTION SUMMARY:")
        for det in detections:
            print(f"   {get_object_emoji(det['object_class'])} {det['object_class'].title()}: {det['total_detections']} detections (avg confidence: {det['avg_confidence']})")

def get_object_emoji(object_class):
    """Get emoji for detected object class"""
    emojis = {
        'ball': '⚽',
        'player': '👤',
        'goalkeeper': '🥅',
        'referee': '👨‍⚖️'
    }
    return emojis.get(object_class, '❓')

if __name__ == "__main__":
    try:
        check_boavista_analysis()
    except Exception as e:
        print(f"❌ Error checking analysis: {e}")
        print("Make sure your database is running and accessible.")
