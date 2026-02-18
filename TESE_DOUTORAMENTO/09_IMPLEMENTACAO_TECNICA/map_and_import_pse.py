#!/usr/bin/env python3
"""
Map simulation PSE data to actual database players and import
"""
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

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
    query = "SELECT id, nome_completo FROM atletas WHERE ativo = true ORDER BY id"
    players = db.query_to_dict(query)
    db.close()
    return players

def create_pse_data_for_players(players, session_date, base_values):
    """Create PSE data for actual database players"""
    db = DatabaseConnection()
    
    # Get session ID
    session_query = """
        SELECT id FROM sessoes 
        WHERE DATE(data) = %s AND jornada = 6
        ORDER BY id DESC LIMIT 1
    """
    sessions = db.query_to_dict(session_query, (session_date,))
    
    if not sessions:
        print(f"❌ No session found for {session_date}")
        return False
    
    session_id = sessions[0]['id']
    print(f"🎯 Using session ID: {session_id} for {session_date}")
    
    inserted = 0
    
    for i, player in enumerate(players):
        try:
            # Vary the values slightly for each player
            sono = base_values['sono'] + (i % 3) - 1  # Vary ±1
            stress = max(1, min(5, base_values['stress'] + (i % 3) - 1))
            fadiga = max(1, min(5, base_values['fadiga'] + (i % 3) - 1))
            doms = max(1, min(5, base_values['doms'] + (i % 3) - 1))
            
            insert_query = """
                INSERT INTO dados_pse (
                    time, atleta_id, sessao_id,
                    qualidade_sono, stress, fadiga, dor_muscular,
                    duracao_min, pse, carga_total,
                    created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """
            
            session_datetime = datetime.strptime(session_date, '%Y-%m-%d')
            
            db.execute_query(insert_query, (
                session_datetime,
                player['id'],
                session_id,
                sono,
                stress,
                fadiga,
                doms,
                base_values['duracao'],
                base_values['rpe'],
                base_values['carga']
            ))
            
            inserted += 1
            
        except Exception as e:
            print(f"Error inserting for {player['nome_completo']}: {e}")
    
    db.close()
    print(f"✅ Inserted {inserted} PSE records for {session_date}")
    return inserted > 0

def main():
    """Create PSE data for simulation week using actual database players"""
    print("🚀 Creating PSE data for actual database players...")
    
    # Get actual players from database
    players = get_database_players()
    print(f"📋 Found {len(players)} active players in database")
    
    # PSE data patterns for each day (realistic progression)
    pse_patterns = [
        # Monday - Recovery
        {"date": "2025-01-20", "sono": 8, "stress": 3, "fadiga": 2, "doms": 2, "duracao": 75, "rpe": 4, "carga": 300},
        # Tuesday - Technical
        {"date": "2025-01-21", "sono": 7, "stress": 4, "fadiga": 3, "doms": 2, "duracao": 90, "rpe": 6, "carga": 540},
        # Wednesday - Tactical
        {"date": "2025-01-22", "sono": 6, "stress": 5, "fadiga": 4, "doms": 4, "duracao": 105, "rpe": 7, "carga": 735},
        # Thursday - Physical
        {"date": "2025-01-23", "sono": 5, "stress": 6, "fadiga": 5, "doms": 5, "duracao": 120, "rpe": 8, "carga": 960},
        # Friday - Pre-match
        {"date": "2025-01-24", "sono": 6, "stress": 5, "fadiga": 4, "doms": 4, "duracao": 60, "rpe": 4, "carga": 240},
        # Saturday - Match
        {"date": "2025-01-25", "sono": 5, "stress": 7, "fadiga": 6, "doms": 5, "duracao": 90, "rpe": 9, "carga": 810},
    ]
    
    success_count = 0
    
    for pattern in pse_patterns:
        if create_pse_data_for_players(players, pattern["date"], pattern):
            success_count += 1
        print("-" * 50)
    
    print(f"📊 Final Summary: {success_count}/{len(pse_patterns)} days completed")
    
    if success_count == len(pse_patterns):
        print("🎉 Complete simulation week PSE data created!")
        print("\n📈 Simulation Week Status:")
        print("✅ GPS data: 6 sessions imported")
        print("✅ PSE data: 6 sessions created")
        print("🎯 Ready for dashboard testing!")
        print("\n🔗 Access your dashboard:")
        print("- Frontend: http://localhost:5173")
        print("- Backend API: http://localhost:8000")

if __name__ == "__main__":
    main()
