# Manual Data Insertion Guide

## Problem: CSV Upload Not Working

The Catapult CSV upload requires **athletes to exist in the database first** because it matches player names. If the `atletas` table is empty, uploads will fail.

---

## Solution 1: Import Athletes CSV (Recommended)

### Step 1: Connect to database
```powershell
psql -h localhost -U postgres -d futebol_tese
```

### Step 2: Import athletes from CSV
```sql
\COPY atletas(jogador_id, nome_completo, data_nascimento, posicao, numero_camisola, pe_dominante, altura_cm, massa_kg) 
FROM 'C:/Users/sorai/CascadeProjects/projeto_futebol/atletas_28_definitivos.csv' 
DELIMITER ',' CSV HEADER;
```

### Step 3: Verify import
```sql
SELECT COUNT(*) FROM atletas;
-- Should show 28 rows

SELECT nome_completo, posicao FROM atletas ORDER BY nome_completo;
-- Should show all athletes
```

### Step 4: Exit and upload GPS data via web UI
```sql
\q
```

Then go to http://localhost:5173/upload and upload the Catapult CSV files.

---

## Solution 2: Manual SQL Insert (If CSV import fails)

If the CSV import doesn't work, use these SQL INSERT statements:

### Insert Athletes Manually

```sql
-- Connect to database first
-- psql -h localhost -U postgres -d futebol_tese

-- Insert all 28 athletes (example - adjust based on your actual data)
INSERT INTO atletas (jogador_id, nome_completo, data_nascimento, posicao, numero_camisola, pe_dominante, altura_cm, massa_kg) VALUES
('DC', 'Duarte Calha', '2000-01-15', 'Medio', 8, 'Direito', 178, 72),
('GC', 'Gabi Coelho', '1999-05-20', 'Medio', 10, 'Direito', 175, 70),
('GA', 'Gaby Alves', '2001-03-12', 'Defesa', 4, 'Direito', 182, 78),
('GCA', 'Gonçalo Cardoso', '2000-08-25', 'Defesa', 3, 'Direito', 185, 80),
('JF', 'João Ferreira', '1998-11-10', 'Avançado', 9, 'Direito', 180, 75),
('LS', 'Leonardo Santos', '1999-07-18', 'Medio', 6, 'Esquerdo', 176, 71),
('LM', 'Lesiandro Marinho', '2000-02-28', 'Medio', 7, 'Direito', 174, 69),
('MS', 'Martim Soares', '2001-06-05', 'Defesa', 2, 'Direito', 183, 79),
('PD', 'Paulo Daniel', '1999-09-14', 'Medio', 5, 'Direito', 177, 73),
('PR', 'Pedro Ribeiro', '2000-04-22', 'Avançado', 11, 'Direito', 179, 74),
('RD', 'Rafael Dias', '1998-12-30', 'Medio', 14, 'Esquerdo', 172, 68),
('RC', 'Rafael Cesário', '1999-10-08', 'Avançado', 19, 'Direito', 181, 76),
('RA', 'Rodrigo Andrade', '2000-07-19', 'Medio', 8, 'Direito', 175, 70),
('YR', 'Yordanov Ricardo', '1998-03-25', 'Avançado', 7, 'Direito', 178, 73);

-- Note: Adjust birth dates, positions, jersey numbers, etc. based on your actual CSV
-- This is just an example with the players from your Catapult CSV
```

### Insert GPS Data Manually (from Jornada 1 CSV)

First, create a session:
```sql
INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao)
VALUES ('2025-09-07', 'jogo', 90, 1, 'Liga Portugal')
RETURNING id;
-- Note the session ID returned (e.g., 3)
```

Then insert GPS data (replace `SESSION_ID` with the actual ID from above):
```sql
-- Get athlete IDs first
SELECT id, nome_completo FROM atletas ORDER BY nome_completo;

-- Insert GPS data for Jornada 1 (example for first few players)
-- Replace ATHLETE_ID with actual IDs from the query above

INSERT INTO dados_gps (time, atleta_id, sessao_id, distancia_total, velocidade_max, aceleracoes, desaceleracoes, effs_19_8_kmh, dist_19_8_kmh, effs_25_2_kmh, fonte)
VALUES
('2025-09-07 15:00:00', 1, 3, 9003, 30.5, 84, 92, 34, 441, 4, 'manual_insert'),
('2025-09-07 15:00:00', 2, 3, 11225, 29.4, 111, 100, 49, 523, 3, 'manual_insert'),
('2025-09-07 15:00:00', 3, 3, 3652, 31.8, 48, 46, 24, 315, 5, 'manual_insert');
-- Continue for all 14 players...
```

---

## Solution 3: Python Script to Insert CSV Data

Create this script: `insert_catapult_data.py`

