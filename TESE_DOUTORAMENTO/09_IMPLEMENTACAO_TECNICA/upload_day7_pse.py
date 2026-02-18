#!/usr/bin/env python3
"""
Upload Day 7 PSE data directly to database
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

def upload_day7_pse():
    """Upload Day 7 PSE data for Sunday recovery session"""
    print("🚀 Uploading Day 7 PSE data...")
    
    # File path
    pse_file = Path("simulation_data/Jogo6_sunday_pse.csv")
    session_date = "2025-01-26"
    
    if not pse_file.exists():
        print(f"❌ File not found: {pse_file}")
        return False
    
    try:
        # Read CSV
        df = pd.read_csv(pse_file)
        print(f"📊 Found {len(df)} PSE records")
        
        # Connect to database
        db = DatabaseConnection()
        
        # Get session ID for Day 7
        session_query = """
            SELECT id FROM sessoes 
            WHERE DATE(data) = %s AND jornada = 6
            ORDER BY id DESC LIMIT 1
        """
        sessions = db.query_to_dict(session_query, (session_date,))
        
        if not sessions:
            print(f"❌ No session found for {session_date}")
            print("Make sure you've uploaded the GPS data first!")
            return False
        
        session_id = sessions[0]['id']
        print(f"🎯 Using session ID: {session_id}")
        
        # Get all athletes
        athlete_query = "SELECT id, nome_completo FROM atletas WHERE ativo = true"
        athletes = db.query_to_dict(athlete_query)
        
        # Create athlete mapping (use first N athletes for simulation)
        athlete_list = athletes[:len(df)]  # Take first 28 athletes
        
        inserted = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                if idx >= len(athlete_list):
                    break
                
                athlete_id = athlete_list[idx]['id']
                athlete_name = athlete_list[idx]['nome_completo']
                
                # Normalize values to fit database constraints
                sono = max(1, min(10, int(row['Sono'])))
                stress = max(1, min(5, int(row['Stress'])))
                fadiga = max(1, min(5, int(row['Fadiga'])))
                doms = max(1, min(5, int(row['DOMS'])))
                duracao = int(row['VOLUME'])
                rpe = max(1, min(10, int(row['Rpe'])))
                carga = int(row['CARGA'])
                
                # Insert PSE data
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
                print(f"✅ Inserted PSE data for {athlete_name}")
                
            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        db.close()
        
        print(f"\n📊 Upload Summary:")
        print(f"✅ Inserted: {inserted} PSE records")
        print(f"❌ Errors: {len(errors)}")
        
        if inserted > 0:
            print("🎉 Day 7 PSE data uploaded successfully!")
            print("\n📈 Complete 7-day simulation week is now ready!")
            return True
        else:
            print("⚠️ No PSE data was uploaded")
            return False
        
    except Exception as e:
        print(f"❌ Error processing PSE file: {e}")
        return False

if __name__ == "__main__":
    upload_day7_pse()
