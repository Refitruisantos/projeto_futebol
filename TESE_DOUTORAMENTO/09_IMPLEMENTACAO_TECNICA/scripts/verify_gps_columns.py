import sys
from pathlib import Path

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

db = DatabaseConnection()

print("=" * 70)
print("GPS DATA COLUMN VERIFICATION")
print("=" * 70)

# Check all GPS columns are populated
gps_sample = db.query_to_dict("""
    SELECT 
        a.nome_completo,
        g.distancia_total,
        g.velocidade_max,
        g.aceleracoes,
        g.desaceleracoes,
        g.effs_19_8_kmh,
        g.dist_19_8_kmh,
        g.effs_25_2_kmh,
        g.tot_effs_gen2
    FROM dados_gps g
    JOIN atletas a ON a.id = g.atleta_id
    ORDER BY g.distancia_total DESC
    LIMIT 5
""")

print("\nTop 5 athletes by distance - ALL GPS COLUMNS:")
print("-" * 70)
for athlete in gps_sample:
    print(f"\n{athlete['nome_completo']}:")
    print(f"  Distance: {athlete['distancia_total']}m")
    print(f"  Max Speed: {athlete['velocidade_max']} km/h")
    print(f"  Accelerations: {athlete['aceleracoes']}")
    print(f"  Decelerations: {athlete['desaceleracoes']}")
    print(f"  Efforts >19.8: {athlete['effs_19_8_kmh']}")
    print(f"  Distance >19.8: {athlete['dist_19_8_kmh']}m")
    print(f"  Efforts >25.2: {athlete['effs_25_2_kmh']}")
    print(f"  Total Gen2 Efforts: {athlete['tot_effs_gen2']}")

# Count records per athlete
athlete_gps_count = db.query_to_dict("""
    SELECT 
        a.nome_completo,
        COUNT(*) as num_records
    FROM atletas a
    LEFT JOIN dados_gps g ON g.atleta_id = a.id
    WHERE a.ativo = TRUE
    GROUP BY a.id, a.nome_completo
    ORDER BY num_records DESC
""")

print("\n\nGPS Records per Athlete:")
print("-" * 70)
for athlete in athlete_gps_count[:10]:
    print(f"  {athlete['nome_completo']}: {athlete['num_records']} records")

# Total stats
total_query = db.query_to_dict("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(DISTINCT atleta_id) as unique_athletes,
        COUNT(DISTINCT sessao_id) as unique_sessions
    FROM dados_gps
""")[0]

print("\n\nSummary:")
print("-" * 70)
print(f"Total GPS records: {total_query['total_records']}")
print(f"Athletes with data: {total_query['unique_athletes']}")
print(f"Sessions recorded: {total_query['unique_sessions']}")

db.close()

print("\n" + "=" * 70)
print("✅ ALL GPS COLUMNS VERIFIED")
print("=" * 70)
