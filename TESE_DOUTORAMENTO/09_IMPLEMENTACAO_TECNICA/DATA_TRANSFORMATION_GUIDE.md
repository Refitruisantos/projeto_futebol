# 📊 DATA TRANSFORMATION GUIDE - Wide to Long Format

**Converting Excel performance data for database ingestion**

---

## 🎯 Problem Statement

Performance data often comes in **wide format** from Excel spreadsheets:
- Multiple sessions as columns (RPE_T1, RPE_T2, DOMS_T1, etc.)
- One row per athlete
- Easy to view in Excel, but **NOT suitable for relational databases**

**Goal:** Transform to **long format** where each row = 1 athlete × 1 session

---

## 📋 Format Comparison

### Wide Format (Input) ❌
```
Athlete     | RPE_T1 | RPE_T2 | DOMS_T1 | DOMS_T2 | Distance_T1 | Distance_T2
------------|--------|--------|---------|---------|-------------|------------
ANDRADE     |   8    |   7    |    3    |    4    |   5000      |   4800
CARDOSO     |   7    |   8    |    2    |    3    |   4900      |   5100
```

**Problems:**
- ❌ Can't query "all RPE values for T1"
- ❌ Can't filter by session
- ❌ Can't join with sessions table
- ❌ Violates database normalization principles

---

### Long Format (Output) ✅
```
Athlete     | Session | RPE | DOMS | Distance
------------|---------|-----|------|----------
ANDRADE     |   T1    |  8  |  3   |  5000
ANDRADE     |   T2    |  7  |  4   |  4800
CARDOSO     |   T1    |  7  |  2   |  4900
CARDOSO     |   T2    |  8  |  3   |  5100
```

**Benefits:**
- ✅ One row per athlete-session observation
- ✅ Easy to query and filter
- ✅ Can join with `sessoes` table on Session ID
- ✅ Ready for TimescaleDB ingestion
- ✅ Follows data science best practices (tidy data principles)

---

## 🔧 Transformation Script

**Location:** `scripts/transform_wide_to_long.py`

### Features

✅ **Auto-detection:** Automatically identifies athlete column and session patterns  
✅ **Flexible input:** Supports Excel (.xlsx, .xls) and CSV files  
✅ **Smart parsing:** Extracts metric names and session IDs from column names  
✅ **Data validation:** Shows statistics and missing value reports  
✅ **Preview:** Displays first 10 rows of transformed data  

---

## 🚀 Usage

### Basic Usage (Auto-detect everything)

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

python scripts\transform_wide_to_long.py input_file.xlsx
```

**Output:** `input_file_long.csv` in same directory

---

### Specify Output File

```powershell
python scripts\transform_wide_to_long.py input.xlsx transformed_data.csv
```

---

### Specify Athlete Column Name

If auto-detection fails or you have a custom column name:

```powershell
python scripts\transform_wide_to_long.py data.xlsx --athlete-col "Nome Completo"
```

---

### Read Specific Excel Sheet

```powershell
# By index (0 = first sheet, 1 = second sheet, etc.)
python scripts\transform_wide_to_long.py data.xlsx --sheet 1

# By name
python scripts\transform_wide_to_long.py data.xlsx --sheet "PSE Data"
```

---

### CSV with Custom Separator

```powershell
# Semicolon separator (common in European CSVs)
python scripts\transform_wide_to_long.py data.csv --csv-sep ";"

# Tab separator
python scripts\transform_wide_to_long.py data.csv --csv-sep "\t"
```

---

### Complete Example

```powershell
python scripts\transform_wide_to_long.py ^
    "C:\Data\performance_data.xlsx" ^
    "C:\Output\performance_long.csv" ^
    --athlete-col "Jogador" ^
    --sheet "Jornada 1-5"
