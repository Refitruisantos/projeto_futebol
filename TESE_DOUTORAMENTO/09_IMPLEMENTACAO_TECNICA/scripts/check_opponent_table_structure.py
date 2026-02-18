#!/usr/bin/env python3
"""Check opponent analysis table structure"""

import psycopg2
import os

try:
    load_dotenv = __import__('dotenv').load_dotenv
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5433'),
        database=os.getenv('DB_NAME', 'futebol_tese'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'desporto.20')
    )
except:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )

cursor = conn.cursor()

print("🔍 Verificando estrutura da tabela analise_adversarios...")

# Check if table exists
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'analise_adversarios'
    )
""")
table_exists = cursor.fetchone()[0]

if table_exists:
    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'analise_adversarios'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"\n📊 Colunas da tabela analise_adversarios ({len(columns)} colunas):")
    for col in columns:
        print(f"   • {col[0]} ({col[1]}) - {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
    # Check existing data
    cursor.execute("SELECT COUNT(*) FROM analise_adversarios")
    count = cursor.fetchone()[0]
    print(f"\n📋 Registros existentes: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM analise_adversarios LIMIT 3")
        sample_data = cursor.fetchall()
        print("Dados de exemplo:")
        for i, record in enumerate(sample_data):
            print(f"   Registro {i+1}: {record[:3]}...")
else:
    print("❌ Tabela analise_adversarios não existe")

cursor.close()
conn.close()
