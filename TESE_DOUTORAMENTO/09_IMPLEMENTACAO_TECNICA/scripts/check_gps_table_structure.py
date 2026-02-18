#!/usr/bin/env python3
"""Check GPS table structure to understand column names"""

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

print("🔍 Verificando estrutura da tabela dados_gps...")

# Check table structure
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'dados_gps'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
print(f"\n📊 Colunas da tabela dados_gps ({len(columns)} colunas):")
for col in columns:
    print(f"   • {col[0]} ({col[1]}) - {'NULL' if col[2] == 'YES' else 'NOT NULL'}")

# Check primary key
cursor.execute("""
    SELECT column_name
    FROM information_schema.key_column_usage
    WHERE table_name = 'dados_gps' AND constraint_name LIKE '%pkey%'
""")
pk_columns = cursor.fetchall()
if pk_columns:
    print(f"\n🔑 Chave primária: {', '.join([col[0] for col in pk_columns])}")

# Sample a few records to see the data
cursor.execute("SELECT * FROM dados_gps LIMIT 3")
sample_data = cursor.fetchall()
print(f"\n📋 Dados de exemplo ({len(sample_data)} registros):")
for i, record in enumerate(sample_data):
    print(f"   Registro {i+1}: {record[:5]}...")  # Show first 5 columns

cursor.close()
conn.close()
