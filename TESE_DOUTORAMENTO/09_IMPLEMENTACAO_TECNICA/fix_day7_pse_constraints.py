#!/usr/bin/env python3
"""
Fix Day 7 PSE data with proper database constraints
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

def fix_day7_pse():
    """Add Day 7 PSE data with strict constraint compliance"""
    print("🔧 Fixing Day 7 PSE data with proper constraints...")
    
    session_date = "2025-01-26"
    
    try:
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
        print(f"🎯 Using session ID: {session_id}")
        
        # Get athletes without PSE data for this session
        missing_pse_query = """
            SELECT a.id, a.nome_completo 
            FROM atletas a 
            WHERE a.ativo = true 
            AND NOT EXISTS (
                SELECT 1 FROM dados_pse p 
                WHERE p.atleta_id = a.id AND p.sessao_id = %s
            )
            ORDER BY a.id
        """
        athletes = db.query_to_dict(missing_pse_query, (session_id,))
        print(f"📋 Found {len(athletes)} athletes missing PSE data")
        
        if len(athletes) == 0:
            print("ℹ️ All athletes already have PSE data for Day 7")
            return True
        
        inserted = 0
        
        for i, athlete in enumerate(athletes):
            try:
                # Very conservative values that definitely fit constraints
                # Based on typical database constraints for PSE data
                sono = 5  # Middle value, safe
                stress = 2  # Low stress
                fadiga = 2  # Low fatigue (recovery day)
                doms = 2   # Low muscle soreness
                rpe = 3    # Very light effort
                duracao = 45  # Short session
                carga = duracao * rpe  # Simple load calculation
                
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
                    athlete['id'],
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
                
                if inserted % 5 == 0:
                    print(f"✅ Inserted {inserted} PSE records...")
                
            except Exception as e:
                print(f"❌ Error for {athlete['nome_completo']}: {e}")
        
        db.close()
        
        print(f"\n📊 PSE Fix Summary:")
        print(f"✅ PSE records added: {inserted}")
        
        if inserted > 0:
            print("🎉 Day 7 PSE data fixed successfully!")
            return True
        else:
            print("⚠️ No PSE data was added")
            return False
        
    except Exception as e:
        print(f"❌ Error fixing Day 7 PSE: {e}")
        return False

if __name__ == "__main__":
    fix_day7_pse()
