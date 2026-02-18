import sys
import pandas as pd
sys.path.insert(0, 'python')
from importlib.machinery import SourceFileLoader

# Load database module
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()
db = db_module.DatabaseConnection()

print("=" * 80)
print("PSE DATA STRUCTURE CHECK")
print("=" * 80)

# Check table columns
cols = db.query_to_dict("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'dados_pse' 
    ORDER BY ordinal_position
""")

print("\ndados_pse table columns:")
for c in cols:
    print(f"  - {c['column_name']}")

# Sample some PSE data
print("\n" + "=" * 80)
print("SAMPLE PSE DATA (first 10 rows)")
print("=" * 80)

sample = db.query_to_dict("SELECT * FROM dados_pse LIMIT 10")
if sample:
    for i, row in enumerate(sample, 1):
        print(f"\nRow {i}:")
        for key, val in row.items():
            print(f"  {key}: {val}")

# Check the CSV file structure
print("\n" + "=" * 80)
print("CSV FILE STRUCTURE")
print("=" * 80)

csv_path = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadosPSE\ALL_PSE_LONG_cleaned.csv"
df = pd.read_csv(csv_path)

print(f"\nCSV Columns: {list(df.columns)}")
print(f"CSV Rows: {len(df)}")
print(f"\nUnique Session numbers: {sorted(df['Session'].unique())}")
print(f"Unique Jornadas: {sorted(df['Jornada'].unique())}")

print("\nSample CSV data:")
print(df.head(10).to_string())

print("\n" + "=" * 80)
