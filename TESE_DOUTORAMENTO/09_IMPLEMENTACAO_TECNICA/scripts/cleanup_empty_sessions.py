#!/usr/bin/env python3
"""
Remove duplicate empty sessions that have no GPS/PSE data
"""

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

print("🧹 Cleaning up empty duplicate sessions\n")

# Find sessions with no data
cursor.execute("""
    SELECT s.id, s.data, s.tipo
    FROM sessoes s
    LEFT JOIN dados_gps g ON g.sessao_id = s.id
    LEFT JOIN dados_pse p ON p.sessao_id = s.id
    WHERE g.sessao_id IS NULL AND p.sessao_id IS NULL
    ORDER BY s.data
""")

empty_sessions = cursor.fetchall()
print(f"Found {len(empty_sessions)} sessions with no data")

if empty_sessions:
    print(f"\n🗑️  Deleting empty sessions...")
    session_ids = [s[0] for s in empty_sessions]
    
    cursor.execute("""
        DELETE FROM sessoes WHERE id = ANY(%s)
    """, (session_ids,))
    
    conn.commit()
    print(f"✅ Deleted {len(empty_sessions)} empty sessions")

# Verify what's left
cursor.execute("""
    SELECT 
        TO_CHAR(s.data, 'YYYY-MM') as month,
        COUNT(*) as total
    FROM sessoes s
    LEFT JOIN dados_gps g ON g.sessao_id = s.id
    LEFT JOIN dados_pse p ON p.sessao_id = s.id
    WHERE g.sessao_id IS NOT NULL OR p.sessao_id IS NOT NULL
    GROUP BY month
    ORDER BY month
""")

print(f"\n📊 Sessions with data by month:")
for month, count in cursor.fetchall():
    print(f"   {month}: {count}")

# Check earliest session
cursor.execute("""
    SELECT MIN(s.data), MAX(s.data), COUNT(*)
    FROM sessoes s
    JOIN dados_pse p ON p.sessao_id = s.id
""")

min_date, max_date, total = cursor.fetchone()
print(f"\n📅 Date Range (sessions with data):")
print(f"   First: {min_date}")
print(f"   Last: {max_date}")
print(f"   Total: {total}")

cursor.close()
conn.close()

print("\n✅ Cleanup complete! Refresh your browser.")
