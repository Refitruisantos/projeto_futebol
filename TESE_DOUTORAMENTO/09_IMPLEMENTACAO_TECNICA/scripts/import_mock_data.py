#!/usr/bin/env python3
"""
Import Mock Data to Database
================================

This script imports the generated mock CSV files into the PostgreSQL database.
It creates athletes, sessions, GPS data, and PSE data records.

Usage:
    python import_mock_data.py
"""

import pandas as pd
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import database connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'python'))

# Import database connection
try:
    from python.conexao_db import DatabaseConnection
except ImportError:
    try:
        from conexao_db import DatabaseConnection
    except ImportError:
        print("❌ Cannot import DatabaseConnection. Check python/01_conexao_db.py")
        sys.exit(1)

def import_mock_data():
    """Import all mock CSV files into the database"""
    
    print("🔄 Starting mock data import...")
    
    # Initialize database connection
    db = DatabaseConnection()
    
    try:
        # File paths
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        athletes_file = base_dir / "mock_athletes.csv"
        sessions_file = base_dir / "mock_sessions.csv"
        gps_file = base_dir / "mock_gps_january_2025.csv"
        pse_file = base_dir / "mock_pse_january_2025.csv"
        
        # Check if files exist
        for file_path in [athletes_file, sessions_file, gps_file, pse_file]:
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                print("Please run demo_mock_generation.py first to create the mock data files.")
                return False
        
        print(f"📁 Working directory: {base_dir}")
        
        # 1. Import Athletes
        print("\n👥 Importing athletes...")
        athletes_df = pd.read_csv(athletes_file)
        print(f"   Found {len(athletes_df)} athletes")
        
        for _, athlete in athletes_df.iterrows():
            query = """
                INSERT INTO atletas (id, nome_completo, data_nascimento, posicao, altura, peso, 
                                   pe_dominante, numero_camisola, ativo, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    nome_completo = EXCLUDED.nome_completo,
                    posicao = EXCLUDED.posicao,
                    altura = EXCLUDED.altura,
                    peso = EXCLUDED.peso,
                    pe_dominante = EXCLUDED.pe_dominante,
                    numero_camisola = EXCLUDED.numero_camisola,
                    ativo = EXCLUDED.ativo
            """
            params = (
                athlete['id'], athlete['nome_completo'], athlete['data_nascimento'],
                athlete['posicao'], athlete['altura'], athlete['peso'],
                athlete['pe_dominante'], athlete['numero_camisola'], 
                athlete['ativo'], datetime.now()
            )
            db.execute_query(query, params)
        
        print(f"   ✅ Imported {len(athletes_df)} athletes")
        
        # 2. Import Sessions
        print("\n🏃 Importing sessions...")
        sessions_df = pd.read_csv(sessions_file)
        print(f"   Found {len(sessions_df)} sessions")
        
        for _, session in sessions_df.iterrows():
            query = """
                INSERT INTO sessoes (id, data, tipo, adversario, local, resultado, 
                                   competicao, fase, observacoes, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    data = EXCLUDED.data,
                    tipo = EXCLUDED.tipo,
                    adversario = EXCLUDED.adversario,
                    local = EXCLUDED.local,
                    resultado = EXCLUDED.resultado,
                    competicao = EXCLUDED.competicao,
                    fase = EXCLUDED.fase,
                    observacoes = EXCLUDED.observacoes
            """
            params = (
                session['id'], session['data'], session['tipo'],
                session['adversario'], session['local'], session['resultado'],
                session['competicao'], session['fase'], session['observacoes'],
                datetime.now()
            )
            db.execute_query(query, params)
        
        print(f"   ✅ Imported {len(sessions_df)} sessions")
        
        # 3. Import GPS Data
        print("\n📊 Importing GPS data...")
        gps_df = pd.read_csv(gps_file)
        print(f"   Found {len(gps_df)} GPS records")
        
        gps_imported = 0
        for _, gps in gps_df.iterrows():
            query = """
                INSERT INTO dados_gps (atleta_id, sessao_id, time, distancia_total, 
                                     velocidade_max, velocidade_media, aceleracoes, 
                                     desaceleracoes, sprints, dist_19_8_kmh, player_load, 
                                     high_intensity_distance, metabolic_power, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                gps['atleta_id'], gps['sessao_id'], gps['time'],
                gps['distancia_total'], gps['velocidade_max'], gps['velocidade_media'],
                gps['aceleracoes'], gps['desaceleracoes'], gps['sprints'],
                gps['dist_19_8_kmh'], gps['player_load'], gps['high_intensity_distance'],
                gps['metabolic_power'], datetime.now()
            )
            db.execute_query(query, params)
            gps_imported += 1
        
        print(f"   ✅ Imported {gps_imported} GPS records")
        
        # 4. Import PSE Data
        print("\n💪 Importing PSE data...")
        pse_df = pd.read_csv(pse_file)
        print(f"   Found {len(pse_df)} PSE records")
        
        pse_imported = 0
        for _, pse in pse_df.iterrows():
            query = """
                INSERT INTO dados_pse (atleta_id, sessao_id, time, pse, duracao_min, 
                                     carga_total, tipo_sessao, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                pse['atleta_id'], pse['sessao_id'], pse['time'],
                pse['pse'], pse['duracao_min'], pse['carga_total'],
                pse['tipo_sessao'], datetime.now()
            )
            db.execute_query(query, params)
            pse_imported += 1
        
        print(f"   ✅ Imported {pse_imported} PSE records")
        
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
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close_all_connections()

if __name__ == "__main__":
    success = import_mock_data()
    if success:
        print("\n🚀 Ready to calculate metrics and view dashboard!")
    else:
        print("\n❌ Import failed. Check error messages above.")
        sys.exit(1)
