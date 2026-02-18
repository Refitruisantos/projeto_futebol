#!/usr/bin/env python3
"""
Complete Day 7 upload with proper GPS and PSE data using actual database players
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

def complete_day7_data():
    """Complete Day 7 GPS and PSE data upload using actual database players"""
    print("🚀 Completing Day 7 data upload...")
    
    session_date = "2025-01-26"
    
    try:
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
            return False
        
        session_id = sessions[0]['id']
        print(f"🎯 Using session ID: {session_id}")
        
        # Get all active athletes
        athlete_query = "SELECT id, nome_completo FROM atletas WHERE ativo = true ORDER BY id"
        athletes = db.query_to_dict(athlete_query)
        print(f"📋 Found {len(athletes)} active athletes")
        
        # Add missing GPS data for players not yet imported
        gps_inserted = 0
        pse_inserted = 0
        
        for i, athlete in enumerate(athletes):
            try:
                athlete_id = athlete['id']
                athlete_name = athlete['nome_completo']
                
                # Check if GPS data already exists
                gps_check = """
                    SELECT COUNT(*) as count FROM dados_gps 
                    WHERE atleta_id = %s AND sessao_id = %s
                """
                gps_exists = db.query_to_dict(gps_check, (athlete_id, session_id))
                
                # Add GPS data if missing (Day 7 recovery values)
                if gps_exists[0]['count'] == 0:
                    # Generate realistic Day 7 recovery GPS values
                    base_distance = 3200 + (i * 10)  # Vary slightly per player
                    max_speed = 21.5 + (i * 0.05)
                    efforts_low = 25 + (i % 8)
                    efforts_high = 2 + (i % 3)
                    
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
                        base_distance,
                        max_speed,
                        efforts_low,
                        efforts_low - 3,
                        efforts_high,
                        efforts_high * 25.0,
                        max(0, efforts_high - 1),
                        'day7_recovery_simulation'
                    ))
                    gps_inserted += 1
                
                # Check if PSE data already exists
                pse_check = """
                    SELECT COUNT(*) as count FROM dados_pse 
                    WHERE atleta_id = %s AND sessao_id = %s
                """
                pse_exists = db.query_to_dict(pse_check, (athlete_id, session_id))
                
                # Add PSE data if missing (Day 7 recovery values)
                if pse_exists[0]['count'] == 0:
                    # Generate realistic Day 7 recovery PSE values (within constraints)
                    sono = max(1, min(10, 7 + (i % 3) - 1))  # 6-8 range
                    stress = max(1, min(5, 4 + (i % 2) - 1))  # 3-4 range
                    fadiga = max(1, min(5, 3 + (i % 2)))      # 3-4 range
                    doms = max(1, min(5, 3 + (i % 2)))        # 3-4 range
                    rpe = max(1, min(10, 3 + (i % 2)))        # 3-4 range
                    
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
                        45,  # Duration
                        rpe,
                        45 * rpe  # Load calculation
                    ))
                    pse_inserted += 1
                
                if (gps_inserted + pse_inserted) % 10 == 0:
                    print(f"📊 Progress: GPS +{gps_inserted}, PSE +{pse_inserted}")
                
            except Exception as e:
                print(f"❌ Error for {athlete_name}: {e}")
        
        db.close()
        
        print(f"\n📊 Final Summary:")
        print(f"✅ GPS records added: {gps_inserted}")
        print(f"✅ PSE records added: {pse_inserted}")
        
        if gps_inserted > 0 or pse_inserted > 0:
            print("🎉 Day 7 data completed successfully!")
            print("\n📈 Complete 7-day simulation week is now ready!")
            return True
        else:
            print("ℹ️ All data was already present")
            return True
        
    except Exception as e:
        print(f"❌ Error completing Day 7 data: {e}")
        return False

if __name__ == "__main__":
    complete_day7_data()
