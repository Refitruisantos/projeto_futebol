# =============================================================================
# CATAPULT DATA INSERTION SCRIPT
# =============================================================================
# This script automates the process of importing athlete and GPS data into
# the PostgreSQL + TimescaleDB database.
#
# WHAT IT DOES:
# 1. Reads athlete data from CSV (atletas_28_definitivos.csv)
# 2. Maps position abbreviations (LAT, MED, EXT) to database format (DL, MC, EX)
# 3. Inserts athletes into the 'atletas' table
# 4. Reads Catapult GPS CSV files for each jornada (match)
# 5. Matches player names from Catapult CSVs to database athletes
# 6. Creates sessions for each jornada if they don't exist
# 7. Inserts GPS metrics into the 'dados_gps' hypertable
#
# DEPENDENCIES:
# - pandas: for CSV reading and data manipulation
# - psycopg2: for PostgreSQL database connection (via 01_conexao_db.py)
# =============================================================================

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add the python/ folder to the system path so we can import the DB connection module
parent_dir = Path(__file__).resolve().parent.parent
python_dir = parent_dir / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

# Dynamically load the 01_conexao_db.py module
# (Can't use normal import because filename starts with a number)
import importlib.util

module_path = python_dir / "01_conexao_db.py"
spec = importlib.util.spec_from_file_location("conexao_db", module_path)
conexao_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conexao_db)

# Get the DatabaseConnection class from the loaded module
DatabaseConnection = conexao_db.DatabaseConnection

# =============================================================================
# NAME MAPPING: Catapult Full Names → Database Short Names
# =============================================================================
# The Catapult CSVs use full names (e.g., "Gonçalo Cardoso")
# but the athletes CSV has short names/nicknames (e.g., "CARDOSO")
# This dictionary maps between them for player matching
NAME_MAPPING = {
    'Gonçalo Cardoso': 'CARDOSO',
    'Goncalo Cardoso': 'CARDOSO',  # Without accent
    'Leonardo Santos': 'LEONARDO',
    'Lesiandro Marinho': 'MARINHO',
    'Martim Soares': 'MARTIM SILVA',  # Might be "HUGO SOARES" or "MARTIM SILVA" (GR)
    'Paulo Daniel': 'ANDRADE',  # Could be "ANDRADE" or another player
    'Rafael Cesário': 'RAFAEL DIAS',  # Assuming same player, different name format
    'Rafael Cesario': 'RAFAEL DIAS',  # Without accent
    'Rodrigo Andrade': 'ANDRADE',
    'Yordanov Ricardo': 'RICARDO',
    'Dionildo Vilhete': 'VILHAÇA',  # Likely "VILHAÇA"
    'Goncalo GR': 'GONÇALO',  # Goalkeeper
    'Joao Ferreira': 'JOÃO FERREIRA',
    'João Ferreira': 'JOÃO FERREIRA',
    'Nuno Torrao': 'NUNO TORRÃO',
    'Nuno Torrão': 'NUNO TORRÃO',
    'Joao Tavares': 'T. BATISTA',  # Could be "T. BATISTA" or another player
    'João Tavares': 'T. BATISTA',
    'Tiago Batista': 'T. BATISTA',  # Same player as João Tavares
    'Soares': 'HUGO SOARES',  # Likely the GR
    'Yordanov Ricrado': 'RICARDO',  # Typo in CSV (should be "Ricardo")
}


