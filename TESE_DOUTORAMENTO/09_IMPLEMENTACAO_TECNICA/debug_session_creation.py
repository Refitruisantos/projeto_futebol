#!/usr/bin/env python3
"""
Debug session creation to see why sessions aren't being created
"""
import sys
from pathlib import Path
from datetime import datetime, date

# Add python/ folder to system path for DB connection
parent_dir = Path(__file__).resolve().parent
python_dir = parent_dir / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

import importlib.util
module_path = python_dir / "01_conexao_db.py"
spec = importlib.util.spec_from_file_location("conexao_db", module_path)
conexao_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conexao_db)
DatabaseConnection = conexao_db.DatabaseConnection

def test_session_creation():
    print("🔍 Testing session creation...")
    
    try:
        db = DatabaseConnection()
        
        # Test parameters
        jornada = 26
        session_date = date(2025, 6, 30)
        filename = "jornada26_day1_recovery.csv"
        
        print(f"Testing with: jornada={jornada}, date={session_date}, filename={filename}")
        
        # Check for existing session first
        check_query = """
            SELECT id FROM sessoes
            WHERE jornada = %s AND data = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        existing = db.query_to_dict(check_query, (jornada, session_date))
        
        if existing:
            print(f"✅ Found existing session: {existing[0]['id']}")
            return existing[0]['id']
        
        print("📝 No existing session found, creating new one...")
        
        # Extract training type from filename
        training_type = "treino"  # default
        description = "Training Session"  # default
        
        if filename:
            filename_lower = filename.lower()
            if "recovery" in filename_lower:
                training_type = "recuperacao"
                description = "Recovery Training"
            elif "match" in filename_lower:
                training_type = "jogo"
                description = "Match"
            elif any(word in filename_lower for word in ["technical", "tactical", "physical", "prematch"]):
                training_type = "treino"
                if "technical" in filename_lower:
                    description = "Technical Training"
                elif "tactical" in filename_lower:
                    description = "Tactical Training"
                elif "physical" in filename_lower:
                    description = "Physical Training"
                elif "prematch" in filename_lower:
                    description = "Pre-Match Training"
        
        print(f"📊 Session details: type='{training_type}', description='{description}'")
        
        # Try to create session
        insert_query = """
            INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao, created_at)
            VALUES (%s, %s, 90, %s, %s, NOW())
            RETURNING id
        """
        
        print("🔧 Executing insert query...")
        result = db.query_to_dict(insert_query, (session_date, training_type, jornada, description))
        
        if result:
            session_id = result[0]['id']
            print(f"✅ Session created successfully: ID {session_id}")
            
            # Verify it exists
            verify_query = "SELECT * FROM sessoes WHERE id = %s"
            verify_result = db.query_to_dict(verify_query, (session_id,))
            
            if verify_result:
                session = verify_result[0]
                print(f"✅ Session verified in database:")
                print(f"   ID: {session['id']}")
                print(f"   Date: {session['data']}")
                print(f"   Type: {session['tipo']}")
                print(f"   Jornada: {session['jornada']}")
                print(f"   Description: {session['competicao']}")
            else:
                print("❌ Session not found after creation!")
            
            return session_id
        else:
            print("❌ Session creation failed - no result returned")
            return None
        
    except Exception as e:
        print(f"❌ Error during session creation: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if 'db' in locals():
            db.close()

def main():
    print("🧪 SESSION CREATION DEBUG TEST")
    print("=" * 40)
    
    session_id = test_session_creation()
    
    if session_id:
        print(f"\n🎉 Session creation successful: ID {session_id}")
    else:
        print(f"\n❌ Session creation failed")

if __name__ == "__main__":
    main()
