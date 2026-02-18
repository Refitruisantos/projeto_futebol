"""
Fix computer vision database operations and create test data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection
import uuid
from datetime import datetime

def fix_and_test_cv_database():
    """Fix CV database operations and create test data"""
    
    db = DatabaseConnection()
    
    try:
        print("🔧 Fixing computer vision database operations...\n")
        
        # Test 1: Use query_to_dict method instead of execute_query
        print("1. Testing query_to_dict method...")
        try:
            result = db.query_to_dict("SELECT COUNT(*) as count FROM video_analysis")
            print(f"   ✅ video_analysis table has {result[0]['count']} records")
        except Exception as e:
            print(f"   ❌ query_to_dict failed: {e}")
            return False
        
        # Test 2: Create a test video analysis record using the correct method
        print("\n2. Creating test video analysis record...")
        analysis_id = str(uuid.uuid4())
        session_id = 360  # Use existing session
        
        try:
            # Use the connection's cursor directly for INSERT operations
            conn = db.get_connection()
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO video_analysis (
                    analysis_id, session_id, video_path, analysis_type,
                    confidence_threshold, sample_rate, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            cursor.execute(insert_query, (
                analysis_id, session_id, "test_video.mp4", "quick",
                0.5, 10, "queued"
            ))
            
            conn.commit()
            cursor.close()
            
            print(f"   ✅ Test record created with analysis_id: {analysis_id}")
            
        except Exception as e:
            print(f"   ❌ Insert failed: {e}")
            return False
        
        # Test 3: Verify the record exists
        print("\n3. Verifying test record...")
        try:
            result = db.query_to_dict("""
                SELECT analysis_id, session_id, status, created_at
                FROM video_analysis 
                WHERE analysis_id = %s
            """, (analysis_id,))
            
            if result and len(result) > 0:
                print(f"   ✅ Test record found: {result[0]}")
            else:
                print(f"   ❌ Test record not found")
                return False
                
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
            return False
        
        # Test 4: Create a few more test records with different statuses
        print("\n4. Creating additional test records...")
        
        test_records = [
            {
                'analysis_id': str(uuid.uuid4()),
                'session_id': session_id,
                'video_path': 'pacos_ferreira_video.mp4',
                'analysis_type': 'full',
                'status': 'processing',
                'confidence_threshold': 0.7,
                'sample_rate': 1
            },
            {
                'analysis_id': str(uuid.uuid4()),
                'session_id': session_id,
                'video_path': 'completed_analysis.mp4',
                'analysis_type': 'quick',
                'status': 'completed',
                'confidence_threshold': 0.5,
                'sample_rate': 5
            }
        ]
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        for record in test_records:
            try:
                cursor.execute(insert_query, (
                    record['analysis_id'], record['session_id'], record['video_path'], 
                    record['analysis_type'], record['confidence_threshold'], 
                    record['sample_rate'], record['status']
                ))
                print(f"   ✅ Created {record['status']} record: {record['analysis_id'][:8]}...")
            except Exception as e:
                print(f"   ❌ Failed to create {record['status']} record: {e}")
        
        conn.commit()
        cursor.close()
        
        # Test 5: Add some metrics for the completed analysis
        print("\n5. Adding test metrics for completed analysis...")
        completed_analysis_id = test_records[1]['analysis_id']
        
        try:
            metrics_query = """
                INSERT INTO video_metrics (
                    analysis_id, total_frames, ball_detections, player_detections,
                    ball_visibility_percentage, avg_players_detected, avg_confidence_score,
                    processing_time_seconds, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            cursor = conn.cursor()
            cursor.execute(metrics_query, (
                completed_analysis_id, 1800, 1200, 15000,
                66.7, 8.5, 0.82, 45.2
            ))
            conn.commit()
            cursor.close()
            
            print(f"   ✅ Added metrics for completed analysis")
            
        except Exception as e:
            print(f"   ❌ Failed to add metrics: {e}")
        
        # Test 6: Verify all records
        print("\n6. Checking all video analysis records...")
        try:
            all_records = db.query_to_dict("""
                SELECT va.analysis_id, va.session_id, va.status, va.analysis_type,
                       va.created_at, vm.ball_visibility_percentage
                FROM video_analysis va
                LEFT JOIN video_metrics vm ON va.analysis_id = vm.analysis_id
                ORDER BY va.created_at DESC
            """)
            
            print(f"   Found {len(all_records)} total records:")
            for record in all_records:
                ball_vis = record.get('ball_visibility_percentage', 0) or 0
                print(f"     - {record['analysis_id'][:8]}... | Session {record['session_id']} | {record['status']} | Ball: {ball_vis:.1f}%")
            
            return all_records
                
        except Exception as e:
            print(f"   ❌ Failed to query all records: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    records = fix_and_test_cv_database()
    if records:
        print(f"\n✅ Database operations fixed! Created {len(records)} test records.")
        print("\nYou can now test the computer vision monitor with these analysis IDs:")
        for record in records:
            print(f"  - {record['analysis_id']} ({record['status']})")
    else:
        print("\n❌ Database operations still have issues.")
