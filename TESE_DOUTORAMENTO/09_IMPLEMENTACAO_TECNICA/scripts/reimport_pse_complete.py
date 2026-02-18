"""
Complete PSE Data Re-import Script
Creates all 30 sessions (5 jornadas × 6 sessions each)
Sessions 1-5: treino, Session 6: jogo
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from importlib.machinery import SourceFileLoader
db_module = SourceFileLoader('conexao_db', os.path.join(os.path.dirname(__file__), '..', 'python', '01_conexao_db.py')).load_module()

def main():
    db = db_module.DatabaseConnection()
    
    # Get a dedicated connection for this entire import
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("COMPLETE PSE DATA RE-IMPORT")
    print("=" * 80)
    
    # Load cleaned PSE data
    csv_path = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadosPSE\ALL_PSE_LONG_cleaned.csv"
    print(f"\nLoading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} PSE records")
    
    # Step 1: Delete existing data
    print("\n" + "=" * 80)
    print("STEP 1: Deleting existing PSE data and sessions")
    print("=" * 80)
    
    # Get counts before deletion
    existing_pse = db.query_to_dict("SELECT COUNT(*) as count FROM dados_pse")[0]['count']
    existing_sessions = db.query_to_dict("SELECT COUNT(*) as count FROM sessoes")[0]['count']
    
    print(f"\nCurrent database:")
    print(f"  - PSE records: {existing_pse}")
    print(f"  - Sessions: {existing_sessions}")
    
    print("\nDeleting...")
    cursor.execute("DELETE FROM dados_pse")
    print("  ✅ Deleted all PSE records")
    
    cursor.execute("DELETE FROM sessoes WHERE id > 1")  # Keep session 1 if it exists
    cursor.execute("DELETE FROM sessoes WHERE id = 1")  # Then delete session 1 too
    conn.commit()
    print("  ✅ Deleted all sessions")
    
    # Step 2: Create all sessions
    print("\n" + "=" * 80)
    print("STEP 2: Creating 30 sessions (5 jornadas × 6 sessions)")
    print("=" * 80)
    
    # Get unique jornada-session combinations from CSV
    session_combos = df[['Jornada', 'Session']].drop_duplicates().sort_values(['Jornada', 'Session'])
    
    print(f"\nUnique combinations in CSV: {len(session_combos)}")
    
    # Base date for sessions (start from Sep 7, 2025)
    base_date = datetime(2025, 9, 7)
    session_id_map = {}  # Maps (jornada, session_num) -> session_id
    
    session_counter = 0
    for _, row in session_combos.iterrows():
        jornada = int(row['Jornada'])
        session_num = int(row['Session'])
        
        # Determine session type
        tipo = 'jogo' if session_num == 6 else 'treino'
        
        # Calculate date: each jornada is ~7 days apart, sessions within jornada are spread
        # Session 6 (game) is at end of week
        days_offset = (jornada - 1) * 7 + (session_num - 1)
        session_date = base_date + timedelta(days=days_offset)
        
        # Insert session
        insert_query = """
            INSERT INTO sessoes (data, tipo, jornada, duracao_min)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        
        cursor.execute(insert_query, (session_date, tipo, jornada, 90))
        session_id = cursor.fetchone()[0]
        session_id_map[(jornada, session_num)] = session_id
        session_counter += 1
        
        print(f"  ✅ Created session {session_id:2d} | Jornada {jornada} #{session_num} | {tipo:6s} | {session_date.date()}")
    
    print(f"\n✅ Created {session_counter} sessions")
    
    # Commit sessions to make them visible for foreign key constraints
    print("\nCommitting sessions to database...")
    conn.commit()
    
    # Step 3: Import PSE data
    print("\n" + "=" * 80)
    print("STEP 3: Importing PSE data")
    print("=" * 80)
    
    # Get athlete name to ID mapping
    athletes = db.query_to_dict("SELECT id, nome_completo FROM atletas")
    athlete_map = {}
    for a in athletes:
        # Try exact match and also normalized versions
        name = a['nome_completo'].strip().upper()
        athlete_map[name] = a['id']
        # Also map without "SANTOS", "SILVA" etc for partial matches
        first_name = name.split()[0]
        if first_name not in athlete_map:
            athlete_map[first_name] = a['id']
    
    print(f"\nMapped {len(athletes)} athletes")
    
    imported_count = 0
    skipped_count = 0
    
    for idx, row in df.iterrows():
        athlete_name = str(row['Athlete']).strip().upper()
        jornada = int(row['Jornada'])
        session_num = int(row['Session'])
        
        # Get athlete ID
        athlete_id = None
        if athlete_name in athlete_map:
            athlete_id = athlete_map[athlete_name]
        else:
            # Try first name only
            first_name = athlete_name.split()[0]
            if first_name in athlete_map:
                athlete_id = athlete_map[first_name]
        
        if not athlete_id:
            skipped_count += 1
            continue
        
        # Get session ID
        session_key = (jornada, session_num)
        if session_key not in session_id_map:
            skipped_count += 1
            continue
        
        session_id = session_id_map[session_key]
        
        # Calculate session date for timestamp
        days_offset = (jornada - 1) * 7 + (session_num - 1)
        session_datetime = base_date + timedelta(days=days_offset)
        session_datetime = session_datetime.replace(hour=15, minute=0, second=0)
        
        # Insert PSE record
        insert_pse = """
            INSERT INTO dados_pse (
                time, atleta_id, sessao_id, pse, duracao_min, carga_total,
                qualidade_sono, fadiga, stress, dor_muscular
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Get values from CSV (handle NaN)
        def get_val(col):
            val = row.get(col)
            return None if pd.isna(val) else float(val)
        
        # Skip records with no volume (constraint requires duracao_min > 0)
        volume = get_val('Volume')
        rpe = get_val('RPE')
        
        # Skip if volume or RPE is missing/invalid (constraints require > 0)
        if volume is None or volume <= 0 or rpe is None or rpe <= 0:
            skipped_count += 1
            continue
        
        cursor.execute(insert_pse, (
            session_datetime,
            athlete_id,
            session_id,
            get_val('RPE'),
            volume,
            get_val('Carga'),
            get_val('Sono'),
            get_val('Fadiga'),
            get_val('Stress'),
            get_val('DOMS')
        ))
        
        imported_count += 1
        
        if imported_count % 100 == 0:
            print(f"  Imported {imported_count} records...")
    
    print(f"\n✅ Imported {imported_count} PSE records")
    if skipped_count > 0:
        print(f"⚠️  Skipped {skipped_count} records (athlete/session not found)")
    
    # Commit all PSE data
    print("\nCommitting PSE data...")
    conn.commit()
    
    # Step 4: Verification
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Count sessions by type
    session_counts = db.query_to_dict("""
        SELECT tipo, COUNT(*) as count
        FROM sessoes
        GROUP BY tipo
        ORDER BY tipo
    """)
    
    print("\nSessions by type:")
    for sc in session_counts:
        print(f"  {sc['tipo']}: {sc['count']} sessions")
    
    # Count PSE records
    cursor.execute("SELECT COUNT(*) as count FROM dados_pse")
    pse_count = cursor.fetchone()[0]
    print(f"\nTotal PSE records: {pse_count}")
    
    # Close cursor and return connection
    cursor.close()
    db.return_connection(conn)
    
    # Sessions per jornada
    jornada_counts = db.query_to_dict("""
        SELECT jornada, COUNT(*) as sessions, tipo
        FROM sessoes
        GROUP BY jornada, tipo
        ORDER BY jornada, tipo
    """)
    
    print("\nSessions per jornada:")
    current_jornada = None
    for jc in jornada_counts:
        if current_jornada != jc['jornada']:
            if current_jornada is not None:
                print()
            current_jornada = jc['jornada']
            print(f"  Jornada {jc['jornada']}:", end="")
        print(f" {jc['tipo']}={jc['sessions']}", end="")
    print()
    
    print("\n" + "=" * 80)
    print("✅ RE-IMPORT COMPLETE!")
    print("=" * 80)
    print("\nRefresh your browser to see all training sessions and games!")
    print("Use the filter buttons: Todas / Treino / Jogos")
    print("=" * 80)

if __name__ == "__main__":
    main()
