# =============================================================================
# PSE DATA INSERTION SCRIPT
# =============================================================================
# Import PSE (Perceived Subjective Exertion) and wellness data from CSV files
# into the dados_pse table for load monitoring and 7-day calculations
#
# CSV COLUMNS (from screenshot):
# - Nome, Pos, Sono, Stress, Fadiga, DOMS, DORES MUSCULARES, VOLUME, Rpe, CARGA
# =============================================================================

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Add python/ folder to system path for DB connection
parent_dir = Path(__file__).resolve().parent.parent
python_dir = parent_dir / "python"
if str(python_dir) not in sys.path:
    sys.path.insert(0, str(python_dir))

import importlib.util
module_path = python_dir / "01_conexao_db.py"
spec = importlib.util.spec_from_file_location("conexao_db", module_path)
conexao_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conexao_db)
DatabaseConnection = conexao_db.DatabaseConnection

# Name mapping (same as GPS script)
NAME_MAPPING = {
    'HUGO SOARES': 'HUGO SOARES',
    'HUGO SOA': 'HUGO SOARES',
    'GONÇALO SANTOS': 'GONÇALO',
    'GONÇALO': 'GONÇALO',
    'MARTIM SILVA': 'MARTIM SILVA',
    'MARTIM SIL': 'MARTIM SILVA',
    'ANDRADE': 'ANDRADE',
    'T. BATISTA': 'T. BATISTA',
    'PEDRO RIBEIRO': 'PEDRO RIBEIRO',
    'PEDRO RIBI': 'PEDRO RIBEIRO',
    'LOURENÇO': 'LOURENÇO',
    'DIGAS': 'DIGAS',
    'CESÁRIO': 'RAFAEL DIAS',
    'BERNARDO MENDES': 'BERNARDO MENDES',
    'BERNARDO': 'BERNARDO MENDES',
    'MÁRIO': 'MÁRIO',
    'PAULO DANIEL': 'ANDRADE',
    'PAULO DAN': 'ANDRADE',
    'DUARTE CALHA': 'DUARTE CALHA',
    'DUARTE CA': 'DUARTE CALHA',
    'MARTIM GOMES': 'MARTIM GOMES',
    'MARTIM GO': 'MARTIM GOMES',
    'GABI COELHO': 'GABI COELHO',
    'GABI COEL': 'GABI COELHO',
    'TIAGO LOBO': 'TIAGO LOBO',
    'TIAGO LOB': 'TIAGO LOBO',
    'NUNO TORRÃO': 'NUNO TORRÃO',
    'NUNO TOR': 'NUNO TORRÃO',
    'RAFAEL DIAS': 'RAFAEL DIAS',
    'RAFAEL DIA': 'RAFAEL DIAS',
    'AVELAR': 'AVELAR',
    'JOÃO FERREIRA': 'JOÃO FERREIRA',
    'JOÃO FERR': 'JOÃO FERREIRA',
    'DIONILDO': 'VILHAÇA',
    'YORDANOV': 'RICARDO',
    'GABY ALVES': 'GABY ALVES',
    'GABY ALVE': 'GABY ALVES',
    'CARDOSO': 'CARDOSO',
    'JOÃO TAVARES': 'T. BATISTA',
    'JOÃO TAVA': 'T. BATISTA',
    'MARINHO': 'MARINHO',
    'MARTIM SOARES': 'HUGO SOARES',
    'LEONARDO': 'LEONARDO',
}

# Jornada dates matching GPS data
JORNADA_DATES = {
    'Jogo1_pse.csv': datetime(2025, 9, 7),
    'jogo2_pse.csv': datetime(2025, 9, 14),
    'jogo3_pse.csv': datetime(2025, 9, 21),
    'jogo4_pse.csv': datetime(2025, 9, 28),
    'jogo5_pse.csv': datetime(2025, 10, 5),
}


