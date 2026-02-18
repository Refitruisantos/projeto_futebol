#!/usr/bin/env python3
"""
Check player names in CSV files against database - helps prepare real data uploads
"""
import sys
import pandas as pd
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

def get_all_database_players():
    """Get all players from database with details"""
    try:
        db = DatabaseConnection()
        query = """
            SELECT nome_completo, jogador_id, posicao, ativo 
            FROM atletas 
            ORDER BY ativo DESC, nome_completo
        """
        players = db.query_to_dict(query)
        db.close()
        return players
    except Exception as e:
        print(f"❌ Error getting database players: {e}")
        return []

def check_csv_player_names(csv_file, name_column='player'):
    """Check if CSV player names match database"""
    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        return
    
    try:
        df = pd.read_csv(csv_file)
        
        # Determine name column
        if name_column not in df.columns:
            if 'Nome' in df.columns:
                name_column = 'Nome'
            elif 'player' in df.columns:
                name_column = 'player'
            else:
                print(f"❌ No player name column found. Expected 'player' or 'Nome'")
                return
        
        print(f"📊 Checking {len(df)} players from {csv_file}")
        print(f"🔍 Using column: {name_column}")
        
        # Get database players
        db_players = get_all_database_players()
        if not db_players:
            print("❌ Could not retrieve database players")
            return
        
        # Create lookup sets
        db_names = set()
        db_lookup = {}
        
        for player in db_players:
            name = player['nome_completo'].strip()
            db_names.add(name.upper())
            db_lookup[name.upper()] = player
            
            if player['jogador_id']:
                id_name = player['jogador_id'].strip()
                db_names.add(id_name.upper())
                db_lookup[id_name.upper()] = player
        
        # Check each CSV name
        matches = []
        no_matches = []
        
        for idx, row in df.iterrows():
            csv_name = str(row[name_column]).strip()
            csv_name_upper = csv_name.upper()
            
            if csv_name_upper in db_names:
                db_player = db_lookup[csv_name_upper]
                matches.append({
                    'csv_name': csv_name,
                    'db_name': db_player['nome_completo'],
                    'position': db_player['posicao'],
                    'active': db_player['ativo']
                })
            else:
                no_matches.append(csv_name)
        
        # Report results
        print(f"\n✅ MATCHES FOUND: {len(matches)}")
        print("-" * 50)
        for match in matches:
            status = "✅ Active" if match['active'] else "⚠️ Inactive"
            print(f"{match['csv_name']} → {match['db_name']} ({match['position']}) {status}")
        
        if no_matches:
            print(f"\n❌ NO MATCHES FOUND: {len(no_matches)}")
            print("-" * 50)
            for name in no_matches:
                print(f"❌ {name}")
            
            print(f"\n💡 SUGGESTIONS:")
            print("Available database players:")
            for player in db_players[:20]:  # Show first 20
                status = "Active" if player['ativo'] else "Inactive"
                print(f"   - {player['nome_completo']} ({player['posicao']}) [{status}]")
            
            if len(db_players) > 20:
                print(f"   ... and {len(db_players) - 20} more players")
        
        print(f"\n📊 SUMMARY:")
        print(f"Total CSV players: {len(df)}")
        print(f"Matched: {len(matches)}")
        print(f"Unmatched: {len(no_matches)}")
        print(f"Match rate: {len(matches)/len(df)*100:.1f}%")
        
        if len(matches) == len(df):
            print("🎉 All player names match! Ready for upload.")
        else:
            print("⚠️ Some names need correction before upload.")
        
    except Exception as e:
        print(f"❌ Error checking player names: {e}")

def list_all_database_players():
    """List all players in database for reference"""
    players = get_all_database_players()
    
    if not players:
        print("❌ Could not retrieve database players")
        return
    
    print(f"📋 DATABASE PLAYERS ({len(players)} total)")
    print("=" * 70)
    print(f"{'Name':<25} {'Position':<10} {'Player ID':<15} {'Status':<10}")
    print("-" * 70)
    
    for player in players:
        name = player['nome_completo'][:24]  # Truncate long names
        pos = player['posicao'] or 'N/A'
        player_id = player['jogador_id'] or 'N/A'
        status = "Active" if player['ativo'] else "Inactive"
        
        print(f"{name:<25} {pos:<10} {player_id:<15} {status:<10}")

def main():
    """Main function for player name checking"""
    if len(sys.argv) < 2:
        print("🔍 Player Name Checker")
        print("=" * 50)
        print("Usage:")
        print("  python check_player_names.py <csv_file>     # Check CSV against database")
        print("  python check_player_names.py --list         # List all database players")
        print("")
        print("Examples:")
        print("  python check_player_names.py gps_2025-03-15_training.csv")
        print("  python check_player_names.py pse_2025-03-15_training.csv")
        print("  python check_player_names.py --list")
        return
    
    if sys.argv[1] == "--list":
        list_all_database_players()
    else:
        csv_file = sys.argv[1]
        check_csv_player_names(csv_file)

if __name__ == "__main__":
    main()
