#!/usr/bin/env python3
"""
Check player names in database
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
    print("🔍 Checking player names in database...")
    
    try:
        db = DatabaseConnection()
        
        # Get all active players
        players = db.query_to_dict('SELECT nome_completo FROM atletas WHERE ativo = true ORDER BY nome_completo')
        
        print(f"📊 Found {len(players)} active players:")
        print("-" * 40)
        
        for i, player in enumerate(players, 1):
            print(f"{i:2d}. {player['nome_completo']}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
