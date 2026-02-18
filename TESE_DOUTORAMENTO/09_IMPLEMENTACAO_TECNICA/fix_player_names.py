#!/usr/bin/env python3
"""
Fix player names in all rounds files to match database
"""
import csv
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

def get_database_players():
    """Get actual player names from database"""
    db = DatabaseConnection()
    players = db.query_to_dict('SELECT nome_completo FROM atletas WHERE ativo = true ORDER BY nome_completo')
    db.close()
    return [p['nome_completo'] for p in players]

def fix_gps_files():
    """Fix all GPS files with correct player names"""
    db_players = get_database_players()
    rounds_dir = Path("rounds")
    
    # Find all GPS CSV files
    gps_files = list(rounds_dir.glob("jornada*_day*.csv"))
    gps_files = [f for f in gps_files if not f.name.endswith('_pse.csv')]
    
    print(f"🔧 Fixing {len(gps_files)} GPS files...")
    
    for gps_file in gps_files:
        try:
            # Read existing file
            with open(gps_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                rows = list(reader)
            
            # Update player names
            for i, row in enumerate(rows):
                if i < len(db_players):
                    row[0] = db_players[i]  # Replace first column (player name)
            
            # Write back to file
            with open(gps_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            
            print(f"✅ Fixed {gps_file.name}")
            
        except Exception as e:
            print(f"❌ Error fixing {gps_file.name}: {e}")

def fix_pse_files():
    """Fix all PSE files with correct player names"""
    db_players = get_database_players()
    rounds_dir = Path("rounds")
    
    # Find all PSE CSV files
    pse_files = list(rounds_dir.glob("*_pse.csv"))
    
    print(f"🔧 Fixing {len(pse_files)} PSE files...")
    
    for pse_file in pse_files:
        try:
            # Read existing file
            with open(pse_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                rows = list(reader)
            
            # Update player names
            for i, row in enumerate(rows):
                if i < len(db_players):
                    row[0] = db_players[i]  # Replace first column (Nome)
            
            # Write back to file
            with open(pse_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            
            print(f"✅ Fixed {pse_file.name}")
            
        except Exception as e:
            print(f"❌ Error fixing {pse_file.name}: {e}")

def main():
    print("🔧 FIXING PLAYER NAMES IN ALL ROUNDS FILES")
    print("=" * 50)
    
    try:
        # Get database players
        db_players = get_database_players()
        print(f"📊 Database has {len(db_players)} active players")
        
        # Fix GPS files
        fix_gps_files()
        
        # Fix PSE files  
        fix_pse_files()
        
        print("\n🎉 All files updated with correct player names!")
        print("📤 Ready for successful manual upload!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
