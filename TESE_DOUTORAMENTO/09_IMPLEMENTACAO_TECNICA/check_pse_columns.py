#!/usr/bin/env python3
"""
Check PSE table structure to see available columns
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
    print("🔍 Checking PSE table structure...")
    
    try:
        db = DatabaseConnection()
        
        # Check PSE table columns
        columns_query = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'dados_pse'
            ORDER BY ordinal_position
        """
        columns = db.query_to_dict(columns_query)
        
        print("📊 PSE table columns:")
        print("-" * 40)
        
        for col in columns:
            print(f"- {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check if there's a fonte/source field
        has_fonte = any(col['column_name'] == 'fonte' for col in columns)
        print(f"\n📋 Has 'fonte' field: {has_fonte}")
        
        if not has_fonte:
            print("❌ PSE table missing 'fonte' field - need to add filename storage")
        else:
            print("✅ PSE table has 'fonte' field - can store filenames")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
