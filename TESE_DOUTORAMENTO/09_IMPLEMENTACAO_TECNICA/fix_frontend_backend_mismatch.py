"""
Fix frontend-backend field mismatch for session creation
The frontend is sending lowercase values but backend expects capitalized
"""
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
print("Fixing Frontend-Backend Field Mismatch")
print("=" * 60)

# Check current constraints
print("\n1. Current constraints:")
cursor.execute("""
    SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
    FROM pg_constraint 
    WHERE conrelid = 'sessoes'::regclass 
    AND conname IN ('sessoes_local_check', 'sessoes_tipo_check')
""")
for row in cursor.fetchall():
    print(f"   {row[0]}")
    print(f"   {row[1]}")

# Drop constraints
print("\n2. Dropping constraints...")
cursor.execute("ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_local_check")
cursor.execute("ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_tipo_check")
conn.commit()
print("   ✓ Constraints dropped")

# Add case-insensitive constraints
print("\n3. Adding case-insensitive constraints...")

# Local constraint - accept any case
cursor.execute("""
    ALTER TABLE sessoes ADD CONSTRAINT sessoes_local_check 
    CHECK (local IS NULL OR LOWER(local) IN ('casa', 'fora', 'neutro'))
""")

# Tipo constraint - accept any case
cursor.execute("""
    ALTER TABLE sessoes ADD CONSTRAINT sessoes_tipo_check 
    CHECK (LOWER(tipo) IN ('treino', 'jogo'))
""")

conn.commit()
print("   ✓ Case-insensitive constraints added")

# Verify
print("\n4. Verifying new constraints:")
cursor.execute("""
    SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
    FROM pg_constraint 
    WHERE conrelid = 'sessoes'::regclass 
    AND conname IN ('sessoes_local_check', 'sessoes_tipo_check')
""")
for row in cursor.fetchall():
    print(f"   ✓ {row[0]}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("✓ Constraints fixed - now accept any case!")
print("=" * 60)

# Test with lowercase values
print("\nTesting session creation with lowercase values...")
import requests
try:
    response = requests.post(
        'http://localhost:8000/api/sessions/',
        json={
            'tipo': 'jogo',  # lowercase
            'data': '2026-02-07',
            'duracao_min': 90,
            'local': 'casa',  # lowercase
            'adversario': 'Test Team',
            'jornada': 22
        }
    )
    if response.status_code in [200, 201]:
        print(f"✓ SUCCESS! Status: {response.status_code}")
        result = response.json()
        print(f"  Session ID: {result.get('id')}")
        print(f"  Type: {result.get('tipo')}")
        print(f"  Location: {result.get('local')}")
        print("\n🎉 Frontend can now create sessions with any case!")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  {response.text[:300]}")
except Exception as e:
    print(f"✗ Error: {e}")
