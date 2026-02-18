"""
Fix Game Session Dates and Import GPS Data
1. Updates game session dates to match actual GPS file dates
2. Creates missing Jornada 5 game session
3. Imports GPS data from Catapult CSV files
"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, 'python')
from importlib.machinery import SourceFileLoader

db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()
db = db_module.DatabaseConnection()

print("=" * 80)
print("FIX GAME DATES & IMPORT GPS DATA")
print("=" * 80)

# Step 1: Update existing game session dates
print("\n📅 STEP 1: Updating game session dates...")
print("-" * 80)

date_updates = [
    (128, 1, '2025-09-07'),  # Session 128 (Jornada 1)
    (134, 2, '2025-09-14'),  # Session 134 (Jornada 2)
    (140, 3, '2025-09-21'),  # Session 140 (Jornada 3)
    (146, 4, '2025-09-28'),  # Session 146 (Jornada 4)
]

for session_id, jornada, new_date in date_updates:
    db.execute_query(
        "UPDATE sessoes SET data = %s WHERE id = %s",
        (new_date, session_id)
    )
    print(f"  ✅ Session {session_id} (Jornada {jornada}): Updated to {new_date}")

# Step 2: Create Jornada 5 game session
print("\n⚽ STEP 2: Creating Jornada 5 game session...")
print("-" * 80)

# Check if Jornada 5 game already exists
existing_j5 = db.query_to_dict("""
    SELECT id FROM sessoes 
    WHERE tipo = 'jogo' AND jornada = 5
