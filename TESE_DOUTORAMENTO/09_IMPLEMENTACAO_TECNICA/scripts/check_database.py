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
print("DATABASE STATUS CHECK")
print("=" * 70)

# Check athletes
athletes = db.query_to_dict("SELECT COUNT(*) as count FROM atletas")
print(f"\n✅ Athletes in database: {athletes[0]['count']}")

athlete_list = db.query_to_dict("SELECT id, nome_completo, posicao FROM atletas ORDER BY id LIMIT 10")
print("\nFirst 10 athletes:")
for a in athlete_list:
    print(f"  - ID {a['id']}: {a['nome_completo']} ({a['posicao']})")

# Check sessions
sessions = db.query_to_dict("SELECT COUNT(*) as count FROM sessoes")
print(f"\n✅ Sessions in database: {sessions[0]['count']}")

session_list = db.query_to_dict("SELECT id, data, tipo, jornada FROM sessoes ORDER BY data")
print("\nAll sessions:")
for s in session_list:
    print(f"  - ID {s['id']}: {s['data']} (Jornada {s['jornada']}, {s['tipo']})")

# Check GPS data
gps = db.query_to_dict("SELECT COUNT(*) as count FROM dados_gps")
print(f"\n✅ GPS records in database: {gps[0]['count']}")

# Check GPS data per session
gps_per_session = db.query_to_dict("""
    SELECT s.jornada, COUNT(g.atleta_id) as player_count
    FROM sessoes s
    LEFT JOIN dados_gps g ON s.id = g.sessao_id
    WHERE s.tipo = 'jogo'
    GROUP BY s.id, s.jornada
    ORDER BY s.jornada
""")
print("\nGPS records per jornada:")
for g in gps_per_session:
    print(f"  - Jornada {g['jornada']}: {g['player_count']} players")

# Check if dashboard view exists and works
try:
    dashboard = db.query_to_dict("SELECT COUNT(*) as count FROM dashboard_principal")
    print(f"\n✅ Dashboard view works: {dashboard[0]['count']} records")
    
    dash_preview = db.query_to_dict("SELECT atleta_id, nome, distancia_total_media FROM dashboard_principal LIMIT 5")
    print("\nDashboard preview (first 5):")
    for d in dash_preview:
        print(f"  - {d['nome']}: {d['distancia_total_media']}m avg")
except Exception as e:
    print(f"\n❌ Dashboard view error: {e}")

# Check API endpoints data
try:
    athletes_api = db.query_to_dict("SELECT id, nome_completo FROM atletas LIMIT 1")
    print(f"\n✅ Athletes API data available: {len(athletes_api)} sample")
except Exception as e:
    print(f"\n❌ Athletes API error: {e}")

db.close()

print("\n" + "=" * 70)
print("CHECK COMPLETE")
print("=" * 70)
