#!/usr/bin/env python3
"""Check the actual structure of metricas_carga table"""

import psycopg2
import os

try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    print("🔍 Verificando estrutura da tabela metricas_carga...")
    
    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'metricas_carga'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"\n📊 Colunas da tabela metricas_carga ({len(columns)} colunas):")
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
    
    # Sample data
    cursor.execute("SELECT * FROM metricas_carga LIMIT 3")
    sample_data = cursor.fetchall()
    print(f"\n📋 Dados de exemplo ({len(sample_data)} registros):")
    for i, record in enumerate(sample_data):
        print(f"   Registro {i+1}: {record[:5]}...")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
