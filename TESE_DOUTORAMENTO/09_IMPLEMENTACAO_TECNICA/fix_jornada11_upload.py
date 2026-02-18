#!/usr/bin/env python3
"""
Direct upload of Jornada 11 data to bypass web interface issues
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

def upload_jornada11_complete():
    """Upload complete Jornada 11 data (GPS + PSE) directly to database"""
    print("🚀 Uploading complete Jornada 11 data...")
    
    # File paths
    gps_file = Path("simulation_data/jornada_11_wednesday_tactical.csv")
    pse_file = Path("simulation_data/Jogo11_wednesday_pse.csv")
    session_date = "2025-02-05"  # Choose your date
    
    if not gps_file.exists():
        print(f"❌ GPS file not found: {gps_file}")
        return False
        
    if not pse_file.exists():
        print(f"❌ PSE file not found: {pse_file}")
        return False
    
    try:
        # Read CSV files
        gps_df = pd.read_csv(gps_file)
        pse_df = pd.read_csv(pse_file)
        print(f"📊 GPS: {len(gps_df)} records, PSE: {len(pse_df)} records")
        
        # Connect to database
        db = DatabaseConnection()
        
        # Create session first
        session_insert = """
            INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao, created_at)
            VALUES (%s, 'treino', 105, 11, 'Tactical Training', NOW())
            RETURNING id
        """
        
        db.execute_query(session_insert, (datetime.strptime(session_date, '%Y-%m-%d'),))
        
        # Get the created session ID
        session_query = """
            SELECT id FROM sessoes 
            WHERE jornada = 11 AND DATE(data) = %s
            ORDER BY created_at DESC LIMIT 1
        """
        sessions = db.query_to_dict(session_query, (session_date,))
        
        if not sessions:
            print("❌ Failed to create session")
            return False
            
        session_id = sessions[0]['id']
        print(f"✅ Created session {session_id} for Jornada 11")
        
        # Get all active athletes
        athlete_query = "SELECT id, nome_completo FROM atletas WHERE ativo = true ORDER BY id"
        athletes = db.query_to_dict(athlete_query)
        print(f"📋 Found {len(athletes)} active athletes")
        
        # Upload GPS data
        gps_inserted = 0
        athlete_list = athletes[:len(gps_df)]  # Match CSV rows to athletes
        
        for idx, row in gps_df.iterrows():
            try:
                if idx >= len(athlete_list):
                    break
                    
                athlete_id = athlete_list[idx]['id']
                athlete_name = athlete_list[idx]['nome_completo']
                
                gps_insert = """
                    INSERT INTO dados_gps (
                        time, atleta_id, sessao_id,
                        distancia_total, velocidade_max,
                        aceleracoes, desaceleracoes,
                        effs_19_8_kmh, dist_19_8_kmh,
                        effs_25_2_kmh,
                        fonte, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                """
                
                db.execute_query(gps_insert, (
                    datetime.strptime(session_date, '%Y-%m-%d'),
                    athlete_id,
                    session_id,
                    float(row['total_distance_m']),
                    float(row['max_velocity_kmh']),
                    int(row['acc_b1_3_total_efforts']),
                    int(row['decel_b1_3_total_efforts']),
                    int(row['efforts_over_19_8_kmh']),
                    float(row['distance_over_19_8_kmh']),
                    int(row['efforts_over_25_2_kmh']),
                    'jornada11_direct_upload'
                ))
                
                gps_inserted += 1
                
            except Exception as e:
                print(f"❌ GPS error for {athlete_name}: {e}")
        
        print(f"✅ Inserted {gps_inserted} GPS records")
        
        # Upload PSE data
        pse_inserted = 0
        
        for idx, row in pse_df.iterrows():
            try:
                if idx >= len(athlete_list):
                    break
                    
                athlete_id = athlete_list[idx]['id']
                athlete_name = athlete_list[idx]['nome_completo']
                
                # Normalize values to fit constraints
                sono = max(1, min(10, int(row['Sono'])))
                stress = max(1, min(5, int(row['Stress'])))
                fadiga = max(1, min(5, int(row['Fadiga'])))
                doms = max(1, min(5, int(row['DOMS'])))
                rpe = max(1, min(10, int(row['Rpe'])))
                duracao = int(row['VOLUME'])
                carga = int(row['CARGA'])
                
                pse_insert = """
                    INSERT INTO dados_pse (
                        time, atleta_id, sessao_id,
                        qualidade_sono, stress, fadiga, dor_muscular,
                        duracao_min, pse, carga_total,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                """
                
                db.execute_query(pse_insert, (
                    datetime.strptime(session_date, '%Y-%m-%d'),
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
                
                pse_inserted += 1
                
            except Exception as e:
                print(f"❌ PSE error for {athlete_name}: {e}")
        
        print(f"✅ Inserted {pse_inserted} PSE records")
        
        db.close()
        
        print(f"\n🎉 Jornada 11 Upload Complete!")
        print(f"📊 Session ID: {session_id}")
        print(f"📊 GPS Records: {gps_inserted}")
        print(f"📊 PSE Records: {pse_inserted}")
        print(f"📅 Date: {session_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading Jornada 11: {e}")
        return False

if __name__ == "__main__":
    upload_jornada11_complete()
