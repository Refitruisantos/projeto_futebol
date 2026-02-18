#!/usr/bin/env python3
"""
Check database constraints for PSE data
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
    print("🔍 Checking PSE database constraints...")
    
    try:
        db = DatabaseConnection()
        
        # Check constraint details
        constraint_query = """
            SELECT constraint_name, check_clause 
            FROM information_schema.check_constraints 
            WHERE constraint_name LIKE '%sono%' OR constraint_name LIKE '%pse%'
        """
        constraints = db.query_to_dict(constraint_query)
        
        print("📊 PSE-related constraints:")
        print("-" * 50)
        
        for constraint in constraints:
            print(f"Name: {constraint['constraint_name']}")
            print(f"Rule: {constraint['check_clause']}")
            print("-" * 30)
        
        # Check table structure
        table_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'dados_pse'
            ORDER BY ordinal_position
        """
        columns = db.query_to_dict(table_query)
        
        print("\n📋 dados_pse table structure:")
        print("-" * 50)
        
        for col in columns:
            print(f"{col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
