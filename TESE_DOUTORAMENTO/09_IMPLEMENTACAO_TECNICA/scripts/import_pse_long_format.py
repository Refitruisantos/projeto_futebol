"""
Import PSE Data from Long Format CSV
====================================

Simplified script to import PSE data from long format CSV files into PostgreSQL.
Much simpler than the original wide-format parser!

Usage:
------
python scripts/import_pse_long_format.py ALL_PSE_LONG.csv
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

# Import database connection class
try:
    from conexao_db import DatabaseConnection
except ImportError:
    # Try alternative module name
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "conexao_db",
        Path(__file__).parent.parent / 'python' / '01_conexao_db.py'
    )
    conexao_db = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conexao_db)
    DatabaseConnection = conexao_db.DatabaseConnection


# Athlete name mapping (same as original script)
NAME_MAPPING = {
    'GONÇALO SANTOS': 'GONÇALO SANTOS',
    'Gonálsio Cardoso': 'CARDOSO',
    'JoÃo Ferreira': 'JOÃO FERREIRA',
    'Yordanov Ricrado': 'RICARDO',
    'Martim Gomes ': 'MARTIM GOMES',
    'Gaby Alves ': 'GABI ALVES',
    'Duarte Calha ': 'DUARTE CALHA',
    'Lourenço  ': 'LOURENÇO',
    'Pedro Ribeiro ': 'PEDRO RIBEIRO',
    'Hugo Soares ': 'HUGO SOARES',
    'Digas ': 'DIGAS',
    'T. Batista': 'TIAGO BATISTA',
    'XANATO': 'XANATO',
    'LOURENÇO  ': 'LOURENÇO',
    'PEDRO RIBEIRO ': 'PEDRO RIBEIRO',
    'HUGO SOARES ': 'HUGO SOARES',
    'DIGAS ': 'DIGAS',
    'KIRILL RODRÍGUES': 'KIRILL',
    'YORDANOV RICARDO': 'RICARDO',
}

# Jornada dates (must match sessoes table)
JORNADA_DATES = {
    1: datetime(2025, 9, 7),
    2: datetime(2025, 9, 14),
    3: datetime(2025, 9, 21),
    4: datetime(2025, 9, 28),
    5: datetime(2025, 10, 5),
}


def import_pse_long_format(csv_path: str, delete_existing: bool = False):
    """
    Import PSE data from long format CSV.
    
    Parameters:
    -----------
    csv_path : str
        Path to long format CSV file
    delete_existing : bool
        If True, delete existing PSE data before import
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    print(f"\n📂 Reading: {csv_path.name}")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}")
    
    # Connect to database
    db = DatabaseConnection()
    
    # Optional: Delete existing data
    if delete_existing:
        confirm = input("\n⚠️ Delete all existing PSE data? (yes/no): ")
        if confirm.lower() == 'yes':
            db.execute_query("DELETE FROM dados_pse")
            print("✓ All existing PSE data deleted")
    
    # Import statistics
    inserted = 0
    skipped = 0
    errors = []
    
    print(f"\n🔄 Processing {len(df)} records...")
    
    for idx, row in df.iterrows():
        # Extract data
        athlete_name = str(row['Athlete']).strip()
        jornada = int(row['Jornada'])
        session_num = int(row['Session'])
        
        # Skip invalid records
        if pd.isna(athlete_name) or athlete_name == '' or athlete_name == 'nan':
            skipped += 1
            continue
        
        # Map athlete name
        mapped_name = NAME_MAPPING.get(athlete_name, athlete_name)
        
        # Find athlete in database
        athlete_query = """
            SELECT id FROM atletas 
            WHERE UPPER(nome_completo) = UPPER(%s)
            LIMIT 1
        """
        athlete_result = db.query_to_dict(athlete_query, (mapped_name,))
        
        if not athlete_result:
            errors.append(f"Athlete not found: {athlete_name}")
            skipped += 1
            continue
        
        athlete_id = athlete_result[0]['id']
        
        # Get session date from jornada
        if jornada not in JORNADA_DATES:
            errors.append(f"Unknown jornada: {jornada}")
            skipped += 1
            continue
        
        jornada_date = JORNADA_DATES[jornada]
        
        # Find or create session
        session_query = """
            SELECT id FROM sessoes 
            WHERE data = %s AND tipo = 'jogo'
            LIMIT 1
        """
        session_result = db.query_to_dict(session_query, (jornada_date,))
        
        if session_result:
            session_id = session_result[0]['id']
        else:
            # Create session
            db.execute_query("""
                INSERT INTO sessoes (data, tipo, local, jornada, duracao_min)
                VALUES (%s, 'jogo', 'casa', %s, 90)
                RETURNING id
            """, (jornada_date, jornada))
            session_result = db.query_to_dict(session_query, (jornada_date,))
            session_id = session_result[0]['id']
        
        # Extract metrics with safe conversion
        def safe_value(col_name, scale_factor=1):
            """Safely extract and optionally scale a value."""
            if col_name not in df.columns:
                return None
            val = row[col_name]
            if pd.isna(val):
                return None
            try:
                num_val = float(val)
                if scale_factor != 1:
                    num_val = num_val / scale_factor
                return int(num_val) if num_val == int(num_val) else num_val
            except (ValueError, TypeError):
                return None
        
        # Wellness metrics (scale 1-10 to 1-5 if needed)
        sono = safe_value('Sono', scale_factor=2)  # Scale down if > 5
        stress = safe_value('Stress', scale_factor=2)
        fadiga = safe_value('Fadiga')
        doms = safe_value('DOMS')
        
        # Load metrics
        volume = safe_value('Volume')
        rpe = safe_value('RPE')
        carga = safe_value('Carga')
        
        # Calculate load if missing
        if not carga and rpe and volume:
            carga = rpe * volume
        
        # Skip if no useful data
        if all(v is None for v in [sono, stress, fadiga, doms, rpe, volume, carga]):
            skipped += 1
            continue
        
        # Create timestamp for this session
        pse_timestamp = jornada_date.replace(hour=15, minute=0, second=0)
        
        # Insert into database
        try:
            db.execute_query("""
                INSERT INTO dados_pse (
                    time, atleta_id, sessao_id,
                    pse, duracao_min, carga_total,
                    qualidade_sono, stress, fadiga, dor_muscular,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
            """, (
                pse_timestamp,
                athlete_id,
                session_id,
                rpe,
                volume,
                carga,
                sono,
                stress,
                fadiga,
                doms
            ))
            inserted += 1
            
            if inserted % 50 == 0:
                print(f"   Processed {inserted} records...")
                
        except Exception as e:
            errors.append(f"Error inserting {athlete_name} (row {idx}): {e}")
            skipped += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ IMPORT COMPLETE")
    print(f"{'='*60}")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped: {skipped}")
    print(f"   Total processed: {len(df)}")
    
    if errors:
        print(f"\n⚠️ Errors ({len(errors)}):")
        unique_errors = list(set(errors))[:10]  # Show first 10 unique errors
        for err in unique_errors:
            print(f"   • {err}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more")
    
    # Verify import
    print(f"\n📊 Database verification:")
    count_query = "SELECT COUNT(*) as total FROM dados_pse"
    total = db.query_to_dict(count_query)[0]['total']
    print(f"   Total PSE records in database: {total}")
    
    athletes_query = "SELECT COUNT(DISTINCT atleta_id) as total FROM dados_pse"
    athletes = db.query_to_dict(athletes_query)[0]['total']
    print(f"   Unique athletes with PSE data: {athletes}")
    
    db.close()
    print(f"\n✅ Done!")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Import PSE data from long format CSV file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import from long format CSV
  python import_pse_long_format.py ALL_PSE_LONG.csv
  
  # Delete existing data first
  python import_pse_long_format.py ALL_PSE_LONG.csv --delete-existing
        """
    )
    
    parser.add_argument('csv_file',
                       help='Path to long format PSE CSV file')
    parser.add_argument('--delete-existing', action='store_true',
                       help='Delete existing PSE data before import')
    
    args = parser.parse_args()
    
    try:
        import_pse_long_format(args.csv_file, args.delete_existing)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
