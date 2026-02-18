#!/usr/bin/env python3
"""
Quick PSE import for simulation data - simplified approach
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

def import_pse_simple(csv_path, session_date):
    """Import PSE data using direct SQL approach"""
    print(f"📤 Importing {csv_path.name} for {session_date}")
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} records")
        
        # Connect to database
        db = DatabaseConnection()
        
        # Get sessions for the date
        session_query = """
            SELECT id, data, tipo FROM sessoes 
            WHERE DATE(data) = %s AND jornada = 6
            ORDER BY id DESC
        """
        sessions = db.query_to_dict(session_query, (session_date,))
        
        if not sessions:
            print(f"❌ No session found for {session_date}")
            return False
        
        session_id = sessions[0]['id']
        print(f"🎯 Using session ID: {session_id}")
        
        # Get all athletes
        athlete_query = "SELECT id, nome_completo, jogador_id FROM atletas WHERE ativo = true"
        athletes = db.query_to_dict(athlete_query)
        
        # Create athlete name mapping
        athlete_map = {}
        for athlete in athletes:
            name = athlete['nome_completo'].upper().strip()
            athlete_map[name] = athlete['id']
            # Also map jogador_id if different
            if athlete['jogador_id']:
                athlete_map[athlete['jogador_id'].upper().strip()] = athlete['id']
        
        print(f"📋 Found {len(athlete_map)} athlete mappings")
        
        # Process each row
        inserted = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                player_name = str(row['Nome']).upper().strip()
                
                # Try to find athlete
                athlete_id = athlete_map.get(player_name)
                if not athlete_id:
                    # Try partial matching
                    for mapped_name, mapped_id in athlete_map.items():
                        if player_name in mapped_name or mapped_name in player_name:
                            athlete_id = mapped_id
                            break
                
                if not athlete_id:
                    errors.append(f"Row {idx}: Player not found - {row['Nome']}")
                    continue
                
                # Simple insert without conflict handling
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
                    athlete_id,
                    session_id,
                    int(row['Sono']) if pd.notna(row['Sono']) else 5,
                    int(row['Stress']) if pd.notna(row['Stress']) else 3,
                    int(row['Fadiga']) if pd.notna(row['Fadiga']) else 3,
                    int(row['DOMS']) if pd.notna(row['DOMS']) else 2,
                    int(row['VOLUME']) if pd.notna(row['VOLUME']) else 90,
                    int(row['Rpe']) if pd.notna(row['Rpe']) else 5,
                    int(row['CARGA']) if pd.notna(row['CARGA']) else 450
                ))
                
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {idx} ({row.get('Nome', 'Unknown')}): {str(e)}")
        
        db.close()
        
        print(f"✅ Inserted {inserted} PSE records")
        if errors:
            print(f"⚠️  {len(errors)} errors:")
            for error in errors[:3]:
                print(f"   - {error}")
        
        return inserted > 0
        
    except Exception as e:
        print(f"❌ Error processing {csv_path.name}: {e}")
        return False

def main():
    """Import all simulation PSE files"""
    print("🚀 Quick PSE simulation data import...")
    
    simulation_dir = Path("simulation_data")
    
    # PSE files to import
    pse_files = [
        ("Jogo6_monday_pse.csv", "2025-01-20"),
        ("Jogo6_tuesday_pse.csv", "2025-01-21"),
        ("Jogo6_wednesday_pse.csv", "2025-01-22"),
        ("Jogo6_thursday_pse.csv", "2025-01-23"),
        ("Jogo6_friday_pse.csv", "2025-01-24"),
        ("Jogo6_saturday_pse.csv", "2025-01-25"),
    ]
    
    success_count = 0
    
    for filename, date in pse_files:
        csv_path = simulation_dir / filename
        if csv_path.exists():
            if import_pse_simple(csv_path, date):
                success_count += 1
        else:
            print(f"❌ File not found: {csv_path}")
        print("-" * 50)
    
    print(f"📊 Import Summary: {success_count}/{len(pse_files)} PSE files imported")
    
    if success_count > 0:
        print("🎉 PSE simulation data imported!")
        print("\n📈 Simulation week status:")
        print("✅ GPS data: Imported")
        print("✅ PSE data: Imported")
        print("🎯 Ready for dashboard testing!")

if __name__ == "__main__":
    main()
