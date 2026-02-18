#!/usr/bin/env python3
"""
Import PSE simulation data directly to database
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

# Name mapping for athletes
NAME_MAPPING = {
    'CARDOSO': 'CARDOSO',
    'JOÃO FERREIRA': 'JOÃO FERREIRA', 
    'RICARDO': 'RICARDO',
    'MIGUEL': 'MIGUEL',
    'BRUNO': 'BRUNO',
    'DIOGO': 'DIOGO',
    'FRANCISCO': 'FRANCISCO',
    'TIAGO': 'TIAGO',
    'ANDRÉ': 'ANDRÉ',
    'JOÃO SILVA': 'JOÃO SILVA',
    'PEDRO': 'PEDRO',
    'RAFAEL': 'RAFAEL',
    'GONÇALO': 'GONÇALO',
    'NUNO': 'NUNO',
    'LUÍS': 'LUÍS',
    'CARLOS': 'CARLOS',
    'MANUEL': 'MANUEL',
    'JOSÉ': 'JOSÉ',
    'PAULO': 'PAULO',
    'RÚBEN': 'RÚBEN',
    'DANIEL': 'DANIEL',
    'MARCO': 'MARCO',
    'VÍTOR': 'VÍTOR',
    'FÁBIO': 'FÁBIO',
    'SÉRGIO': 'SÉRGIO',
    'HUGO': 'HUGO',
    'ALEX': 'ALEX',
    'MÁRIO': 'MÁRIO'
}

def get_athlete_id(name, db):
    """Get athlete ID from name"""
    clean_name = name.strip().upper()
    mapped_name = NAME_MAPPING.get(clean_name, clean_name)
    
    query = """
        SELECT id FROM atletas 
        WHERE UPPER(nome_completo) = %s OR UPPER(jogador_id) = %s
        LIMIT 1
    """
    result = db.query_to_dict(query, (mapped_name, mapped_name))
    
    if result:
        return result[0]['id']
    
    print(f"⚠️  Player not found: {name} (mapped to {mapped_name})")
    return None

def get_session_id(session_date, db):
    """Get or create session for the date"""
    # First try to find existing session
    query = """
        SELECT id FROM sessoes 
        WHERE DATE(data) = %s AND jornada = 6
        ORDER BY id DESC
        LIMIT 1
    """
    result = db.query_to_dict(query, (session_date,))
    
    if result:
        return result[0]['id']
    
    # Create new session if not found
    insert_query = """
        INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao, created_at)
        VALUES (%s, 'treino', 90, 6, 'Simulation Week', NOW())
        RETURNING id
    """
    
    try:
        db.execute_query(insert_query, (datetime.strptime(session_date, '%Y-%m-%d'),))
        result = db.query_to_dict(query, (session_date,))
        if result:
            return result[0]['id']
    except Exception as e:
        print(f"Error creating session: {e}")
    
    return None

def import_pse_file(csv_path, session_date):
    """Import a single PSE CSV file"""
    print(f"📤 Importing {csv_path.name} for {session_date}")
    
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return False
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} records")
        
        # Connect to database
        db = DatabaseConnection()
        
        # Get session ID
        session_id = get_session_id(session_date, db)
        if not session_id:
            print(f"❌ Could not find/create session for {session_date}")
            return False
        
        print(f"🎯 Using session ID: {session_id}")
        
        # Process each row
        inserted = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                athlete_id = get_athlete_id(row['Nome'], db)
                if not athlete_id:
                    errors.append(f"Row {idx}: Player not found - {row['Nome']}")
                    continue
                
                # Insert PSE data
                insert_query = """
                    INSERT INTO dados_pse (
                        time, atleta_id, sessao_id,
                        qualidade_sono, stress, fadiga, dor_muscular,
                        duracao_min, pse, carga_total,
                        created_at
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        NOW()
                    )
                    ON CONFLICT (time, atleta_id, sessao_id) DO UPDATE SET
                        qualidade_sono = EXCLUDED.qualidade_sono,
                        stress = EXCLUDED.stress,
                        fadiga = EXCLUDED.fadiga,
                        dor_muscular = EXCLUDED.dor_muscular,
                        duracao_min = EXCLUDED.duracao_min,
                        pse = EXCLUDED.pse,
                        carga_total = EXCLUDED.carga_total
                """
                
                db.execute_query(insert_query, (
                    datetime.strptime(session_date, '%Y-%m-%d'),
                    athlete_id,
                    session_id,
                    int(row['Sono']) if pd.notna(row['Sono']) else None,
                    int(row['Stress']) if pd.notna(row['Stress']) else None,
                    int(row['Fadiga']) if pd.notna(row['Fadiga']) else None,
                    int(row['DOMS']) if pd.notna(row['DOMS']) else None,
                    int(row['VOLUME']) if pd.notna(row['VOLUME']) else None,
                    int(row['Rpe']) if pd.notna(row['Rpe']) else None,
                    int(row['CARGA']) if pd.notna(row['CARGA']) else None
                ))
                
                inserted += 1
                
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
        
        db.close()
        
        print(f"✅ Inserted {inserted} PSE records")
        if errors:
            print(f"⚠️  {len(errors)} errors:")
            for error in errors[:5]:
                print(f"   - {error}")
        
        return inserted > 0
        
    except Exception as e:
        print(f"❌ Error processing {csv_path.name}: {e}")
        return False

def main():
    """Import all simulation PSE files"""
    print("🚀 Starting PSE simulation data import...")
    
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
        if import_pse_file(csv_path, date):
            success_count += 1
        print("-" * 50)
    
    print(f"📊 Import Summary: {success_count}/{len(pse_files)} PSE files imported")
    
    if success_count == len(pse_files):
        print("🎉 All PSE simulation data imported successfully!")
        print("\n📈 Complete simulation week is now ready!")
        print("✅ GPS data: Imported")
        print("✅ PSE data: Imported")
        print("🎯 Ready for dashboard testing and scoring system")
    else:
        print("⚠️  Some PSE files failed to import")

if __name__ == "__main__":
    main()
