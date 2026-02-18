#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar automaticamente PDFs de GPS já carregados
Extrai dados do PDF "Gps_jornada_1.pdf" e insere diretamente na base de dados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.database import get_db
from datetime import datetime, date
import pandas as pd

def extrair_dados_gps_jornada_1():
    """
    Dados extraídos do PDF Gps_jornada_1.pdf (JOGO_2ªJORNADA)
    """
    
    dados_gps = [
        {'player': 'DUARTE CALHA', 'total_distance_m': 11255, 'max_velocity_kmh': 29.4, 'acc_b1_3_total_efforts': 84, 'decel_b1_3_total_efforts': 69, 'efforts_over_19_8_kmh': 39, 'distance_over_19_8_kmh': 590, 'efforts_over_25_2_kmh': 5},
        {'player': 'GABI COELHO', 'total_distance_m': 8544, 'max_velocity_kmh': 30.5, 'acc_b1_3_total_efforts': 77, 'decel_b1_3_total_efforts': 84, 'efforts_over_19_8_kmh': 39, 'distance_over_19_8_kmh': 686, 'efforts_over_25_2_kmh': 9},
        {'player': 'GONÇALO CARDOSO', 'total_distance_m': 4300, 'max_velocity_kmh': 28.8, 'acc_b1_3_total_efforts': 44, 'decel_b1_3_total_efforts': 46, 'efforts_over_19_8_kmh': 28, 'distance_over_19_8_kmh': 506, 'efforts_over_25_2_kmh': 9},
        {'player': 'GONÇALO GR', 'total_distance_m': 5216, 'max_velocity_kmh': 23.2, 'acc_b1_3_total_efforts': 21, 'decel_b1_3_total_efforts': 18, 'efforts_over_19_8_kmh': 5, 'distance_over_19_8_kmh': 30, 'efforts_over_25_2_kmh': 0},
        {'player': 'JOÃO FERREIRA', 'total_distance_m': 12114, 'max_velocity_kmh': 32.1, 'acc_b1_3_total_efforts': 114, 'decel_b1_3_total_efforts': 126, 'efforts_over_19_8_kmh': 75, 'distance_over_19_8_kmh': 1141, 'efforts_over_25_2_kmh': 19},
        {'player': 'LEONARDO SANTOS', 'total_distance_m': 6203, 'max_velocity_kmh': 26.7, 'acc_b1_3_total_efforts': 54, 'decel_b1_3_total_efforts': 55, 'efforts_over_19_8_kmh': 30, 'distance_over_19_8_kmh': 327, 'efforts_over_25_2_kmh': 2},
        {'player': 'LESIANDRO MARINHO', 'total_distance_m': 8512, 'max_velocity_kmh': 30.2, 'acc_b1_3_total_efforts': 89, 'decel_b1_3_total_efforts': 77, 'efforts_over_19_8_kmh': 32, 'distance_over_19_8_kmh': 548, 'efforts_over_25_2_kmh': 9},
        {'player': 'MARTIM SOARES', 'total_distance_m': 3333, 'max_velocity_kmh': 32.0, 'acc_b1_3_total_efforts': 35, 'decel_b1_3_total_efforts': 36, 'efforts_over_19_8_kmh': 17, 'distance_over_19_8_kmh': 308, 'efforts_over_25_2_kmh': 4},
        {'player': 'PAULO DANIEL', 'total_distance_m': 9653, 'max_velocity_kmh': 32.1, 'acc_b1_3_total_efforts': 61, 'decel_b1_3_total_efforts': 66, 'efforts_over_19_8_kmh': 34, 'distance_over_19_8_kmh': 717, 'efforts_over_25_2_kmh': 11},
        {'player': 'PEDRO RIBEIRO', 'total_distance_m': 10153, 'max_velocity_kmh': 32.4, 'acc_b1_3_total_efforts': 90, 'decel_b1_3_total_efforts': 86, 'efforts_over_19_8_kmh': 47, 'distance_over_19_8_kmh': 806, 'efforts_over_25_2_kmh': 14},
        {'player': 'RAFAEL DIAS', 'total_distance_m': 4501, 'max_velocity_kmh': 30.3, 'acc_b1_3_total_efforts': 43, 'decel_b1_3_total_efforts': 47, 'efforts_over_19_8_kmh': 27, 'distance_over_19_8_kmh': 437, 'efforts_over_25_2_kmh': 4},
        {'player': 'RAFAEL CESÁRIO', 'total_distance_m': 9146, 'max_velocity_kmh': 32.7, 'acc_b1_3_total_efforts': 56, 'decel_b1_3_total_efforts': 52, 'efforts_over_19_8_kmh': 29, 'distance_over_19_8_kmh': 500, 'efforts_over_25_2_kmh': 7},
        {'player': 'RODRIGO ANDRADE', 'total_distance_m': 8190, 'max_velocity_kmh': 30.5, 'acc_b1_3_total_efforts': 56, 'decel_b1_3_total_efforts': 72, 'efforts_over_19_8_kmh': 45, 'distance_over_19_8_kmh': 644, 'efforts_over_25_2_kmh': 11},
        {'player': 'TIAGO BATISTA', 'total_distance_m': 3014, 'max_velocity_kmh': 26.3, 'acc_b1_3_total_efforts': 25, 'decel_b1_3_total_efforts': 23, 'efforts_over_19_8_kmh': 9, 'distance_over_19_8_kmh': 130, 'efforts_over_25_2_kmh': 4},
        {'player': 'TIAGO LOBO', 'total_distance_m': 6225, 'max_velocity_kmh': 29.2, 'acc_b1_3_total_efforts': 51, 'decel_b1_3_total_efforts': 39, 'efforts_over_19_8_kmh': 19, 'distance_over_19_8_kmh': 274, 'efforts_over_25_2_kmh': 5}
    ]
    
    return pd.DataFrame(dados_gps)

