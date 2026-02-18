#!/usr/bin/env python3
"""Test the ingestion history endpoint"""

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

print("🔍 Testing Ingestion History Query\n")

# Check if dados_gps has fonte column
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dados_gps' AND column_name = 'fonte'")
    fonte_exists = cursor.fetchone()
    print(f"fonte column exists: {bool(fonte_exists)}")
except Exception as e:
    print(f"Error checking fonte column: {e}")

# Check if dados_gps has created_at column
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dados_gps' AND column_name = 'created_at'")
    created_at_exists = cursor.fetchone()
    print(f"created_at column exists: {bool(created_at_exists)}")
except Exception as e:
    print(f"Error checking created_at column: {e}")

# Check sample data
try:
    cursor.execute("SELECT COUNT(*) FROM dados_gps")
    count = cursor.fetchone()[0]
    print(f"Total GPS records: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM dados_gps LIMIT 1")
        sample = cursor.fetchone()
        print(f"Sample record: {sample}")
        
        # Get column names
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'dados_gps' ORDER BY ordinal_position")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Available columns: {columns}")
        
except Exception as e:
    print(f"Error checking GPS data: {e}")

# Test the actual query from the endpoint
print("\n📋 Testing ingestion history query...")
try:
    query = """
        SELECT DISTINCT
            'mock_data' as fonte,
            sessao_id,
            DATE(time) as data,
            COUNT(*) as num_records,
            MIN(time) as ingested_at
        FROM dados_gps
        GROUP BY sessao_id, DATE(time)
        ORDER BY ingested_at DESC
        LIMIT 10
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    print(f"Query results: {len(results)} records")
    
    for i, result in enumerate(results[:5]):
        print(f"  {i+1}: {result}")
        
except Exception as e:
    print(f"Query error: {e}")

cursor.close()
conn.close()
