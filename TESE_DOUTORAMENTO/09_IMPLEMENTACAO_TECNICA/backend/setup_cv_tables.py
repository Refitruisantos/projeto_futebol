"""
Setup computer vision database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection

def setup_cv_tables():
    """Create computer vision tables if they don't exist"""
    
    db = DatabaseConnection()
    
    try:
        # Check if video_analysis table exists
        result = db.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'video_analysis'
            );
        """)
        
        table_exists = result[0][0] if result else False
        
        if not table_exists:
            print("❌ Computer vision tables don't exist. Creating them...")
            
            # Create video_analysis table
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS video_analysis (
                    id SERIAL PRIMARY KEY,
                    analysis_id VARCHAR(36) UNIQUE NOT NULL,
                    session_id INTEGER,
                    video_path TEXT NOT NULL,
                    analysis_type VARCHAR(50) DEFAULT 'full',
                    confidence_threshold FLOAT DEFAULT 0.5,
                    sample_rate INTEGER DEFAULT 1,
                    status VARCHAR(20) DEFAULT 'queued',
                    results JSONB,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    processing_time_seconds FLOAT
                );
            """)
            
            # Create video_detections table
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS video_detections (
                    id SERIAL PRIMARY KEY,
                    analysis_id VARCHAR(36) NOT NULL,
                    frame_number INTEGER NOT NULL,
                    timestamp_seconds FLOAT NOT NULL,
                    object_class VARCHAR(20) NOT NULL,
                    confidence FLOAT NOT NULL,
                    bbox_x1 FLOAT NOT NULL,
                    bbox_y1 FLOAT NOT NULL,
                    bbox_x2 FLOAT NOT NULL,
                    bbox_y2 FLOAT NOT NULL,
                    center_x FLOAT NOT NULL,
                    center_y FLOAT NOT NULL,
                    area FLOAT NOT NULL
                );
            """)
            
            # Create video_metrics table
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS video_metrics (
                    id SERIAL PRIMARY KEY,
                    analysis_id VARCHAR(36) NOT NULL,
                    session_id INTEGER,
                    total_frames_analyzed INTEGER,
                    ball_visibility_percentage FLOAT,
                    avg_players_detected FLOAT,
                    goalkeeper_visibility_percentage FLOAT,
                    ball_tracking_quality VARCHAR(20),
                    total_ball_detections INTEGER,
                    avg_ball_movement_per_frame FLOAT,
                    max_ball_movement FLOAT,
                    ball_activity_level VARCHAR(20),
                    avg_players_visible FLOAT,
                    max_players_detected INTEGER,
                    min_players_detected INTEGER,
                    player_detection_consistency FLOAT,
                    possession_left_third_percentage FLOAT,
                    possession_center_third_percentage FLOAT,
                    possession_right_third_percentage FLOAT,
                    overall_quality_score VARCHAR(20),
                    video_coverage_percentage FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Create indexes
            db.execute_query("CREATE INDEX IF NOT EXISTS idx_video_analysis_session_id ON video_analysis(session_id);")
            db.execute_query("CREATE INDEX IF NOT EXISTS idx_detections_analysis_id ON video_detections(analysis_id);")
            db.execute_query("CREATE INDEX IF NOT EXISTS idx_video_metrics_analysis_id ON video_metrics(analysis_id);")
            
            print("✅ Computer vision tables created successfully!")
        else:
            print("✅ Computer vision tables already exist!")
        
        # Test table access
        result = db.execute_query("SELECT COUNT(*) FROM video_analysis;")
        count = result[0][0] if result else 0
        print(f"📊 video_analysis table has {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Setting up Computer Vision Database Tables...")
    success = setup_cv_tables()
    
    if success:
        print("🎉 Database setup complete!")
    else:
        print("❌ Database setup failed!")
        sys.exit(1)