```

---

## 📝 Column Naming Requirements

### Pattern Recognition

The script recognizes session columns using this pattern:
```
METRIC_SESSION
```

**Examples:**
- `RPE_T1`, `RPE_T2`, `RPE_T3` → Metric: RPE, Sessions: T1, T2, T3
- `DOMS_Jogo1`, `DOMS_Jogo2` → Metric: DOMS, Sessions: Jogo1, Jogo2
- `Distance_Session_1` → Metric: Distance, Session: Session_1

### Athlete Column

Auto-detected if column name contains:
- `athlete` / `atleta`
- `nome` / `name`
- `player` / `jogador`

**Tip:** First column is often assumed to be athlete name.

---

## 🔍 Example Transformation

### Input: `sample_wide_format.csv`

```csv
Athlete,RPE_T1,RPE_T2,RPE_T3,DOMS_T1,DOMS_T2,DOMS_T3,Distance_T1,Distance_T2,Distance_T3
ANDRADE,8,7,9,3,4,2,5000,4800,5200
CARDOSO,7,8,7,2,3,3,4900,5100,4950
JOÃO FERREIRA,9,8,8,4,3,4,5300,5000,5150
```

**Command:**
```powershell
python scripts\transform_wide_to_long.py scripts\sample_wide_format.csv
```

### Output: `sample_wide_format_long.csv`

```csv
Athlete,Session,DOMS,Distance,RPE
ANDRADE,T1,3,5000,8
ANDRADE,T2,4,4800,7
ANDRADE,T3,2,5200,9
CARDOSO,T1,2,4900,7
CARDOSO,T2,3,5100,8
CARDOSO,T3,3,4950,7
JOÃO FERREIRA,T1,4,5300,9
JOÃO FERREIRA,T2,3,5000,8
JOÃO FERREIRA,T3,4,5150,8
```

**Statistics:**
```
✓ 3 athletes × 3 sessions = 9 rows
✓ Metrics: DOMS, Distance, RPE
✓ No missing values
```

---

## 📊 Script Output

When you run the script, you'll see:

```
📂 Reading: performance_data.xlsx
   Excel sheet: 0
   Shape: 28 rows × 45 columns
✓ Using athlete column: Athlete
✓ Found 15 sessions: T1, T2, T3, T4, T5, Jogo1, Jogo2, ...
✓ Transformed 28 athletes × 15 sessions = 420 rows

✅ Saved: performance_data_long.csv
   Shape: 420 rows × 12 columns

📊 Preview (first 10 rows):
Athlete         Session  RPE  DOMS  Distance  Sleep  Stress  ...
ANDRADE         T1       8    3     5000      7      4       ...
ANDRADE         T2       7    4     4800      8      3       ...
CARDOSO         T1       7    2     4900      8      3       ...
...

📈 Statistics:
   Unique athletes: 28
   Unique sessions: 15
   Total records: 420
   Metrics: RPE, DOMS, Distance, Sleep, Stress, Fatigue, Load

⚠️ Missing values detected:
   Distance: 45 (10.7%)
   Load: 12 (2.9%)

✅ Transformation completed successfully!
```

---

## 🔄 Integration with Database Import

### Step 1: Transform your data

```powershell
python scripts\transform_wide_to_long.py raw_data.xlsx cleaned_data.csv
```

### Step 2: Create import script

Create a new script `scripts/import_long_format_data.py`:

```python
import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent / 'python'))
from conexao_db import DatabaseConnection

# Read long format CSV
df = pd.read_csv('cleaned_data.csv')

db = DatabaseConnection()

for _, row in df.iterrows():
    # Find athlete ID
    athlete_query = """
        SELECT id FROM atletas 
        WHERE UPPER(nome_completo) = UPPER(%s)
    """
    athlete = db.query_to_dict(athlete_query, (row['Athlete'],))
    
    if not athlete:
        print(f"⚠️ Athlete not found: {row['Athlete']}")
        continue
    
    athlete_id = athlete[0]['id']
    
    # Find session ID (you'll need to map Session to sessao_id)
    # ... session mapping logic ...
    
    # Insert into dados_pse
    db.execute_query("""
        INSERT INTO dados_pse (
            time, atleta_id, sessao_id,
            pse, duracao_min, carga_total,
            qualidade_sono, stress, fadiga, dor_muscular
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT DO NOTHING
    """, (
        session_timestamp,
        athlete_id,
        session_id,
        row['RPE'],
        row.get('Duration'),
        row.get('Load'),
        row.get('Sleep'),
        row.get('Stress'),
        row.get('Fatigue'),
        row.get('DOMS')
    ))
```

---

## 🎯 Use Cases

### 1. PSE/Wellness Data from Excel

**Input columns:**
```
Athlete | RPE_T1 | RPE_T2 | Sleep_T1 | Sleep_T2 | Stress_T1 | Stress_T2 | DOMS_T1 | DOMS_T2
```

**Transform:**
```powershell
python scripts\transform_wide_to_long.py wellness_data.xlsx
```

**Result:** Ready for `dados_pse` table

---

### 2. GPS Data Spread Across Sessions

**Input columns:**
```
Player | Distance_Jogo1 | Distance_Jogo2 | Sprint_Jogo1 | Sprint_Jogo2 | HSR_Jogo1 | HSR_Jogo2
```

**Transform:**
```powershell
python scripts\transform_wide_to_long.py gps_data.xlsx --athlete-col "Player"
```

**Result:** Ready for `dados_gps` table

---

### 3. Match Reports

**Input columns:**
```
Jogador | Golos_J1 | Golos_J2 | Assists_J1 | Assists_J2 | Minutes_J1 | Minutes_J2
```

**Transform:**
```powershell
python scripts\transform_wide_to_long.py match_reports.xlsx --athlete-col "Jogador"
```

**Result:** Ready for custom match statistics table

---

## 🛠️ Advanced Customization

### Programmatic Usage

You can import and use the function in your own scripts:

```python
from transform_wide_to_long import wide_to_long
import pandas as pd