def parse_pse_csv(csv_path, jornada_date):
    """
    Parse PSE CSV file - complex structure with multiple sessions per athlete
    """
    print(f"\n📁 {Path(csv_path).name}")
    
    db = DatabaseConnection()
    
    # Get session ID for this jornada
    session_query = """
        SELECT id FROM sessoes 
        WHERE data = %s AND tipo = 'jogo'
        LIMIT 1
    """
    session_result = db.query_to_dict(session_query, (jornada_date,))
    
    if not session_result:
        print(f"  ⚠️ No session found for {jornada_date}")
        db.close()
        return
    
    session_id = session_result[0]['id']
    print(f"  ℹ️ Session ID: {session_id}")
    
    # Read CSV with pandas
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    inserted = 0
    errors = []
    
    # Process each row (each athlete)
    for idx, row in df.iterrows():
        if idx < 2:  # Skip header rows
            continue
            
        athlete_name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else None
        if not athlete_name or athlete_name == 'nan' or athlete_name == '':
            continue
        
        # Map name
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
            continue
        
        athlete_id = athlete_result[0]['id']
        
        # Extract PSE data from row
        # Columns: Nome, Pos, Sono, Stress, Fadiga, DOMS, ..., VOLUME, Rpe, CARGA
        # Note: CSV uses 1-10 scale for wellness, DB expects 1-5, so divide by 2
        try:
            sono_raw = int(row.iloc[2]) if pd.notna(row.iloc[2]) and str(row.iloc[2]).strip() != '' else None
            sono = int(sono_raw / 2) if sono_raw else None  # Scale 1-10 → 1-5
            
            stress_raw = int(row.iloc[3]) if pd.notna(row.iloc[3]) and str(row.iloc[3]).strip() != '' else None
            stress = int(stress_raw / 2) if stress_raw else None  # Scale 1-10 → 1-5
            
            fadiga = int(row.iloc[4]) if pd.notna(row.iloc[4]) and str(row.iloc[4]).strip() != '' else None
            doms = int(row.iloc[5]) if pd.notna(row.iloc[5]) and str(row.iloc[5]).strip() != '' else None
            volume = int(row.iloc[8]) if pd.notna(row.iloc[8]) and str(row.iloc[8]).strip() != '' else None
            rpe = int(row.iloc[9]) if pd.notna(row.iloc[9]) and str(row.iloc[9]).strip() != '' else None
            carga = int(row.iloc[10]) if pd.notna(row.iloc[10]) and str(row.iloc[10]).strip() != '' else None
            
            # Skip if no RPE data
            if not rpe or not volume:
                continue
            
            # Insert PSE data - add time to date
            pse_timestamp = jornada_date.replace(hour=15, minute=0, second=0)
            
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
                float(rpe),
                volume,
                float(carga) if carga else float(rpe * volume),
                sono,
                stress,
                fadiga,
                doms
            ))
            
            inserted += 1
            print(f"    ✅ {athlete_name}: RPE={rpe}, Load={carga}")
            
        except Exception as e:
            errors.append(f"{athlete_name}: {str(e)}")
    
    db.close()
    
    print(f"  📊 Inserted: {inserted}")
    if errors:
        print(f"  ⚠️ Errors ({len(errors)}):")
        for err in errors[:5]:
            print(f"    - {err}")


def main():
    print("=" * 70)
    print("INSERTING PSE DATA")
    print("=" * 70)
    
    # PSE CSV files directory
    pse_dir = Path(__file__).resolve().parent.parent.parent / "dadosPSE"
    
    if not pse_dir.exists():
        print(f"❌ PSE directory not found: {pse_dir}")
        return
    
    # Process each PSE file
    processed = 0
    for filename, jornada_date in JORNADA_DATES.items():
        csv_path = pse_dir / filename
        if csv_path.exists():
            parse_pse_csv(csv_path, jornada_date)
            processed += 1
    
    print("\n" + "=" * 70)
    print(f"✅ DONE! Processed {processed} PSE files")
    print("=" * 70)


if __name__ == "__main__":
    main()
