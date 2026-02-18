import sys
sys.path.insert(0, 'python')
from importlib.machinery import SourceFileLoader

# Load database module
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()
db = db_module.DatabaseConnection()

# Get all sessions
print("=" * 80)
print("DATABASE SESSION VERIFICATION")
print("=" * 80)

sessions = db.query_to_dict("SELECT id, data, tipo, jornada, duracao_min FROM sessoes ORDER BY data, id")
print(f"\nTotal sessions in database: {len(sessions)}")

# Group by type
from collections import defaultdict
by_type = defaultdict(list)
for s in sessions:
    by_type[s['tipo']].append(s)

print("\n--- Sessions by Type ---")
for tipo, sess_list in sorted(by_type.items()):
    print(f"\n{tipo.upper()}: {len(sess_list)} sessions")
    for s in sess_list:
        print(f"  {s['id']:2d}. {s['data']} | Jornada {s['jornada']} | {s['duracao_min']}min")

# Check how many athletes have data for each session
print("\n" + "=" * 80)
print("ATHLETE PARTICIPATION PER SESSION")
print("=" * 80)

for s in sessions:
    gps_count = db.query_to_dict(
        "SELECT COUNT(DISTINCT atleta_id) as count FROM dados_gps WHERE sessao_id = %s",
        (s['id'],)
    )[0]['count']
    
    pse_count = db.query_to_dict(
        "SELECT COUNT(DISTINCT atleta_id) as count FROM dados_pse WHERE sessao_id = %s",
        (s['id'],)
    )[0]['count']
    
    print(f"Session {s['id']:2d} ({s['data']}, {s['tipo']:6s}): GPS={gps_count} athletes, PSE={pse_count} athletes")

# Check PSE source files
print("\n" + "=" * 80)
print("PSE SOURCE FILES")
print("=" * 80)

import os
pse_dir = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadosPSE"
if os.path.exists(pse_dir):
    pse_files = [f for f in os.listdir(pse_dir) if f.endswith('.csv')]
    print(f"\nFound {len(pse_files)} CSV files in PSE directory:")
    for f in sorted(pse_files):
        print(f"  - {f}")
else:
    print(f"PSE directory not found: {pse_dir}")

print("\n" + "=" * 80)
