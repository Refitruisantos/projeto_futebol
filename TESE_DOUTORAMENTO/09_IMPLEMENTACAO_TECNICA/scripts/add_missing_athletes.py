"""
Add missing athletes to database
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

try:
    from conexao_db import DatabaseConnection
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "conexao_db",
        Path(__file__).parent.parent / 'python' / '01_conexao_db.py'
    )
    conexao_db = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conexao_db)
    DatabaseConnection = conexao_db.DatabaseConnection

# Athletes to add
MISSING_ATHLETES = [
    ('PAULO DANIEL', 'GR'),
    ('CESÁRIO', 'DC'),
]

db = DatabaseConnection()

print("\n🔧 Adding missing athletes to database...")

for athlete_name, position in MISSING_ATHLETES:
    # Check if exists
    check = db.query_to_dict(
        "SELECT id FROM atletas WHERE UPPER(nome_completo) = UPPER(%s)",
        (athlete_name,)
    )
    
    if check:
        print(f"   ✓ {athlete_name} already exists (ID: {check[0]['id']})")
    else:
        # Generate jogador_id from name
        jogador_id = athlete_name.replace(' ', '_').upper()[:20]
        
        # Add athlete
        db.execute_query("""
            INSERT INTO atletas (jogador_id, nome_completo, posicao, ativo)
            VALUES (%s, %s, %s, TRUE)
        """, (jogador_id, athlete_name, position))
        
        # Get ID
        result = db.query_to_dict(
            "SELECT id FROM atletas WHERE UPPER(nome_completo) = UPPER(%s)",
            (athlete_name,)
        )
        print(f"   ✅ Added {athlete_name} ({position}) - ID: {result[0]['id']}, jogador_id: {jogador_id}")

db.close()
print("\n✅ Done!")