```python
import sys
import pandas as pd
from pathlib import Path

# Add python folder to path
sys.path.append('python')
from conexao_db import DatabaseConnection

def insert_athletes_from_csv():
    """Insert athletes from CSV"""
    db = DatabaseConnection()
    
    # Read athletes CSV
    athletes_csv = Path('C:/Users/sorai/CascadeProjects/projeto_futebol/atletas_28_definitivos.csv')
    
    if not athletes_csv.exists():
        print(f"❌ Athletes CSV not found: {athletes_csv}")
        return False
    
    df = pd.read_csv(athletes_csv)
    
    print(f"📥 Importing {len(df)} athletes...")
    
    for idx, row in df.iterrows():
        try:
            db.execute_query("""
                INSERT INTO atletas (jogador_id, nome_completo, data_nascimento, posicao, 
                                     numero_camisola, pe_dominante, altura_cm, massa_kg)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                row.get('jogador_id'),
                row.get('nome_completo'),
                row.get('data_nascimento'),
                row.get('posicao'),
                row.get('numero_camisola'),
                row.get('pe_dominante'),
                row.get('altura_cm'),
                row.get('massa_kg')
            ))
            print(f"✅ Inserted: {row.get('nome_completo')}")
        except Exception as e:
            print(f"❌ Error inserting {row.get('nome_completo')}: {e}")
    
    db.close()
    return True


def insert_catapult_csv(csv_path, jornada, session_date='2025-09-07'):
    """Insert Catapult CSV data"""
    db = DatabaseConnection()
    
    # Create session
    session_query = """
        INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao)
        VALUES (%s, 'jogo', 90, %s, 'Liga Portugal')
        ON CONFLICT DO NOTHING
        RETURNING id
    """
    db.execute_query(session_query, (session_date, jornada))
    
    # Get session ID
    session_id_query = """
        SELECT id FROM sessoes WHERE tipo = 'jogo' AND jornada = %s AND data = %s
    """
    session_result = db.query_to_dict(session_id_query, (jornada, session_date))
    
    if not session_result:
        print(f"❌ Failed to create/find session for jornada {jornada}")
        db.close()
        return False
    
    session_id = session_result[0]['id']
    print(f"✅ Session ID: {session_id}")
    
    # Read Catapult CSV
    df = pd.read_csv(csv_path)
    print(f"📥 Processing {len(df)} players from {Path(csv_path).name}...")
    
    inserted = 0
    errors = []
    
    for idx, row in df.iterrows():
        player_name = row['player']
        
        # Find athlete by name
        athlete_query = """
            SELECT id FROM atletas 
            WHERE LOWER(nome_completo) = LOWER(%s)
            LIMIT 1
        """
        athlete_result = db.query_to_dict(athlete_query, (player_name,))
        
        if not athlete_result:
            errors.append(f"Player not found: {player_name}")
            continue
        
        athlete_id = athlete_result[0]['id']
        
        # Insert GPS data
        try:
            db.execute_query("""
                INSERT INTO dados_gps (
                    time, atleta_id, sessao_id,
                    distancia_total, velocidade_max,
                    aceleracoes, desaceleracoes,
                    effs_19_8_kmh, dist_19_8_kmh,
                    effs_25_2_kmh,
                    fonte
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                f'{session_date} 15:00:00',
                athlete_id,
                session_id,
                row['total_distance_m'],
                row['max_velocity_kmh'],
                row['acc_b1_3_total_efforts'],
                row['decel_b1_3_total_efforts'],
                row['efforts_over_19_8_kmh'],
                row['distance_over_19_8_kmh'],
                row['efforts_over_25_2_kmh'],
                f'script_{Path(csv_path).name}'
            ))
            inserted += 1
            print(f"✅ {player_name}: {row['total_distance_m']}m")
        except Exception as e:
            errors.append(f"{player_name}: {str(e)}")
    
    db.close()
    
    print(f"\n📊 Results:")
    print(f"  Inserted: {inserted}/{len(df)}")
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
    
    return inserted > 0


if __name__ == '__main__':
    print("=" * 60)
    print("CATAPULT DATA INSERTION SCRIPT")
    print("=" * 60)
    
    # Step 1: Insert athletes
    print("\n1️⃣ Inserting athletes...")
    if insert_athletes_from_csv():
        print("✅ Athletes imported successfully")
    
    # Step 2: Insert Catapult data for all jornadas
    catapult_folder = Path('C:/Users/sorai/CascadeProjects/projeto_futebol/TESE_DOUTORAMENTO/dadoscatapult')
    
    csv_files = [
        ('jornada_1_players_en_snake_case.csv', 1, '2025-09-07'),
        ('jornada_2_players_en_snake_case.csv', 2, '2025-09-14'),
        ('jornada_3_players_en_snake_case.csv', 3, '2025-09-21'),
        ('jornada_4_players_en_snake_case.csv', 4, '2025-09-28'),
        ('jornada_5_players_en_snake_case.csv', 5, '2025-10-05'),
    ]
    
    print("\n2️⃣ Inserting Catapult GPS data...")
    for csv_file, jornada, date in csv_files:
        csv_path = catapult_folder / csv_file
        if csv_path.exists():
            print(f"\n📁 Processing {csv_file}...")
            insert_catapult_csv(str(csv_path), jornada, date)
        else:
            print(f"⚠️ File not found: {csv_path}")
    
    print("\n" + "=" * 60)
    print("✅ DONE! Check the web UI at http://localhost:5173")
    print("=" * 60)
```

### Run the Python script:
```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

python insert_catapult_data.py
```

---

## Verify Data Insertion

After inserting data, verify it worked:

```sql
-- Check athletes
SELECT COUNT(*) FROM atletas;

-- Check sessions
SELECT * FROM sessoes;

-- Check GPS data
SELECT COUNT(*) FROM dados_gps;

-- View GPS data with athlete names
SELECT 
    s.data,
    s.jornada,
    a.nome_completo,
    g.distancia_total,
    g.velocidade_max
FROM dados_gps g
JOIN atletas a ON g.atleta_id = a.id
JOIN sessoes s ON g.sessao_id = s.id
ORDER BY s.data DESC, a.nome_completo;
```

---

## Troubleshooting

### CSV Import Fails with Encoding Error
If you get UTF-8 encoding errors, try:
```sql
SET client_encoding = 'UTF8';
\COPY atletas... 
```

### Player Names Don't Match
Check exact names in both files:
```sql
SELECT nome_completo FROM atletas ORDER BY nome_completo;
```

Compare with CSV column `player`. Names must match exactly (case-insensitive).

### Web Upload Still Fails
Check backend logs (terminal running uvicorn) for detailed error messages.

Common issues:
- Backend not running
- Athletes table still empty
- Player names don't match
- CSV format incorrect
