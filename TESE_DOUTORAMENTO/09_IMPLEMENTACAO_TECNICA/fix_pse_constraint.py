#!/usr/bin/env python3
"""
Fix PSE constraint issue by checking actual constraint and using safe values
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
    print("🔍 Investigating PSE constraint issue...")
    
    try:
        db = DatabaseConnection()
        
        # Check what values currently exist and work
        existing_query = """
            SELECT DISTINCT qualidade_sono, COUNT(*) as count
            FROM dados_pse 
            WHERE qualidade_sono IS NOT NULL
            GROUP BY qualidade_sono
            ORDER BY qualidade_sono
        """
        existing_values = db.query_to_dict(existing_query)
        
        print("📊 Existing sleep quality values that work:")
        print("-" * 50)
        
        for val in existing_values:
            print(f"Value {val['qualidade_sono']}: {val['count']} records")
        
        # Check constraint using pg_get_constraintdef
        constraint_query = """
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint 
            WHERE conname LIKE '%sono%'
        """
        constraints = db.query_to_dict(constraint_query)
        
        print("\n🔧 Constraint definitions:")
        print("-" * 50)
        
        for constraint in constraints:
            print(f"Name: {constraint['conname']}")
            print(f"Definition: {constraint['definition']}")
            print("-" * 30)
        
        # Try inserting a test record to see exact error
        print("\n🧪 Testing with safe values...")
        
        # Use values that we know work from existing data
        if existing_values:
            safe_value = existing_values[0]['qualidade_sono']
            print(f"Using safe value: {safe_value}")
        else:
            print("No existing data found - will use conservative values")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
