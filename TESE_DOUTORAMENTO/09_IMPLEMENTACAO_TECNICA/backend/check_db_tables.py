"""
Check and create computer vision database tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from database import get_db_connection

def check_and_create_tables():
    """Check if CV tables exist and create them if needed"""
    
    try:
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if video_analysis table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'video_analysis'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Computer vision tables don't exist. Creating them...")
            
            # Read and execute the SQL schema
            schema_path = "database_schema_cv.sql"
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Execute the schema
                cursor.execute(schema_sql)
                conn.commit()
                print("✅ Computer vision tables created successfully!")
            else:
                print("❌ Schema file not found. Creating tables manually...")
                create_tables_manually(cursor, conn)
        else:
            print("✅ Computer vision tables already exist!")
        
        # Test table access
        cursor.execute("SELECT COUNT(*) FROM video_analysis;")
        count = cursor.fetchone()[0]
        print(f"📊 video_analysis table has {count} records")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def create_tables_manually(cursor, conn):
    """Create tables manually if schema file is missing"""
    
    # Create video_analysis table
    cursor.execute("""
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
    cursor.execute("""
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
    cursor.execute("""
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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_analysis_session_id ON video_analysis(session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_detections_analysis_id ON video_detections(analysis_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_metrics_analysis_id ON video_metrics(analysis_id);")
    
    conn.commit()
    print("✅ Tables created manually!")

if __name__ == "__main__":
    print("🔧 Checking Computer Vision Database Setup...")
    success = check_and_create_tables()
    
    if success:
        print("🎉 Database setup complete!")
    else:
        print("❌ Database setup failed!")
        sys.exit(1)
