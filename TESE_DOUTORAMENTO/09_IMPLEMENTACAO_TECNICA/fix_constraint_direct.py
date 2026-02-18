"""Direct database constraint fix using psycopg2"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connect directly
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5433'),
    database=os.getenv('DB_NAME', 'futebol_tese'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres')
)

cursor = conn.cursor()

print("=" * 60)
print("Fixing sessoes_local_check constraint")
print("=" * 60)

# Step 1: Drop existing constraint FIRST
print("\n1. Dropping existing constraint...")
try:
    cursor.execute("ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_local_check")
    conn.commit()
    print("   ✓ Constraint dropped")
except Exception as e:
    print(f"   Note: {e}")

# Step 2: Update lowercase values
print("\n2. Updating lowercase values to capitalized...")
cursor.execute("UPDATE sessoes SET local = 'Casa' WHERE LOWER(local) = 'casa'")
casa_count = cursor.rowcount
cursor.execute("UPDATE sessoes SET local = 'Fora' WHERE LOWER(local) = 'fora'")
fora_count = cursor.rowcount
cursor.execute("UPDATE sessoes SET local = 'Neutro' WHERE LOWER(local) = 'neutro'")
neutro_count = cursor.rowcount
conn.commit()
print(f"   ✓ Updated {casa_count} 'casa' → 'Casa'")
print(f"   ✓ Updated {fora_count} 'fora' → 'Fora'")
print(f"   ✓ Updated {neutro_count} 'neutro' → 'Neutro'")

# Step 3: Add new constraint
print("\n3. Adding new constraint...")
cursor.execute("""
    ALTER TABLE sessoes ADD CONSTRAINT sessoes_local_check 
    CHECK (local IS NULL OR local IN ('Casa', 'Fora', 'Neutro'))
""")
conn.commit()
print("   ✓ Constraint added")

# Step 4: Verify
print("\n4. Verifying constraint...")
cursor.execute("""
    SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
    FROM pg_constraint 
    WHERE conrelid = 'sessoes'::regclass AND conname = 'sessoes_local_check'
""")
result = cursor.fetchone()
if result:
    print(f"   ✓ Constraint: {result[0]}")
    print(f"   Definition: {result[1]}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("✓ Constraint fixed successfully!")
print("=" * 60)

# Test session creation
print("\nTesting session creation...")
import requests
try:
    response = requests.post(
        'http://localhost:8000/api/sessions/',
        json={'tipo': 'Treino', 'data': '2026-02-06', 'duracao_min': 90, 'local': None}
    )
    if response.status_code in [200, 201]:
        print(f"✓ Session creation works! Status: {response.status_code}")
        print(f"  Session ID: {response.json().get('id')}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {e}")
