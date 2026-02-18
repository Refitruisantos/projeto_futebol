"""
Fix sessoes_local_check constraint
"""
import sys
sys.path.insert(0, 'backend')

from database import DatabaseConnection

def main():
    print("=" * 60)
    print("Fixing sessoes_local_check constraint")
    print("=" * 60)
    
    db = DatabaseConnection()
    
    # Step 1: Check current local values
    print("\n1. Checking current local values...")
    rows = db.query_to_dict('SELECT DISTINCT local FROM sessoes WHERE local IS NOT NULL', ())
    print(f"   Found {len(rows)} distinct values:")
    for row in rows:
        print(f"   - '{row['local']}'")
    
    # Step 2: Update lowercase values to capitalized
    print("\n2. Standardizing values to capitalized format...")
    
    # Map lowercase to capitalized
    value_map = {
        'casa': 'Casa',
        'fora': 'Fora',
        'neutro': 'Neutro'
    }
    
    for old_val, new_val in value_map.items():
        try:
            # Use execute directly, not query_to_dict for UPDATE
            cursor = db.conn.cursor()
            cursor.execute("UPDATE sessoes SET local = %s WHERE LOWER(local) = %s", (new_val, old_val))
            db.conn.commit()
            if cursor.rowcount > 0:
                print(f"   ✓ Updated {cursor.rowcount} rows: '{old_val}' → '{new_val}'")
            cursor.close()
        except Exception as e:
            print(f"   Note: {e}")
    
    # Step 3: Drop existing constraint
    print("\n3. Dropping existing constraint...")
    try:
        db.query_to_dict('ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_local_check', ())
        print("   ✓ Constraint dropped")
    except Exception as e:
        print(f"   Note: {e}")
    
    # Step 4: Add new constraint
    print("\n4. Adding new constraint...")
    try:
        db.query_to_dict(
            "ALTER TABLE sessoes ADD CONSTRAINT sessoes_local_check CHECK (local IS NULL OR local IN ('Casa', 'Fora', 'Neutro'))",
            ()
        )
        print("   ✓ Constraint added successfully")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        db.close()
        return False
    
    # Step 5: Verify constraint
    print("\n5. Verifying constraint...")
    result = db.query_to_dict(
        "SELECT conname, pg_get_constraintdef(pg_constraint.oid) FROM pg_constraint WHERE conrelid = 'sessoes'::regclass AND conname = 'sessoes_local_check'",
        ()
    )
    
    if result:
        print(f"   ✓ Constraint verified: {result[0]['conname']}")
        print(f"   Definition: {result[0]['pg_get_constraintdef']}")
    else:
        print("   ⚠ Constraint not found")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("✓ Constraint fix complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nNow testing session creation...")
            import requests
            response = requests.post(
                'http://localhost:8000/api/sessions/',
                json={
                    'tipo': 'Treino',
                    'data': '2026-02-06',
                    'duracao_min': 90,
                    'local': None
                }
            )
            if response.status_code in [200, 201]:
                print(f"✓ Session creation works! Status: {response.status_code}")
                print(f"  Session ID: {response.json().get('id')}")
            else:
                print(f"✗ Session creation failed: {response.status_code}")
                print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
