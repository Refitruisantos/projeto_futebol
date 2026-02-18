"""
Fix session linking for video analyses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection

def fix_session_linking():
    """Fix session linking for existing analyses"""
    
    db = DatabaseConnection()
    
    try:
        print("🔧 Fixing session linking for video analyses...\n")
        
        # Get all analyses with null session_id
        print("1. Finding analyses with missing session links...")
        analyses = db.query_to_dict("""
            SELECT analysis_id, session_id, video_path, created_at
            FROM video_analysis 
            WHERE session_id IS NULL
            ORDER BY created_at DESC
        """)
        
        print(f"   Found {len(analyses)} analyses with missing session links")
        
        # Link the completed analysis to session 362
        analysis_id = "3f0ac8ec-c329-4a55-b1a7-8ed5c1ce5ee0"
        session_id = 362
        
        print(f"\n2. Linking analysis {analysis_id[:8]}... to session {session_id}...")
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE video_analysis 
            SET session_id = %s
            WHERE analysis_id = %s
        """, (session_id, analysis_id))
        
        conn.commit()
        cursor.close()
        
        print(f"   ✅ Linked analysis to session {session_id}")
        
        # Verify the link
        print(f"\n3. Verifying session link...")
        result = db.query_to_dict("""
            SELECT analysis_id, session_id, status
            FROM video_analysis 
            WHERE analysis_id = %s
        """, (analysis_id,))
        
        if result:
            analysis = result[0]
            print(f"   ✅ Analysis {analysis_id[:8]}... now linked to session {analysis['session_id']}")
            print(f"   Status: {analysis['status']}")
        
        # Check what analyses are now available for session 362
        print(f"\n4. Checking analyses for session 362...")
        session_analyses = db.query_to_dict("""
            SELECT analysis_id, status, created_at, completed_at
            FROM video_analysis 
            WHERE session_id = %s
            ORDER BY created_at DESC
        """, (session_id,))
        
        print(f"   ✅ Session 362 now has {len(session_analyses)} analyses:")
        for analysis in session_analyses:
            print(f"     - {analysis['analysis_id'][:8]}... | {analysis['status']} | {analysis['created_at']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing session linking: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = fix_session_linking()
    if success:
        print("\n✅ Session linking fixed! The analysis should now appear in the frontend.")
    else:
        print("\n❌ Failed to fix session linking.")
