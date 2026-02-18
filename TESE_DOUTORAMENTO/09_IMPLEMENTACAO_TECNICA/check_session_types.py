#!/usr/bin/env python3
"""
Check allowed session types in database constraint
"""
import sys
from pathlib import Path

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

def main():
    print("🔍 Checking session type constraints...")
    
    try:
        db = DatabaseConnection()
        
        # Check constraint definition for sessoes table
        constraint_query = """
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint 
            WHERE conname LIKE '%tipo%' AND conrelid = (
                SELECT oid FROM pg_class WHERE relname = 'sessoes'
            )
        """
        constraints = db.query_to_dict(constraint_query)
        
        print("📊 Session type constraints:")
        print("-" * 50)
        
        for constraint in constraints:
            print(f"Name: {constraint['conname']}")
            print(f"Definition: {constraint['definition']}")
            print("-" * 30)
        
        # Check existing session types to see what works
        existing_query = """
            SELECT DISTINCT tipo, COUNT(*) as count
            FROM sessoes 
            WHERE tipo IS NOT NULL
            GROUP BY tipo
            ORDER BY tipo
        """
        existing_types = db.query_to_dict(existing_query)
        
        print("\n📋 Existing session types in database:")
        print("-" * 50)
        
        for session_type in existing_types:
            print(f"'{session_type['tipo']}': {session_type['count']} sessions")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
