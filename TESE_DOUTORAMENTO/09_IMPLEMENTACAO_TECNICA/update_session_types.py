import sys
import pandas as pd
sys.path.insert(0, 'python')
from importlib.machinery import SourceFileLoader

# Load database module
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()
db = db_module.DatabaseConnection()

print("=" * 80)
print("UPDATING SESSION TYPES: Training vs Games")
print("=" * 80)
print("\nRule: Sessions 1-5 = treino, Session 6 = jogo")

# Load the CSV to map session numbers
csv_path = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadosPSE\ALL_PSE_LONG_cleaned.csv"
df = pd.read_csv(csv_path)

# Get unique combinations of Jornada and Session to map to database sessions
session_mapping = df[['Jornada', 'Session']].drop_duplicates().sort_values(['Jornada', 'Session'])

print(f"\nFound {len(session_mapping)} unique jornada-session combinations in CSV")

# For each session in database, find its session number from PSE data
sessions = db.query_to_dict("""
    SELECT DISTINCT s.id, s.data, s.tipo, s.jornada
    FROM sessoes s
    ORDER BY s.jornada, s.data
""")

print(f"\nCurrent database sessions: {len(sessions)}")
print("\n" + "-" * 80)
print("Session Analysis:")
print("-" * 80)

updates_needed = []

for s in sessions:
    # Get PSE data for this session to find the session number
    pse_data = db.query_to_dict("""
        SELECT atleta_id, sessao_id, time
        FROM dados_pse 
        WHERE sessao_id = %s
        LIMIT 1
    """, (s['id'],))
    
    if pse_data:
        # Match to CSV to find session number
        session_date = pse_data[0]['time'].date()
        jornada = s['jornada']
        
        # Find matching session in CSV by jornada and approximate date
        csv_matches = df[df['Jornada'] == jornada]
        
        if len(csv_matches) > 0:
            # Sessions within same jornada - determine session number
            # Count how many sessions exist for this jornada up to this session
            earlier_sessions = db.query_to_dict("""
                SELECT COUNT(*) as count
                FROM sessoes
                WHERE jornada = %s AND data <= %s
            """, (jornada, s['data']))[0]['count']
            
            session_num = earlier_sessions
            
            # Determine correct type
            correct_type = 'jogo' if session_num >= 6 else 'treino'
            current_type = s['tipo']
            
            status = "✅" if current_type == correct_type else "❌"
            
            print(f"{status} Session {s['id']:2d} | Jornada {jornada} #{session_num} | "
                  f"{s['data']} | Current: {current_type:6s} → Should be: {correct_type:6s}")
            
            if current_type != correct_type:
                updates_needed.append({
                    'id': s['id'],
                    'current': current_type,
                    'new': correct_type,
                    'jornada': jornada,
                    'session_num': session_num
                })

print("\n" + "=" * 80)
print(f"SUMMARY: {len(updates_needed)} sessions need updating")
print("=" * 80)

if updates_needed:
    print("\nUpdates to apply:")
    for u in updates_needed:
        print(f"  Session {u['id']:2d} (Jornada {u['jornada']} #{u['session_num']}): "
              f"{u['current']} → {u['new']}")
    
    print("\n" + "=" * 80)
    print("Applying updates...")
    print("=" * 80)
    
    for u in updates_needed:
        db.execute_query(
            "UPDATE sessoes SET tipo = %s WHERE id = %s",
            (u['new'], u['id'])
        )
        print(f"  ✅ Updated session {u['id']} to '{u['new']}'")
    
    print(f"\n✅ Successfully updated {len(updates_needed)} sessions!")
else:
    print("\n✅ All sessions already have correct types!")

# Verify final state
print("\n" + "=" * 80)
print("FINAL VERIFICATION")
print("=" * 80)

final_sessions = db.query_to_dict("""
    SELECT tipo, COUNT(*) as count
    FROM sessoes
    GROUP BY tipo
    ORDER BY tipo
""")

print("\nSession breakdown:")
for row in final_sessions:
    print(f"  {row['tipo']}: {row['count']} sessions")

print("\n" + "=" * 80)
print("✅ DONE! Refresh your browser to see training vs games.")
print("=" * 80)
