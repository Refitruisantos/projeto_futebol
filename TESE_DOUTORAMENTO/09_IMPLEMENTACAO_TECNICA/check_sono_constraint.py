#!/usr/bin/env python3
"""
Check the exact constraint definition for qualidade_sono
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
    print("🔍 Checking qualidade_sono constraint...")
    
    try:
        db = DatabaseConnection()
        
        # Check constraint definition
        constraint_query = """
            SELECT conname, consrc 
            FROM pg_constraint 
            WHERE conname LIKE '%sono%'
        """
        constraints = db.query_to_dict(constraint_query)
        
        print("📊 Sleep quality constraints:")
        print("-" * 50)
        
        for constraint in constraints:
            print(f"Name: {constraint['conname']}")
            print(f"Definition: {constraint['consrc']}")
            print("-" * 30)
        
        # Check existing PSE data to see what values work
        existing_query = """
            SELECT DISTINCT qualidade_sono 
            FROM dados_pse 
            WHERE qualidade_sono IS NOT NULL
            ORDER BY qualidade_sono
            LIMIT 20
        """
        existing_values = db.query_to_dict(existing_query)
        
        print("\n📋 Existing sleep quality values in database:")
        print("-" * 50)
        
        values = [str(v['qualidade_sono']) for v in existing_values]
        print(f"Valid values: {', '.join(values)}")
        
        # Try to insert a test value to see what happens
        print("\n🧪 Testing constraint with different values...")
        
        test_values = [1, 5, 10, 11, 0]
        for val in test_values:
            try:
                test_query = f"SELECT CASE WHEN {val} >= 1 AND {val} <= 10 THEN 'VALID' ELSE 'INVALID' END as result"
                result = db.query_to_dict(test_query)
                print(f"Value {val}: {result[0]['result']}")
            except Exception as e:
                print(f"Value {val}: ERROR - {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