def inserir_dados_automaticamente():
    """
    Insere os dados GPS diretamente na base de dados
    """
    
    print("🏃 Processando dados GPS do PDF automaticamente...")
    
    # Obter dados
    df = extrair_dados_gps_jornada_1()
    print(f"✓ Dados extraídos: {len(df)} jogadores")
    
    # Conectar à base de dados
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Criar ou obter sessão para jornada 1
        session_date = date(2025, 8, 15)  # Data do relatório
        jornada = 1
        
        # Verificar se já existe sessão
        check_query = """
            SELECT id FROM sessoes
            WHERE jornada = %s AND data = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        existing = db.query_to_dict(check_query, (jornada, session_date))
        
        if existing:
            session_id = existing[0]['id']
            print(f"✓ Usando sessão existente: {session_id}")
        else:
            # Criar nova sessão
            insert_session = """
                INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao, created_at)
                VALUES (%s, %s, 90, %s, %s, NOW())
            """
            db.execute_query(insert_session, (session_date, 'jogo', jornada, 'JOGO_2ªJORNADA'))
            
            # Obter ID da sessão criada
            result = db.query_to_dict(check_query, (jornada, session_date))
            session_id = result[0]['id']
            print(f"✓ Nova sessão criada: {session_id}")
        
        # Inserir dados GPS
        inserted_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Encontrar atleta
                athlete_query = """
                    SELECT id FROM atletas
                    WHERE LOWER(nome_completo) = %s OR LOWER(jogador_id) = %s
                    ORDER BY ativo DESC
                    LIMIT 1
                """
                player_name = row['player'].strip().lower()
                athlete_result = db.query_to_dict(athlete_query, (player_name, player_name))
                
                if not athlete_result:
                    errors.append(f"Jogador não encontrado: {row['player']}")
                    continue
                
                athlete_id = athlete_result[0]['id']
                
                # Inserir dados GPS
                insert_gps = """
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
                    ON CONFLICT DO NOTHING
                """
                
                db.execute_query(insert_gps, (
                    datetime.combine(session_date, datetime.min.time()),
                    athlete_id,
                    session_id,
                    float(row['total_distance_m']),
                    float(row['max_velocity_kmh']),
                    int(row['acc_b1_3_total_efforts']),
                    int(row['decel_b1_3_total_efforts']),
                    int(row['efforts_over_19_8_kmh']),
                    float(row['distance_over_19_8_kmh']),
                    int(row['efforts_over_25_2_kmh']),
                    'pdf_gps_jornada_1_automatico'
                ))
                
                inserted_count += 1
                
            except Exception as e:
                errors.append(f"Erro no jogador {row['player']}: {str(e)}")
        
        print(f"🎉 Processamento concluído!")
        print(f"  - Sessão ID: {session_id}")
        print(f"  - Registos inseridos: {inserted_count}/{len(df)}")
        
        if errors:
            print(f"⚠️  Avisos:")
            for error in errors[:5]:  # Mostrar apenas os primeiros 5
                print(f"    - {error}")
        
        return {
            "success": True,
            "session_id": session_id,
            "inserted": inserted_count,
            "total": len(df),
            "errors": errors
        }
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()

if __name__ == '__main__':
    resultado = inserir_dados_automaticamente()
    
    if resultado["success"]:
        print(f"\n✅ Dados GPS inseridos com sucesso na base de dados!")
        print(f"   Pode agora visualizar no dashboard em http://localhost:5173")
    else:
        print(f"\n❌ Falha no processamento: {resultado['error']}")
