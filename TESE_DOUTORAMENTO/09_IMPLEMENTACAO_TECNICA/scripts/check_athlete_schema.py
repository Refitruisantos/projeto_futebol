#!/usr/bin/env python3
"""Check athlete table schema"""

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

print("🔍 Checking athlete table schema...")

cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'atletas'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
print("Available columns:")
for col, dtype in columns:
    print(f"  {col}: {dtype}")

# Check if we have age data
cursor.execute("SELECT * FROM atletas LIMIT 1")
sample = cursor.fetchone()
print(f"\nSample record: {sample}")

cursor.close()
conn.close()
