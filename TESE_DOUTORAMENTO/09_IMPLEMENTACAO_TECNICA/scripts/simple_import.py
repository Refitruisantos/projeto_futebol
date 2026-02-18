#!/usr/bin/env python3
"""
Simple Mock Data Import
========================

Direct import using psycopg2 to avoid encoding issues.
"""

import pandas as pd
import psycopg2
import os
from datetime import datetime
from pathlib import Path
import sys

def get_db_connection():
    """Get direct database connection"""
    try:
        # Load environment variables
        load_dotenv = __import__('dotenv').load_dotenv
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5433'),
            database=os.getenv('DB_NAME', 'futebol_tese'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'desporto.20')
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def import_mock_data():
    """Import mock data using direct SQL"""
    
    print("🔄 Starting mock data import...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # File paths
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        athletes_file = base_dir / "mock_athletes.csv"
        sessions_file = base_dir / "mock_sessions.csv"
        gps_file = base_dir / "mock_gps_january_2025.csv"
        pse_file = base_dir / "mock_pse_january_2025.csv"
        
        print(f"📁 Working directory: {base_dir}")
        
        # Check files exist
        for file_path in [athletes_file, sessions_file, gps_file, pse_file]:
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                return False
        
        # 1. Import Athletes
        print("\n👥 Importing athletes...")
        athletes_df = pd.read_csv(athletes_file)
        print(f"   Found {len(athletes_df)} athletes")
        
        for _, athlete in athletes_df.iterrows():
            cursor.execute("""
                INSERT INTO atletas (jogador_id, nome_completo, data_nascimento, posicao, altura_cm, massa_kg,
                                   pe_dominante, numero_camisola, ativo, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (jogador_id) DO UPDATE SET
                    nome_completo = EXCLUDED.nome_completo,
                    posicao = EXCLUDED.posicao,
                    altura_cm = EXCLUDED.altura_cm,
                    massa_kg = EXCLUDED.massa_kg,
                    pe_dominante = EXCLUDED.pe_dominante,
                    numero_camisola = EXCLUDED.numero_camisola,
                    ativo = EXCLUDED.ativo
            """, (
                athlete['jogador_id'], athlete['nome_completo'], athlete['data_nascimento'],
                athlete['posicao'], athlete['altura_cm'], athlete['massa_kg'],
                athlete['pe_dominante'], athlete['numero_camisola'], 
                athlete['ativo'], datetime.now()
            ))
        
        print(f"   ✅ Imported {len(athletes_df)} athletes")
        
        # 2. Import Sessions
        print("\n🏃 Importing sessions...")
        sessions_df = pd.read_csv(sessions_file)
        print(f"   Found {len(sessions_df)} sessions")
        
        # Clear existing sessions and create them manually
        cursor.execute("DELETE FROM sessoes")
        
        for index, row in sessions_df.iterrows():
            try:
                session_id = index + 1  # Use index as ID (1-27)
                session_data = str(row.get('data', '2025-01-01'))
                session_tipo = str(row.get('tipo', 'treino'))
                session_duracao = int(row.get('duracao_min', 60))
                
                cursor.execute("""
                    INSERT INTO sessoes (id, data, tipo, duracao_min, adversario, local, resultado, 
                                       competicao, jornada, observacoes, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session_id, session_data, session_tipo, session_duracao,
                    '', 'casa', '', '', 1, f"Training session - {session_duracao} min",
                    datetime.now()
                ))
            except Exception as e:
                print(f"   ⚠️ Error importing session {index}: {e}")
                continue
        
        print(f"   ✅ Imported {len(sessions_df)} sessions")
        
        # 3. Import GPS Data
        print("\n📊 Importing GPS data...")
        gps_df = pd.read_csv(gps_file)
        print(f"   Found {len(gps_df)} GPS records")
        
        # Create mapping from numeric ID to database id
        cursor.execute("SELECT id, jogador_id FROM atletas")
        athlete_mapping = {}
        for row in cursor.fetchall():
            db_id, jogador_id = row
            # Extract numeric part from ATL001 -> 1
            numeric_id = int(jogador_id.replace('ATL', ''))
            athlete_mapping[numeric_id] = db_id
        print(f"   Athlete mapping (first 5): {dict(list(athlete_mapping.items())[:5])}")
        
        # Create mapping for sessions (they should be 1-27 matching the CSV)
        cursor.execute("SELECT id FROM sessoes ORDER BY id")
        session_mapping = {}
        session_ids = cursor.fetchall()
        print(f"   Session IDs in database: {session_ids}")
        for i, row in enumerate(session_ids, 1):
            session_mapping[i] = row[0]  # CSV ID -> Database ID
        print(f"   Session mapping (first 5): {dict(list(session_mapping.items())[:5])}")
        
        if not session_mapping:
            print("   ❌ No sessions found in database! Using direct IDs...")
            # Use direct mapping if sessions weren't imported properly
            for i in range(1, 28):
                session_mapping[i] = i
        
        gps_imported = 0
        for _, gps in gps_df.iterrows():
            # Convert jogador_id to database id
            original_atleta_id = gps['atleta_id']
            db_atleta_id = athlete_mapping.get(original_atleta_id, original_atleta_id)
            
            # Convert session_id to database id
            original_sessao_id = gps['sessao_id']
            db_sessao_id = session_mapping.get(original_sessao_id, original_sessao_id)
            
            cursor.execute("""
                INSERT INTO dados_gps (atleta_id, sessao_id, time, distancia_total, 
                                     velocidade_max, velocidade_media, aceleracoes, 
                                     desaceleracoes, sprints, player_load)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                db_atleta_id, db_sessao_id, gps['time'],
                gps['distancia_total'], gps['velocidade_max'], gps['velocidade_media'],
                gps['aceleracoes'], gps['desaceleracoes'], gps['sprints'],
                0  # Default player_load
            ))
            gps_imported += 1
        
        print(f"   ✅ Imported {gps_imported} GPS records")
        
        # 4. Import PSE Data
        print("\n💪 Importing PSE data...")
        pse_df = pd.read_csv(pse_file)
        print(f"   Found {len(pse_df)} PSE records")
        
        pse_imported = 0
        for _, pse in pse_df.iterrows():
            # Convert jogador_id to database id
            original_atleta_id = pse['atleta_id']
            db_atleta_id = athlete_mapping.get(original_atleta_id, original_atleta_id)
            
            # Convert session_id to database id
            original_sessao_id = pse['sessao_id']
            db_sessao_id = session_mapping.get(original_sessao_id, original_sessao_id)
            
            cursor.execute("""
                INSERT INTO dados_pse (atleta_id, sessao_id, time, pse, duracao_min, 
                                     carga_total)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                db_atleta_id, db_sessao_id, pse['time'],
                pse['pse'], pse['duracao_min'], pse['carga_total']
            ))
            pse_imported += 1
        
        print(f"   ✅ Imported {pse_imported} PSE records")
        
        # Commit all changes
        conn.commit()
        
        # Summary
        print("\n" + "="*60)
        print("✅ IMPORT SUMMARY")
        print("="*60)
        print(f"   Athletes:     {len(athletes_df)}")
        print(f"   Sessions:      {len(sessions_df)}")
        print(f"   GPS Records:   {gps_imported}")
        print(f"   PSE Records:   {pse_imported}")
        print("="*60)
        print("\n🎯 Mock data successfully imported!")
        print("\n📊 Next step: Calculate weekly metrics")
        print("   Run: python scripts/calculate_weekly_metrics.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing data: {str(e)}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = import_mock_data()
    if success:
        print("\n🚀 Ready to calculate metrics and view dashboard!")
    else:
        print("\n❌ Import failed. Check error messages above.")
        sys.exit(1)
