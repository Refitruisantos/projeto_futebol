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

# Check dados_pse columns
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'dados_pse'
    ORDER BY ordinal_position
""")

print("dados_pse columns:")
for col, dtype in cursor.fetchall():
    print(f"  {col}: {dtype}")

# Check dados_gps columns
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'dados_gps'
    ORDER BY ordinal_position
""")

print("\ndados_gps columns:")
for col, dtype in cursor.fetchall():
    print(f"  {col}: {dtype}")

cursor.close()
conn.close()
