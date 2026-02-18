"""
Test computer vision database operations directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection
import uuid

def test_cv_database_operations():
    """Test CV database operations"""
    
    db = DatabaseConnection()
    
    try:
        print("🔍 Testing computer vision database operations...\n")
        
        # Test 1: Check if video_analysis table exists
        print("1. Checking video_analysis table...")
        try:
            result = db.execute_query("""
                SELECT COUNT(*) FROM video_analysis
            """)
            print(f"   ✅ video_analysis table exists with {result[0][0]} records")
        except Exception as e:
            print(f"   ❌ video_analysis table issue: {e}")
            return False
        
        # Test 2: Try inserting a test record
        print("\n2. Testing record insertion...")
        analysis_id = str(uuid.uuid4())
        session_id = 360  # Use the session we created earlier
        
        try:
            insert_query = """
                INSERT INTO video_analysis (
                    analysis_id, session_id, video_path, analysis_type,
                    confidence_threshold, sample_rate, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            db.execute_query(insert_query, (
                analysis_id, session_id, "test_video.mp4", "quick",
                0.5, 10, "queued"
            ))
            
            print(f"   ✅ Record inserted with analysis_id: {analysis_id}")
            
        except Exception as e:
            print(f"   ❌ Insert failed: {e}")
            print(f"   Error type: {type(e)}")
            return False
        
        # Test 3: Verify the record was inserted
        print("\n3. Verifying record insertion...")
        try:
            query = """
                SELECT analysis_id, session_id, status, created_at
                FROM video_analysis 
                WHERE analysis_id = %s
            """
            
            result = db.execute_query(query, (analysis_id,))
            
            if result and len(result) > 0:
                print(f"   ✅ Record found: {result[0]}")
            else:
                print(f"   ❌ Record not found after insertion")
                return False
                
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            return False
        
        # Test 4: Check all records in video_analysis
        print("\n4. Checking all video_analysis records...")
        try:
            all_records = db.execute_query("""
                SELECT analysis_id, session_id, status, created_at
                FROM video_analysis
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            print(f"   Found {len(all_records)} total records:")
            for record in all_records:
                print(f"     - {record[0][:8]}... | Session {record[1]} | {record[2]} | {record[3]}")
                
        except Exception as e:
            print(f"   ❌ Failed to query all records: {e}")
        
        # Test 5: Test the execute_query method specifically
        print("\n5. Testing execute_query method behavior...")
        try:
            # Test with a simple query
            test_result = db.execute_query("SELECT NOW()")
            print(f"   ✅ execute_query works: {test_result}")
            
            # Test with parameters
            param_result = db.execute_query("SELECT %s as test_param", ("test_value",))
            print(f"   ✅ execute_query with params works: {param_result}")
            
        except Exception as e:
            print(f"   ❌ execute_query method issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_cv_database_operations()
    if success:
        print("\n✅ Database operations working correctly!")
        print("The issue might be in the API endpoint error handling.")
    else:
        print("\n❌ Database operations have issues that need fixing.")
