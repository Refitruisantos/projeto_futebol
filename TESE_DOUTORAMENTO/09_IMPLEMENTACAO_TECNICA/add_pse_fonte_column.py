#!/usr/bin/env python3
"""
Add fonte column to PSE table to store filenames
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
    print("🔧 Adding fonte column to PSE table...")
    
    try:
        db = DatabaseConnection()
        
        # Add fonte column to dados_pse table
        alter_query = """
            ALTER TABLE dados_pse 
            ADD COLUMN IF NOT EXISTS fonte VARCHAR(255)
        """
        
        db.execute_query(alter_query)
        print("✅ Added 'fonte' column to dados_pse table")
        
        # Verify the column was added
        check_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'dados_pse' AND column_name = 'fonte'
        """
        result = db.query_to_dict(check_query)
        
        if result:
            print("✅ Verified: 'fonte' column exists in dados_pse table")
        else:
            print("❌ Error: 'fonte' column not found after adding")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
