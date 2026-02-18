"""
Debug script to show detailed monotony calculations
Shows actual workout data and rolling 7-workout window for verification
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'utils'))

from importlib.machinery import SourceFileLoader
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()

from metrics_calculator import MetricsCalculator

db = db_module.DatabaseConnection()
calc = MetricsCalculator()

print("=" * 100)
print("MONOTONY CALCULATION DEBUG - Rolling 7-Workout Window Verification")
print("=" * 100)
print()

# Get the most recent week
most_recent_week_query = """
    SELECT DISTINCT semana_inicio 
    FROM metricas_carga 
    ORDER BY semana_inicio DESC 
    LIMIT 1
"""
most_recent = db.query_to_dict(most_recent_week_query)[0]['semana_inicio']
week_end = most_recent + timedelta(days=6)

print(f"📅 Analyzing Most Recent Week: {most_recent} to {week_end}")
print()

# Get athletes from that week
athletes_in_week = db.query_to_dict(f"""
    SELECT 
        mc.atleta_id,
        a.nome_completo,
        a.posicao,
        mc.monotonia,
        mc.nivel_risco_monotonia,
        mc.dias_treino
    FROM metricas_carga mc
    JOIN atletas a ON a.id = mc.atleta_id
    WHERE mc.semana_inicio = '{most_recent}'
    ORDER BY mc.monotonia DESC
    LIMIT 5
""")

# Count athletes in this week
count_query = f"SELECT COUNT(*) as c FROM metricas_carga WHERE semana_inicio = '{most_recent}'"
total_in_week = db.query_to_dict(count_query)[0]['c']
print(f"🏃 Athletes in this week: {total_in_week}")
print()
print("=" * 100)
print("TOP 5 ATHLETES BY MONOTONY (Showing Detailed Calculation)")
print("=" * 100)
print()

for athlete in athletes_in_week:
    athlete_id = athlete['atleta_id']
    athlete_name = athlete['nome_completo']
    position = athlete['posicao']
    calculated_monotony = athlete['monotonia']
    risk_level = athlete['nivel_risco_monotonia']
    
    print(f"\n{'='*100}")
    print(f"👤 {athlete_name} ({position}) - Calculated Monotony: {calculated_monotony:.2f} ({risk_level.upper()})")
    print(f"{'='*100}")
    
    # Get ALL workouts for this athlete up to and including the week
    all_workouts = db.query_to_dict(f"""
        SELECT 
            DATE(p.time) as data,
            (p.pse * p.duracao_min) as carga_total,
            p.pse,
            p.duracao_min
        FROM dados_pse p
        JOIN sessoes s ON s.id = p.sessao_id
        WHERE p.atleta_id = {athlete_id}
          AND DATE(p.time) <= '{week_end}'
          AND p.pse IS NOT NULL AND p.pse > 0
          AND p.duracao_min IS NOT NULL AND p.duracao_min > 0
        ORDER BY p.time
    """)
    
    print(f"\n📊 Total workouts up to {week_end}: {len(all_workouts)}")
    
    if len(all_workouts) < 7:
        print(f"   ⚠️  Only {len(all_workouts)} workouts available (need 7 for full calculation)")
    
    # Get last 7 workouts
    last_7 = all_workouts[-7:] if len(all_workouts) >= 7 else all_workouts
    workout_loads = [w['carga_total'] for w in last_7]
    
    print(f"\n🔄 ROLLING 7-WORKOUT WINDOW:")
    print(f"   Using last {len(last_7)} workout(s) for monotony calculation")
    print()
    
    for i, workout in enumerate(last_7, 1):
        date = workout['data']
        load = workout['carga_total']
        pse = workout['pse']
        duration = workout['duracao_min']
        
        # Check if this workout is in the current week
        in_current_week = most_recent <= date <= week_end
        week_marker = " ← THIS WEEK" if in_current_week else " (previous week)"
        
        print(f"   Workout {i}: {date.strftime('%Y-%m-%d (%a)')} - "
              f"Load={load:6.0f} (PSE={pse} × {duration}min){week_marker}")
    
    # Manual calculation
    if len(workout_loads) >= 2:
        import statistics
        mean = statistics.mean(workout_loads)
        stdev = statistics.stdev(workout_loads)
        manual_monotony = mean / stdev if stdev > 0 else None
        
        print()
        print(f"   📈 CALCULATION:")
        print(f"      Loads: {[round(l, 0) for l in workout_loads]}")
        print(f"      Mean:  {mean:.2f}")
        print(f"      StDev: {stdev:.2f}")
        print(f"      Monotony = Mean / StDev = {mean:.2f} / {stdev:.2f} = {manual_monotony:.2f}")
        print()
        print(f"   ✓ Database value: {calculated_monotony:.2f}")
        print(f"   ✓ Manual calculation: {manual_monotony:.2f}")
        
        if abs(float(calculated_monotony) - manual_monotony) < 0.01:
            print(f"   ✅ VERIFIED - Calculation matches!")
        else:
            print(f"   ❌ MISMATCH - Database and manual calculation differ!")
    
    # Get this week's workouts specifically
    this_week_workouts = [w for w in last_7 if most_recent <= w['data'] <= week_end]
    print()
    print(f"   📅 Workouts in current week ({most_recent}): {len(this_week_workouts)}")
    print(f"   📅 Workouts from previous weeks: {len(last_7) - len(this_week_workouts)}")

print()
print("=" * 100)
print("WHY ONLY 17 ATHLETES?")
print("=" * 100)
print()

# Count athletes per week
weekly_counts = db.query_to_dict("""
    SELECT 
        semana_inicio,
        COUNT(*) as athlete_count
    FROM metricas_carga
    GROUP BY semana_inicio
    ORDER BY semana_inicio DESC
""")

print("Athletes training per week:")
for week_data in weekly_counts:
    week = week_data['semana_inicio']
    count = week_data['athlete_count']
    marker = " ← Most recent (displayed in frontend)" if week == most_recent else ""
    print(f"   Week {week}: {count} athletes{marker}")

print()
print("💡 The frontend shows the MOST RECENT WEEK only.")
print("   Only athletes who trained during that specific week appear.")
print("   Different athletes may have been active in other weeks.")

# Show total unique athletes
total_athletes = db.query_to_dict("""
    SELECT COUNT(DISTINCT atleta_id) as total
    FROM metricas_carga
""")[0]['total']

print()
print(f"📊 Total unique athletes across all 6 weeks: {total_athletes}")
print(f"📊 Athletes in most recent week: {len(athletes_in_week)} (only this week is displayed)")

print()
print("=" * 100)

db.close()
