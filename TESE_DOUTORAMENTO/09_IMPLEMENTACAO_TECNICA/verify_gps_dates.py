"""
GPS Date Verification Script
Compares GPS file dates with game session dates in database
"""

import sys
sys.path.insert(0, 'python')
from importlib.machinery import SourceFileLoader

# Load database module
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()
db = db_module.DatabaseConnection()

print("=" * 80)
print("GPS FILES vs GAME SESSIONS - DATE VERIFICATION")
print("=" * 80)

# GPS files from insert_catapult_data.py script
gps_files = [
    ('jornada_1_players_en_snake_case.csv', 1, '2025-09-07'),
    ('jornada_2_players_en_snake_case.csv', 2, '2025-09-14'),
    ('jornada_3_players_en_snake_case.csv', 3, '2025-09-21'),
    ('jornada_4_players_en_snake_case.csv', 4, '2025-09-28'),
    ('jornada_5_players_en_snake_case.csv', 5, '2025-10-05'),
]

# Get all game sessions from database
game_sessions = db.query_to_dict("""
    SELECT id, data, jornada, tipo
    FROM sessoes
    WHERE tipo = 'jogo'
    ORDER BY jornada, data
""")

print(f"\nFound {len(game_sessions)} game sessions in database:")
for session in game_sessions:
    print(f"  Session {session['id']:3d} | Jornada {session['jornada']} | {session['data']}")

print("\n" + "=" * 80)
print("DATE COMPARISON")
print("=" * 80)

mismatches = []
matches = []

for csv_file, jornada, expected_date in gps_files:
    # Find corresponding game session in database
    db_sessions = [s for s in game_sessions if s['jornada'] == jornada]
    
    if not db_sessions:
        print(f"\n❌ Jornada {jornada}: {csv_file}")
        print(f"   GPS File expects: {expected_date}")
        print(f"   Database: NO GAME SESSION FOUND")
        mismatches.append({
            'jornada': jornada,
            'file': csv_file,
            'expected_date': expected_date,
            'db_session': None
        })
    else:
        db_session = db_sessions[0]  # Take first game session for this jornada
        db_date = str(db_session['data'])
        
        if expected_date == db_date:
            print(f"\n✅ Jornada {jornada}: {csv_file}")
            print(f"   GPS File date: {expected_date}")
            print(f"   Database date: {db_date}")
            print(f"   Session ID: {db_session['id']}")
            matches.append({
                'jornada': jornada,
                'file': csv_file,
                'session_id': db_session['id'],
                'date': expected_date
            })
        else:
            print(f"\n⚠️  Jornada {jornada}: {csv_file}")
            print(f"   GPS File expects: {expected_date}")
            print(f"   Database has:     {db_date}")
            print(f"   Session ID: {db_session['id']}")
            print(f"   MISMATCH: {expected_date} ≠ {db_date}")
            mismatches.append({
                'jornada': jornada,
                'file': csv_file,
                'expected_date': expected_date,
                'db_date': db_date,
                'db_session': db_session['id']
            })

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✅ Matching dates: {len(matches)}/{len(gps_files)}")
if matches:
    for m in matches:
        print(f"   Jornada {m['jornada']}: {m['file']} → Session {m['session_id']}")

print(f"\n⚠️  Date mismatches: {len(mismatches)}/{len(gps_files)}")
if mismatches:
    for m in mismatches:
        if m['db_session']:
            print(f"   Jornada {m['jornada']}: {m['file']}")
            print(f"     Expected: {m['expected_date']}")
            print(f"     Database: {m['db_date']}")
        else:
            print(f"   Jornada {m['jornada']}: {m['file']} - NO GAME SESSION IN DB")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if len(mismatches) == 0:
    print("\n✅ All GPS file dates match game session dates!")
    print("   Safe to run: python scripts\\insert_catapult_data.py")
elif len(mismatches) == len(gps_files):
    print("\n⚠️  ALL dates mismatch!")
    print("\nOptions:")
    print("  A) Update GPS import script dates to match database")
    print("  B) Update database session dates to match GPS files")
    print("  C) Import anyway (data will link to wrong sessions)")
else:
    print(f"\n⚠️  {len(mismatches)} out of {len(gps_files)} dates mismatch")
    print("\nOptions:")
    print("  A) Fix mismatched dates in import script")
    print("  B) Update database session dates")
    print("  C) Import matching ones only")

# Show actual game session dates for reference
print("\n" + "=" * 80)
print("GAME SESSION DATES IN DATABASE")
print("=" * 80)

for session in game_sessions:
    print(f"Jornada {session['jornada']} | Session {session['id']:3d} | {session['data']}")

print("\n" + "=" * 80)
