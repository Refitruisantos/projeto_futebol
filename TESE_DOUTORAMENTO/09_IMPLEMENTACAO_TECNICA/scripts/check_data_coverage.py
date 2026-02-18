"""Check PSE data coverage vs calculated metrics"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from importlib.machinery import SourceFileLoader
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()

db = db_module.DatabaseConnection()

# Check PSE data range
pse_query = """
    SELECT 
        MIN(DATE(time)) as first_date,
        MAX(DATE(time)) as last_date,
        COUNT(DISTINCT DATE(time)) as total_days,
        COUNT(*) as total_records,
        COUNT(DISTINCT atleta_id) as total_athletes
    FROM dados_pse
    WHERE pse IS NOT NULL AND pse > 0
"""
pse_data = db.query_to_dict(pse_query)[0]

# Check calculated metrics range
metrics_query = """
    SELECT 
        MIN(semana_inicio) as first_week,
        MAX(semana_inicio) as last_week,
        COUNT(DISTINCT semana_inicio) as total_weeks,
        COUNT(*) as total_records
    FROM metricas_carga
"""
metrics_data = db.query_to_dict(metrics_query)[0]

# Calculate weeks
first_date = pse_data['first_date']
last_date = pse_data['last_date']
days_span = (last_date - first_date).days
weeks_available = days_span // 7

print("=" * 80)
print("DATA COVERAGE ANALYSIS")
print("=" * 80)
print()
print("📊 PSE RAW DATA:")
print(f"   First session: {pse_data['first_date']}")
print(f"   Last session: {pse_data['last_date']}")
print(f"   Time span: {days_span} days ({weeks_available} weeks)")
print(f"   Total training days: {pse_data['total_days']}")
print(f"   Total PSE records: {pse_data['total_records']}")
print(f"   Athletes tracked: {pse_data['total_athletes']}")
print()
print("📈 CALCULATED METRICS:")
print(f"   First week: {metrics_data['first_week']}")
print(f"   Last week: {metrics_data['last_week']}")
print(f"   Total weeks calculated: {metrics_data['total_weeks']}")
print(f"   Total athlete-weeks: {metrics_data['total_records']}")
print()

# Calculate remaining
if metrics_data['last_week']:
    days_remaining = (last_date - metrics_data['last_week']).days
    weeks_remaining = days_remaining // 7
    
    print("⏳ REMAINING DATA:")
    print(f"   Latest calculated week: {metrics_data['last_week']}")
    print(f"   Latest PSE data: {last_date}")
    print(f"   Days not yet calculated: {days_remaining}")
    print(f"   Weeks remaining: {weeks_remaining}")
    print()
    
    if weeks_remaining > 0:
        print(f"✅ You can calculate {weeks_remaining} more week(s) of metrics!")
        print(f"   Run: python scripts/calculate_weekly_metrics.py")
    else:
        print("✅ All available data has been calculated!")
else:
    print("⚠️ No metrics calculated yet!")

print("=" * 80)

db.close()
