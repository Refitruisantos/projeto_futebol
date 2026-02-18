#!/usr/bin/env python3
"""Check all sessions in database"""

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

print("🔍 Checking all sessions in database\n")

# Count sessions by month
cursor.execute("""
    SELECT 
        TO_CHAR(data, 'YYYY-MM') as month,
        tipo,
        COUNT(*) as count
    FROM sessoes
    GROUP BY month, tipo
    ORDER BY month, tipo
""")

print("📅 Sessions by Month:")
print(f"{'Month':<12} | {'Type':<10} | Count")
print("-" * 40)
for month, tipo, count in cursor.fetchall():
    print(f"{month:<12} | {tipo:<10} | {count}")

# Check date range
cursor.execute("""
    SELECT MIN(data), MAX(data), COUNT(*)
    FROM sessoes
""")

min_date, max_date, total = cursor.fetchone()
print(f"\n📊 Total Sessions: {total}")
print(f"   Date Range: {min_date} to {max_date}")

# Check for gaps in dates
cursor.execute("""
    SELECT data, tipo, COALESCE(adversario, observacoes) as info
    FROM sessoes
    ORDER BY data
    LIMIT 20
""")

print(f"\n📋 First 20 Sessions:")
print(f"{'Date':<12} | {'Type':<10} | Info")
print("-" * 60)
for data, tipo, info in cursor.fetchall():
    info_str = str(info)[:35] if info else '-'
    print(f"{str(data):<12} | {tipo:<10} | {info_str}")

# Check last 10 sessions
cursor.execute("""
    SELECT data, tipo, COALESCE(adversario, observacoes) as info
    FROM sessoes
    ORDER BY data DESC
    LIMIT 10
""")

print(f"\n📋 Last 10 Sessions:")
print(f"{'Date':<12} | {'Type':<10} | Info")
print("-" * 60)
for data, tipo, info in cursor.fetchall():
    info_str = str(info)[:35] if info else '-'
    print(f"{str(data):<12} | {tipo:<10} | {info_str}")

cursor.close()
conn.close()