def insert_athletes_from_csv():
    """
    STEP 1: Import athletes from CSV into the database
    
    READS FROM: C:/Users/sorai/CascadeProjects/projeto_futebol/atletas_28_definitivos.csv
    CSV FORMAT: num, nome, posicao
    
    POSITION MAPPING:
    The CSV uses Portuguese abbreviations that need to be mapped to database format:
    - LAT (Lateral) → DL (Defesa Lateral)
    - DC (Defesa Central) → DC (unchanged)
    - MED (Medio) → MC (Médio Centro)
    - EXT (Extremo) → EX (Extremo)
    - GR (Guarda-Redes) → GR (unchanged)
    - AV (Avançado) → AV (unchanged)
    
    DATABASE CONSTRAINT:
    The 'atletas' table has a CHECK constraint that only allows:
    posicao IN ('GR', 'DC', 'DL', 'MC', 'EX', 'AV')
    
    RETURNS: True if at least 1 athlete was inserted, False otherwise
    """
    db = DatabaseConnection()
    
    athletes_csv = Path('C:/Users/sorai/CascadeProjects/projeto_futebol/atletas_28_definitivos.csv')
    
    if not athletes_csv.exists():
        print(f"❌ Athletes CSV not found: {athletes_csv}")
        return False
    
    df = pd.read_csv(athletes_csv)
    
    print(f"📥 Importing {len(df)} athletes...")
    print(f"📋 CSV columns: {list(df.columns)}")
    
    # Position mapping: CSV abbreviations → Database format
    # This ensures compatibility with the database CHECK constraint
    position_map = {
        'LAT': 'DL',  # Lateral → Defesa Lateral
        'DC': 'DC',   # Defesa Central (unchanged)
        'MED': 'MC',  # Medio → Médio Centro
        'EXT': 'EX',  # Extremo (shortened)
        'GR': 'GR',   # Guarda-Redes (unchanged)
        'AV': 'AV'    # Avançado (unchanged)
    }
    
    inserted = 0  # Counter for successfully inserted athletes
    
    # Process each row in the CSV
    for idx, row in df.iterrows():
        try:
            # Extract and clean the data from CSV columns
            # IMPORTANT: Keep original case for names (don't uppercase)
            # This allows proper matching with Catapult CSVs later
            nome = row.get('nome', '').strip() if pd.notna(row.get('nome')) else None
            num = int(row.get('num')) if pd.notna(row.get('num')) else None
            posicao_csv = row.get('posicao', '').strip() if pd.notna(row.get('posicao')) else None
            
            # Map the CSV position abbreviation to database format
            posicao = position_map.get(posicao_csv, posicao_csv)
            
            # Validation: Skip if name is missing
            if not nome:
                print(f"  ⚠️ Skipping row {idx+1}: missing name")
                continue
            
            # Validation: Skip if position is invalid (not in allowed list)
            if posicao not in ['GR', 'DC', 'DL', 'MC', 'EX', 'AV']:
                print(f"  ⚠️ Skipping {nome}: invalid position '{posicao_csv}'")
                continue
            
            # Insert athlete into database
            # jogador_id = name (used as unique identifier)
            # nome_completo = full name
            # ON CONFLICT DO NOTHING = skip if athlete already exists
            db.execute_query("""
                INSERT INTO atletas (jogador_id, nome_completo, posicao, numero_camisola)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                nome,      # jogador_id
                nome,      # nome_completo
                posicao,   # mapped position (DL, MC, EX, etc.)
                num        # numero_camisola
            ))
            inserted += 1
            print(f"  ✅ {nome} ({posicao}, #{num})")
            
        except Exception as e:
            # Log any errors but continue processing other athletes
            print(f"  ❌ Error inserting {row.get('nome')}: {e}")
    
    db.close()
    print(f"✅ Inserted {inserted}/{len(df)} athletes\n")
    return inserted > 0


def insert_catapult_csv(csv_path, jornada, session_date='2025-09-07'):
    """
    STEP 2: Import GPS data from Catapult CSV files
    
    PROCESS:
    1. Check if a session already exists for this jornada + date
    2. Create new session if needed (tipo='jogo', duracao_min=90)
    3. Read Catapult CSV with player GPS metrics
    4. For each player:
       a. Match player name to athlete in database (case-insensitive)
       b. Insert GPS metrics into dados_gps hypertable
       c. Handle duplicates with ON CONFLICT DO NOTHING
    
    CATAPULT CSV FORMAT:
    player, total_distance_m, max_velocity_kmh, acc_b1_3_total_efforts,
    decel_b1_3_total_efforts, efforts_over_19_8_kmh, distance_over_19_8_kmh,
    efforts_over_25_2_kmh, velocity_b3_plus_total_efforts
    
    ARGS:
        csv_path: Full path to Catapult CSV file
        jornada: Match number (1, 2, 3, ...)
        session_date: Date of the match (YYYY-MM-DD format)
    
    RETURNS: True if at least 1 GPS record was inserted, False otherwise
    """
    db = DatabaseConnection()
    
    # -------------------------------------------------------------------------
    # PART A: Get or Create Session
    # -------------------------------------------------------------------------
    # Check if a session already exists for this jornada + date
    # This prevents creating duplicate sessions if script is run multiple times
    check_session = """
        SELECT id FROM sessoes WHERE tipo = 'jogo' AND jornada = %s AND data = %s
    """
    existing_session = db.query_to_dict(check_session, (jornada, session_date))
    
    if existing_session:
        # Session already exists, use its ID
        session_id = existing_session[0]['id']
        print(f"  ℹ️ Using existing session ID: {session_id}")
    else:
        # Create new session for this match
        # tipo='jogo' (match), duracao_min=90 (standard match duration)
        db.execute_query("""
            INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao, created_at)
            VALUES (%s, 'jogo', 90, %s, 'Liga Portugal', NOW())
        """, (session_date, jornada))
        
        # Retrieve the newly created session ID
        session_result = db.query_to_dict(check_session, (jornada, session_date))
        
        if not session_result:
            print(f"  ❌ Failed to create session for jornada {jornada}")
            db.close()
            return False
        
        session_id = session_result[0]['id']
        print(f"  ✅ Created session ID: {session_id}")
    
    df = pd.read_csv(csv_path)
    print(f"  📥 Processing {len(df)} players...")
    
    inserted = 0
    errors = []
    
    # -------------------------------------------------------------------------
    # PART B: Process Each Player in the CSV
    # -------------------------------------------------------------------------
    for idx, row in df.iterrows():
        # Get player name from CSV and clean whitespace
        player_name = row['player'].strip()
        
        # -------------------------------------------------------------------------
        # CRITICAL: Player Name Mapping and Matching
        # -------------------------------------------------------------------------
        # Step 1: Check if this name needs to be mapped to a database name
        # (e.g., "Gonçalo Cardoso" → "CARDOSO")
        mapped_name = NAME_MAPPING.get(player_name, player_name)
        
        # Step 2: Match player name to database using case-insensitive comparison
        # UPPER() function in SQL converts both sides to uppercase for comparison
        # This allows "Duarte Calha" to match "DUARTE CALHA" or "duarte calha"
        athlete_query = """
            SELECT id, nome_completo FROM atletas 
            WHERE UPPER(nome_completo) = UPPER(%s)
            LIMIT 1
        """
        athlete_result = db.query_to_dict(athlete_query, (mapped_name,))
        
        # If player not found in database, skip this row and log error
        if not athlete_result:
            errors.append(f"Player not found: {player_name}")
            continue
        
        # Get the athlete's database ID for foreign key reference
        athlete_id = athlete_result[0]['id']
        
        # -------------------------------------------------------------------------
        # PART C: Insert GPS Metrics into Database
        # -------------------------------------------------------------------------
        try:
            # Insert ALL GPS data columns from Catapult CSV into dados_gps hypertable
            # Mapping: CSV column → Database column
            db.execute_query("""
                INSERT INTO dados_gps (
                    time, atleta_id, sessao_id,
                    distancia_total, velocidade_max,
                    aceleracoes, desaceleracoes,
                    effs_19_8_kmh, dist_19_8_kmh,
                    effs_25_2_kmh,
                    tot_effs_gen2,
                    fonte, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
            """, (
                f'{session_date} 15:00:00',  # time: match date + arbitrary time (3pm)
                athlete_id,                   # FK to atletas table
                session_id,                   # FK to sessoes table
                # ALL GPS metrics from Catapult CSV (9 columns total):
                float(row['total_distance_m']) if pd.notna(row.get('total_distance_m')) else None,
                float(row['max_velocity_kmh']) if pd.notna(row.get('max_velocity_kmh')) else None,
                int(row['acc_b1_3_total_efforts']) if pd.notna(row.get('acc_b1_3_total_efforts')) else None,
                int(row['decel_b1_3_total_efforts']) if pd.notna(row.get('decel_b1_3_total_efforts')) else None,
                int(row['efforts_over_19_8_kmh']) if pd.notna(row.get('efforts_over_19_8_kmh')) else None,
                float(row['distance_over_19_8_kmh']) if pd.notna(row.get('distance_over_19_8_kmh')) else None,
                int(row['efforts_over_25_2_kmh']) if pd.notna(row.get('efforts_over_25_2_kmh')) else None,
                int(row['velocity_b3_plus_total_efforts']) if pd.notna(row.get('velocity_b3_plus_total_efforts')) else None,
                f'script_{Path(csv_path).name}'  # fonte: track data source
            ))
            inserted += 1
            print(f"    ✅ {player_name}: {row['total_distance_m']}m")
        except Exception as e:
            # Log error but continue processing other players
            errors.append(f"{player_name}: {str(e)}")
    
    db.close()
    
    print(f"  📊 Inserted: {inserted}/{len(df)}")
    if errors:
        print(f"  ⚠️ Errors ({len(errors)}):")
        for err in errors[:5]:
            print(f"    - {err}")
        if len(errors) > 5:
            print(f"    ... and {len(errors)-5} more")
    print()
    
    return inserted > 0


if __name__ == '__main__':
    print("=" * 70)
    print(" CATAPULT DATA INSERTION SCRIPT")
    print("=" * 70)
    
    print("\n1️⃣ STEP 1: Inserting athletes from CSV...")
    print("-" * 70)
    if insert_athletes_from_csv():
        print("✅ Athletes imported successfully\n")
    else:
        print("⚠️ No athletes imported\n")
    
    catapult_folder = Path('C:/Users/sorai/CascadeProjects/projeto_futebol/TESE_DOUTORAMENTO/dadoscatapult')
    
    csv_files = [
        ('jornada_1_players_en_snake_case.csv', 1, '2025-09-07'),
        ('jornada_2_players_en_snake_case.csv', 2, '2025-09-14'),
        ('jornada_3_players_en_snake_case.csv', 3, '2025-09-21'),
        ('jornada_4_players_en_snake_case.csv', 4, '2025-09-28'),
        ('jornada_5_players_en_snake_case.csv', 5, '2025-10-05'),
    ]
    
    print("2️⃣ STEP 2: Inserting Catapult GPS data...")
    print("-" * 70)
    
    total_success = 0
    total_files = 0
    
    for csv_file, jornada, date in csv_files:
        csv_path = catapult_folder / csv_file
        if csv_path.exists():
            print(f"📁 {csv_file} (Jornada {jornada})")
            if insert_catapult_csv(str(csv_path), jornada, date):
                total_success += 1
            total_files += 1
        else:
            print(f"⚠️ File not found: {csv_path}\n")
    
    print("=" * 70)
    print(f"✅ DONE! Processed {total_success}/{total_files} files successfully")
    print("=" * 70)
    print("\n🌐 Check the web UI at: http://localhost:5173")
    print("📊 View API docs at: http://localhost:8000/docs")
    print("\nIf dashboard shows errors, run:")
    print("  psql -h localhost -U postgres -d futebol_tese -f sql\\05_funcoes_auxiliares.sql")
    print()
