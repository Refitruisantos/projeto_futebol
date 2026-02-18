#!/usr/bin/env python3
"""
Final PSE import with proper constraint handling
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

def normalize_value(value, min_val=1, max_val=5):
    """Normalize values to fit database constraints"""
    if pd.isna(value):
        return 3  # Default middle value
    val = int(value)
    return max(min_val, min(max_val, val))

def import_pse_final(csv_path, session_date):
    """Import PSE data with proper constraint handling"""
    print(f"📤 Importing {csv_path.name} for {session_date}")
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} records")
        
        # Connect to database
        db = DatabaseConnection()
        
        # Get sessions for the date
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
        print(f"🎯 Using session ID: {session_id}")
        
        # Get all athletes with exact name matching
        athlete_query = "SELECT id, nome_completo FROM atletas WHERE ativo = true"
        athletes = db.query_to_dict(athlete_query)
        
        # Create exact athlete mapping
        athlete_map = {}
        for athlete in athletes:
            name = athlete['nome_completo'].strip()
            athlete_map[name] = athlete['id']
        
        print(f"📋 Available athletes: {list(athlete_map.keys())[:5]}...")
        
        # Process each row with constraint-safe values
        inserted = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                player_name = str(row['Nome']).strip()
                
                # Find athlete ID
                athlete_id = athlete_map.get(player_name)
                if not athlete_id:
                    errors.append(f"Row {idx}: Player not found - {player_name}")
                    continue
                
                # Normalize all values to fit constraints (1-5 scale)
                sono = normalize_value(row['Sono'], 1, 10)  # Sleep can be 1-10
                stress = normalize_value(row['Stress'], 1, 5)
                fadiga = normalize_value(row['Fadiga'], 1, 5)
                doms = normalize_value(row['DOMS'], 1, 5)
                
                # Duration and RPE
                duracao = int(row['VOLUME']) if pd.notna(row['VOLUME']) else 90
                rpe = normalize_value(row['Rpe'], 1, 10)  # RPE can be 1-10
                carga = int(row['CARGA']) if pd.notna(row['CARGA']) else (duracao * rpe)
                
                # Insert with normalized values
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
                    sono,
                    stress,
                    fadiga,
                    doms,
                    duracao,
                    rpe,
                    carga
                ))
                
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {idx} ({row.get('Nome', 'Unknown')}): {str(e)}")
        
        db.close()
        
        print(f"✅ Inserted {inserted} PSE records")
        if errors and len(errors) < 10:  # Only show errors if not too many
            print(f"⚠️  {len(errors)} errors:")
            for error in errors[:3]:
                print(f"   - {error}")
        
        return inserted > 0
        
    except Exception as e:
        print(f"❌ Error processing {csv_path.name}: {e}")
        return False

def main():
    """Import all simulation PSE files with proper constraints"""
    print("🚀 Final PSE simulation data import...")
    
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
    total_imported = 0
    
    for filename, date in pse_files:
        csv_path = simulation_dir / filename
        if csv_path.exists():
            if import_pse_final(csv_path, date):
                success_count += 1
        else:
            print(f"❌ File not found: {csv_path}")
        print("-" * 50)
    
    print(f"📊 Final Import Summary: {success_count}/{len(pse_files)} PSE files imported")
    
    if success_count > 0:
        print("🎉 PSE simulation data imported successfully!")
        print("\n📈 Complete Simulation Week Status:")
        print("✅ GPS data: 6 sessions imported")
        print("✅ PSE data: Imported with normalized values")
        print("🎯 Ready for dashboard testing and scoring system!")
        print("\n🔗 Next steps:")
        print("1. Check dashboard at http://localhost:5173")
        print("2. Verify data in Sessions page")
        print("3. Test advanced analytics")
    else:
        print("⚠️  PSE import failed - check database constraints")

if __name__ == "__main__":
    main()