# Read your data
df = pd.read_excel('data.xlsx')

# Transform
df_long = wide_to_long(df, athlete_col='Nome')

# Further processing
df_long['Date'] = '2025-09-07'
df_long['Type'] = 'Training'

# Save or insert to database
df_long.to_csv('output.csv', index=False)
```

---

### Handling Complex Session Names

If your sessions have complex names with multiple underscores:

**Example:** `RPE_Training_Session_1`

The script will extract: `Session = Training_Session_1`

---

### Missing Values

The script preserves missing values (NaN) from the original data.

**Recommendations:**
- Review missing value report after transformation
- Decide whether to:
  - Keep as NULL in database
  - Fill with default values
  - Exclude incomplete records

---

## 📋 Best Practices

### 1. Consistent Column Naming

✅ **Good:**
```
RPE_T1, RPE_T2, RPE_T3
DOMS_T1, DOMS_T2, DOMS_T3
Distance_T1, Distance_T2, Distance_T3
```

❌ **Bad:**
```
RPE_T1, RPETraining2, T3_RPE  # Inconsistent patterns
```

---

### 2. Athlete Name Consistency

Ensure athlete names match your database exactly:
- Use consistent capitalization
- Avoid typos
- Use same format as `atletas.nome_completo`

**Tip:** Review the unique athletes list after transformation.

---

### 3. Session Identifier Mapping

After transformation, you'll need to map session identifiers to database session IDs:

```python
SESSION_MAPPING = {
    'T1': 1,  # sessao_id from sessoes table
    'T2': 2,
    'Jogo1': 10,
    'Jogo2': 11,
}
```

---

### 4. Data Validation

Always review the script output:
- ✅ Check unique athlete count matches expectations
- ✅ Verify session count is correct
- ✅ Review missing value percentages
- ✅ Inspect preview to ensure metrics extracted correctly

---

## 🔍 Troubleshooting

### "Could not identify athlete column"

**Solution:** Specify with `--athlete-col` parameter:
```powershell
python scripts\transform_wide_to_long.py data.xlsx --athlete-col "Jogador"
```

---

### "No session columns found"

**Cause:** Column naming doesn't match expected pattern (`METRIC_SESSION`)

**Solution:** 
1. Check your column names
2. Ensure they follow `METRIC_SESSION` pattern with underscore
3. Example: `RPE_T1` not `RPE-T1` or `RPET1`

---

### Metric Names Not Recognized

**Issue:** Columns like `RPE_T1` and `RPE_Training_1` create different metrics

**Solution:** Standardize your column naming before transformation

---

### Memory Issues with Large Files

For very large Excel files (>100 MB):

```python
# Read in chunks (custom script)
chunk_size = 1000
for chunk in pd.read_excel('large_file.xlsx', chunksize=chunk_size):
    df_long = wide_to_long(chunk)
    # Process chunk...
```

---

## 📚 Related Documentation

- **Main Guide:** `PROJECT_MASTER_GUIDE.md`
- **Database Schema:** `sql/01_criar_schema.sql`
- **Import Scripts:** 
  - `scripts/insert_catapult_data.py` (GPS data)
  - `scripts/insert_pse_data.py` (PSE data)

---

## 🎓 Tidy Data Principles

This transformation follows Hadley Wickham's "Tidy Data" principles:

1. ✅ Each variable forms a column (RPE, DOMS, Distance)
2. ✅ Each observation forms a row (1 athlete × 1 session)
3. ✅ Each type of observational unit forms a table (performance metrics)

**Reference:** Wickham, H. (2014). Tidy Data. Journal of Statistical Software, 59(10).

---

## 📊 Summary

| Aspect | Wide Format | Long Format |
|--------|-------------|-------------|
| **Rows** | 1 per athlete | 1 per athlete × session |
| **Columns** | Many (1 per metric × session) | Few (1 per metric) |
| **Excel viewing** | ✅ Easy | ❌ Harder |
| **Database storage** | ❌ Terrible | ✅ Ideal |
| **Queries** | ❌ Impossible | ✅ Easy |
| **Joins** | ❌ Can't | ✅ Yes |
| **Analytics** | ❌ Difficult | ✅ Simple |

**Verdict:** Always use long format for databases! 🎯

---

**Last Updated:** December 20, 2025  
**Script Version:** 1.0  
**Author:** Cascade AI Assistant