""")

if existing_j5:
    session_5_id = existing_j5[0]['id']
    # Update existing session date
    db.execute_query(
        "UPDATE sessoes SET data = %s WHERE id = %s",
        ('2025-10-05', session_5_id)
    )
    print(f"  ✅ Updated existing Jornada 5 game (Session {session_5_id}) to 2025-10-05")
else:
    # Create new Jornada 5 game session
    db.execute_query("""
        INSERT INTO sessoes (data, tipo, jornada, duracao_min)
        VALUES (%s, 'jogo', 5, 90)
    """, ('2025-10-05',))
    
    new_session = db.query_to_dict("""
        SELECT id FROM sessoes 
        WHERE tipo = 'jogo' AND jornada = 5
    """)
    
    session_5_id = new_session[0]['id']
    print(f"  ✅ Created new Jornada 5 game session (Session {session_5_id}) on 2025-10-05")

# Step 3: Import GPS data
print("\n📊 STEP 3: Importing GPS data from Catapult files...")
print("-" * 80)

# Name mapping for player matching
NAME_MAPPING = {
    'Gonçalo Cardoso': 'CARDOSO',
    'Goncalo Cardoso': 'CARDOSO',
    'Leonardo Santos': 'LEONARDO',
    'Lesiandro Marinho': 'MARINHO',
    'Martim Soares': 'MARTIM SILVA',
    'Paulo Daniel': 'PAULO DANIEL',
    'Rafael Cesário': 'CESÁRIO',
    'Rafael Cesario': 'CESÁRIO',
    'Rodrigo Andrade': 'ANDRADE',
    'Yordanov Ricardo': 'RICARDO',
    'Dionildo Vilhete': 'VILHAÇA',
    'Goncalo GR': 'GONÇALO',
    'Joao Ferreira': 'JOÃO FERREIRA',
    'João Ferreira': 'JOÃO FERREIRA',
    'Nuno Torrao': 'NUNO TORRÃO',
    'Nuno Torrão': 'NUNO TORRÃO',
    'Joao Tavares': 'T. BATISTA',
    'João Tavares': 'T. BATISTA',
    'Tiago Batista': 'T. BATISTA',
    'Soares': 'HUGO SOARES',
    'Yordanov Ricrado': 'RICARDO',
}

gps_files = [
    ('jornada_1_players_en_snake_case.csv', 1, '2025-09-07', 128),
    ('jornada_2_players_en_snake_case.csv', 2, '2025-09-14', 134),
    ('jornada_3_players_en_snake_case.csv', 3, '2025-09-21', 140),
    ('jornada_4_players_en_snake_case.csv', 4, '2025-09-28', 146),
    ('jornada_5_players_en_snake_case.csv', 5, '2025-10-05', session_5_id),
]

catapult_folder = Path(r'C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadoscatapult')

total_imported = 0
total_files = 0
total_errors = []

for csv_file, jornada, date, session_id in gps_files:
    csv_path = catapult_folder / csv_file
    
    if not csv_path.exists():
        print(f"  ⚠️ File not found: {csv_file}")
        continue
    
    print(f"\n📁 {csv_file} (Jornada {jornada}, Session {session_id})")
    
    df = pd.read_csv(csv_path)
    imported = 0
    errors = []
    
    for idx, row in df.iterrows():
        player_name = row['player'].strip()
        
        # Map player name
        mapped_name = NAME_MAPPING.get(player_name, player_name)
        
        # Find athlete in database
        athlete_query = """
            SELECT id, nome_completo FROM atletas 
            WHERE UPPER(nome_completo) = UPPER(%s)
            LIMIT 1
        """
        athlete_result = db.query_to_dict(athlete_query, (mapped_name,))
        
        if not athlete_result:
            errors.append(f"Player not found: {player_name} (mapped: {mapped_name})")
            continue
        
        athlete_id = athlete_result[0]['id']
        
        try:
            # Insert GPS data
            db.execute_query("""
                INSERT INTO dados_gps (
                    time, atleta_id, sessao_id,
                    distancia_total, velocidade_max,
                    aceleracoes, desaceleracoes,
                    effs_19_8_kmh, dist_19_8_kmh,
                    effs_25_2_kmh,
                    tot_effs_gen2,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
            """, (
                f'{date} 15:00:00',
                athlete_id,
                session_id,
                float(row['total_distance_m']) if pd.notna(row.get('total_distance_m')) else None,
                float(row['max_velocity_kmh']) if pd.notna(row.get('max_velocity_kmh')) else None,
                int(row['acc_b1_3_total_efforts']) if pd.notna(row.get('acc_b1_3_total_efforts')) else None,
                int(row['decel_b1_3_total_efforts']) if pd.notna(row.get('decel_b1_3_total_efforts')) else None,
                int(row['efforts_over_19_8_kmh']) if pd.notna(row.get('efforts_over_19_8_kmh')) else None,
                float(row['distance_over_19_8_kmh']) if pd.notna(row.get('distance_over_19_8_kmh')) else None,
                int(row['efforts_over_25_2_kmh']) if pd.notna(row.get('efforts_over_25_2_kmh')) else None,
                int(row['velocity_b3_plus_total_efforts']) if pd.notna(row.get('velocity_b3_plus_total_efforts')) else None,
            ))
            imported += 1
            print(f"    ✅ {player_name}: {row['total_distance_m']}m")
        except Exception as e:
            errors.append(f"{player_name}: {str(e)}")
    
    print(f"  📊 Imported: {imported}/{len(df)} players")
    if errors:
        print(f"  ⚠️ Errors: {len(errors)}")
        for err in errors[:3]:
            print(f"    - {err}")
        if len(errors) > 3:
            print(f"    ... and {len(errors)-3} more")
        total_errors.extend(errors)
    
    total_imported += imported
    total_files += 1

# Verification
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

# Count GPS records
gps_count = db.query_to_dict("SELECT COUNT(*) as count FROM dados_gps")[0]['count']
print(f"\nTotal GPS records in database: {gps_count}")

# Count by session
session_counts = db.query_to_dict("""
    SELECT s.id, s.jornada, s.data, COUNT(g.atleta_id) as athletes
    FROM sessoes s
    LEFT JOIN dados_gps g ON g.sessao_id = s.id
    WHERE s.tipo = 'jogo'
    GROUP BY s.id, s.jornada, s.data
    ORDER BY s.jornada
""")

print("\nGPS data by game session:")
for sc in session_counts:
    print(f"  Jornada {sc['jornada']} | Session {sc['id']:3d} | {sc['data']} | {sc['athletes']} athletes")

print("\n" + "=" * 80)
print(f"✅ COMPLETE!")
print("=" * 80)
print(f"\nImported {total_imported} GPS records from {total_files} files")
if total_errors:
    print(f"⚠️ Total errors: {len(total_errors)}")
print("\n🔄 Refresh your browser to see GPS data in the dashboard!")
print("=" * 80)
