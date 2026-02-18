"""Fix all session constraints"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5433'),
    database=os.getenv('DB_NAME', 'futebol_tese'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres')
)

cursor = conn.cursor()

print("=" * 60)
print("Fixing ALL session constraints")
print("=" * 60)

# Check current tipo values
print("\n1. Checking current tipo values...")
cursor.execute("SELECT DISTINCT tipo FROM sessoes WHERE tipo IS NOT NULL")
rows = cursor.fetchall()
print(f"   Found {len(rows)} distinct values:")
for row in rows:
    print(f"   - '{row[0]}'")

# Drop tipo constraint
print("\n2. Dropping tipo constraint...")
cursor.execute("ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_tipo_check")
conn.commit()
print("   ✓ Constraint dropped")

# Standardize tipo values
print("\n3. Standardizing tipo values...")
cursor.execute("UPDATE sessoes SET tipo = 'Treino' WHERE LOWER(tipo) = 'treino'")
treino_count = cursor.rowcount
cursor.execute("UPDATE sessoes SET tipo = 'Jogo' WHERE LOWER(tipo) = 'jogo'")
jogo_count = cursor.rowcount
cursor.execute("UPDATE sessoes SET tipo = 'Treino' WHERE LOWER(tipo) = 'recuperacao'")
recuperacao_count = cursor.rowcount
conn.commit()
print(f"   ✓ Updated {treino_count} rows to 'Treino'")
print(f"   ✓ Updated {jogo_count} rows to 'Jogo'")
print(f"   ✓ Updated {recuperacao_count} 'recuperacao' → 'Treino'")

# Add new tipo constraint
print("\n4. Adding new tipo constraint...")
cursor.execute("""
    ALTER TABLE sessoes ADD CONSTRAINT sessoes_tipo_check 
    CHECK (tipo IN ('Treino', 'Jogo'))
""")
conn.commit()
print("   ✓ Constraint added")

# Verify both constraints
print("\n5. Verifying constraints...")
cursor.execute("""
    SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
    FROM pg_constraint 
    WHERE conrelid = 'sessoes'::regclass 
    AND conname IN ('sessoes_local_check', 'sessoes_tipo_check')
    ORDER BY conname
""")
for row in cursor.fetchall():
    print(f"   ✓ {row[0]}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("✓ All constraints fixed!")
print("=" * 60)

# Test session creation
print("\nTesting session creation...")
import requests
try:
    response = requests.post(
        'http://localhost:8000/api/sessions/',
        json={'tipo': 'Treino', 'data': '2026-02-06', 'duracao_min': 90, 'local': 'Casa'}
    )
    if response.status_code in [200, 201]:
        print(f"✓ Session creation WORKS! Status: {response.status_code}")
        result = response.json()
        print(f"  Session ID: {result.get('id')}")
        print(f"  Type: {result.get('tipo')}")
        print(f"  Location: {result.get('local')}")
        print("\n🎉 SUCCESS! You can now create sessions from the frontend!")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  {response.text[:300]}")
except Exception as e:
    print(f"✗ Error: {e}")
