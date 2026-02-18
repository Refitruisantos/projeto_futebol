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
print("PSE DATA VERIFICATION")
print("=" * 70)

# Check PSE records count
pse_count = db.query_to_dict("SELECT COUNT(*) as count FROM dados_pse")[0]
print(f"\n✅ Total PSE records: {pse_count['count']}")

# PSE records per athlete
athlete_pse = db.query_to_dict("""
    SELECT 
        a.nome_completo,
        COUNT(p.*) as num_records,
        ROUND(AVG(p.pse)::numeric, 2) as avg_rpe,
        ROUND(AVG(p.carga_total)::numeric, 2) as avg_load
    FROM atletas a
    INNER JOIN dados_pse p ON p.atleta_id = a.id
    GROUP BY a.id, a.nome_completo
    ORDER BY num_records DESC
    LIMIT 15
""")

print("\nTop 15 athletes by PSE records:")
print("-" * 70)
for athlete in athlete_pse:
    print(f"  {athlete['nome_completo']}: {athlete['num_records']} records | Avg RPE: {athlete['avg_rpe']} | Avg Load: {athlete['avg_load']}")

# Sample PSE data with wellness metrics
pse_sample = db.query_to_dict("""
    SELECT 
        a.nome_completo,
        p.time::date as date,
        p.pse,
        p.duracao_min,
        p.carga_total,
        p.qualidade_sono,
        p.stress,
        p.fadiga,
        p.dor_muscular
    FROM dados_pse p
    JOIN atletas a ON a.id = p.atleta_id
    ORDER BY p.carga_total DESC
    LIMIT 5
""")

print("\nTop 5 highest load sessions (with wellness data):")
print("-" * 70)
for record in pse_sample:
    print(f"\n{record['nome_completo']} ({record['date']}):")
    print(f"  RPE: {record['pse']} | Duration: {record['duracao_min']}min | Load: {record['carga_total']}")
    print(f"  Sleep: {record['qualidade_sono']} | Stress: {record['stress']} | Fatigue: {record['fadiga']} | DOMS: {record['dor_muscular']}")

# Check 7-day load calculation (manual query)
load_7d = db.query_to_dict("""
    SELECT 
        a.nome_completo,
        SUM(p.carga_total) as total_load_7d,
        COUNT(*) as sessions_7d,
        ROUND(AVG(p.carga_total)::numeric, 2) as avg_load_7d
    FROM atletas a
    INNER JOIN dados_pse p ON p.atleta_id = a.id
    WHERE p.time >= NOW() - INTERVAL '7 days'
    GROUP BY a.id, a.nome_completo
    ORDER BY total_load_7d DESC
    LIMIT 10
""")

print("\n\n7-Day Load Summary (Top 10):")
print("-" * 70)
for athlete in load_7d:
    print(f"  {athlete['nome_completo']}: {athlete['total_load_7d']} total | {athlete['sessions_7d']} sessions | {athlete['avg_load_7d']} avg")

# Check combined GPS + PSE data availability
combined = db.query_to_dict("""
    SELECT 
        a.nome_completo,
        COUNT(DISTINCT g.sessao_id) as gps_sessions,
        COUNT(DISTINCT p.sessao_id) as pse_sessions
    FROM atletas a
    LEFT JOIN dados_gps g ON g.atleta_id = a.id
    LEFT JOIN dados_pse p ON p.atleta_id = a.id
    WHERE a.ativo = TRUE
    GROUP BY a.id, a.nome_completo
    HAVING COUNT(DISTINCT g.sessao_id) > 0 OR COUNT(DISTINCT p.sessao_id) > 0
    ORDER BY (COUNT(DISTINCT g.sessao_id) + COUNT(DISTINCT p.sessao_id)) DESC
    LIMIT 10
""")

print("\n\nCombined GPS + PSE Data (Top 10):")
print("-" * 70)
for athlete in combined:
    print(f"  {athlete['nome_completo']}: {athlete['gps_sessions']} GPS | {athlete['pse_sessions']} PSE")

db.close()

print("\n" + "=" * 70)
print("✅ PSE DATA VERIFICATION COMPLETE")
print("=" * 70)
