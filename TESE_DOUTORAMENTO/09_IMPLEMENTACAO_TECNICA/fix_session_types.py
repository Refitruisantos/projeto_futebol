import sys
sys.path.insert(0, 'python')
from importlib.machinery import SourceFileLoader

# Load database module
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()
db = db_module.DatabaseConnection()

print("=" * 80)
print("SESSION TYPE FIX PROPOSAL")
print("=" * 80)

# Get all sessions
sessions = db.query_to_dict("""
    SELECT s.id, s.data, s.tipo, s.jornada, s.duracao_min,
           COUNT(DISTINCT p.atleta_id) as pse_count
    FROM sessoes s
    LEFT JOIN dados_pse p ON p.sessao_id = s.id
    GROUP BY s.id, s.data, s.tipo, s.jornada, s.duracao_min
    ORDER BY s.jornada, s.data
""")

print(f"\nCurrent sessions: {len(sessions)}")
print("\nProposed changes:")
print("-" * 80)

# Mapping: session numbers 1-5 in each jornada should be training
for s in sessions:
    # Get all PSE records for this session to determine session number
    pse_records = db.query_to_dict("""
        SELECT DISTINCT sessao, jornada 
        FROM dados_pse 
        WHERE sessao_id = %s 
        LIMIT 1
    """, (s['id'],))
    
    if pse_records:
        session_num = pse_records[0]['sessao']
        jornada = pse_records[0]['jornada']
        
        # Sessions 1-5 = training, Session 6 = game
        proposed_type = 'treino' if session_num < 6 else 'jogo'
        current_type = s['tipo']
        
        status = "✅ OK" if current_type == proposed_type else "❌ NEEDS FIX"
        
        print(f"{status} | Session {s['id']:2d} | Jornada {jornada} Session #{session_num} | "
              f"Current: {current_type:6s} → Proposed: {proposed_type:6s} | "
              f"{s['data']} | {s['pse_count']} athletes")

print("\n" + "=" * 80)
print("APPLY FIXES?")
print("=" * 80)

response = input("\nDo you want to update session types? (yes/no): ").lower().strip()

if response in ['yes', 'y', 'sim', 's']:
    print("\nUpdating session types...")
    
    for s in sessions:
        pse_records = db.query_to_dict("""
            SELECT DISTINCT sessao, jornada 
            FROM dados_pse 
            WHERE sessao_id = %s 
            LIMIT 1
        """, (s['id'],))
        
        if pse_records:
            session_num = pse_records[0]['sessao']
            proposed_type = 'treino' if session_num < 6 else 'jogo'
            
            if s['tipo'] != proposed_type:
                db.execute_query(
                    "UPDATE sessoes SET tipo = %s WHERE id = %s",
                    (proposed_type, s['id'])
                )
                print(f"  ✅ Updated session {s['id']} to '{proposed_type}'")
    
    print("\n✅ Session types updated successfully!")
    print("\nRefresh your browser to see the changes.")
else:
    print("\n❌ No changes made.")

print("\n" + "=" * 80)
