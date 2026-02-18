"""
Analyze why risk metrics are showing so many athletes at risk
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from importlib.machinery import SourceFileLoader
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()

def main():
    db = db_module.DatabaseConnection()
    
    print("=" * 80)
    print("RISK METRICS ANALYSIS")
    print("=" * 80)
    
    # 1. Check PSE data coverage
    print("\n1️⃣  PSE Data Coverage (Top 10 Athletes)")
    print("-" * 80)
    
    pse_coverage = db.query_to_dict("""
        SELECT 
            a.nome_completo,
            COUNT(*) as total_sessions,
            MIN(DATE(p.time)) as first_session,
            MAX(DATE(p.time)) as last_session,
            COUNT(DISTINCT DATE(p.time)) as unique_days,
            ROUND(AVG(p.pse * p.duracao_min)::numeric, 0) as avg_load
        FROM dados_pse p
        JOIN atletas a ON a.id = p.atleta_id
        WHERE p.pse > 0 AND p.duracao_min > 0
        GROUP BY a.nome_completo
        ORDER BY total_sessions DESC
        LIMIT 10
    """)
    
    for r in pse_coverage:
        days_range = (r['last_session'] - r['first_session']).days
        print(f"{r['nome_completo']:20s} | {r['total_sessions']:3d} sessions | "
              f"{r['unique_days']:3d} days | Avg Load: {r['avg_load']:4.0f} | "
              f"Range: {days_range} days")
    
    # 2. Check most recent week metrics details
    print("\n2️⃣  Most Recent Week - Detailed Metrics")
    print("-" * 80)
    
    recent_metrics = db.query_to_dict("""
        SELECT 
            a.nome_completo,
            mc.semana_inicio,
            mc.carga_total_semanal,
            mc.dias_treino,
            mc.monotonia,
            mc.desvio_padrao,
            mc.media_carga,
            mc.tensao,
            mc.acwr,
            mc.carga_aguda,
            mc.carga_cronica,
            mc.nivel_risco_monotonia,
            mc.nivel_risco_tensao,
            mc.nivel_risco_acwr
        FROM metricas_carga mc
        JOIN atletas a ON a.id = mc.atleta_id
        WHERE mc.semana_inicio = (SELECT MAX(semana_inicio) FROM metricas_carga)
        ORDER BY mc.monotonia DESC
        LIMIT 10
    """)
    
    print(f"{'Athlete':<20} | {'Load':<6} | {'Days':<4} | {'Mean':<6} | {'StdDev':<6} | "
          f"{'Monotony':<8} | {'ACWR':<6} | Risks")
    print("-" * 80)
    
    for r in recent_metrics:
        risks = f"{r['nivel_risco_monotonia'][0]}{r['nivel_risco_tensao'][0]}{r['nivel_risco_acwr'][0]}"
        print(f"{r['nome_completo']:<20} | {r['carga_total_semanal']:>6.0f} | "
              f"{r['dias_treino']:>4} | {r['media_carga']:>6.0f} | "
              f"{r['desvio_padrao']:>6.0f} | {r['monotonia']:>8.2f} | "
              f"{r['acwr']:>6.2f} | {risks}")
    
    # 3. Examine actual daily loads for one athlete with high monotony
    print("\n3️⃣  Sample: Daily Loads for Athlete with High Monotony")
    print("-" * 80)
    
    high_monotony_athlete = recent_metrics[0] if recent_metrics else None
    
    if high_monotony_athlete:
        athlete_name = high_monotony_athlete['nome_completo']
        week_start = high_monotony_athlete['semana_inicio']
        
        # Get athlete_id
        athlete_id = db.query_to_dict(
            "SELECT id FROM atletas WHERE nome_completo = %s", 
            (athlete_name,)
        )[0]['id']
        
        daily_loads = db.query_to_dict("""
            SELECT 
                DATE(p.time) as data,
                p.pse,
                p.duracao_min,
                (p.pse * p.duracao_min) as carga_total
            FROM dados_pse p
            WHERE p.atleta_id = %s
              AND DATE(p.time) >= %s
              AND DATE(p.time) < %s + INTERVAL '7 days'
            ORDER BY p.time
        """, (athlete_id, week_start, week_start))
        
        print(f"\nAthlete: {athlete_name}")
        print(f"Week: {week_start}")
        print(f"Monotony: {high_monotony_athlete['monotonia']:.2f}")
        print(f"\nDaily Loads:")
        
        for d in daily_loads:
            print(f"  {d['data']} | PSE: {d['pse']:2.0f} | Duration: {d['duracao_min']:3.0f} min | "
                  f"Load: {d['carga_total']:5.0f}")
        
        if daily_loads:
            loads = [d['carga_total'] for d in daily_loads]
            import statistics
            mean = statistics.mean(loads)
            stdev = statistics.stdev(loads) if len(loads) > 1 else 0
            print(f"\n  Mean: {mean:.0f}")
            print(f"  Std Dev: {stdev:.0f}")
            print(f"  Monotony (mean/stdev): {mean/stdev:.2f}" if stdev > 0 else "  Monotony: N/A (zero variance)")
            print(f"\n  ⚠️  Low standard deviation = {stdev:.0f} means loads are very similar!")
            print(f"  ⚠️  This creates HIGH monotony = {mean/stdev:.2f} (risk threshold: >1.5)")
    
    # 4. Check ACWR distribution
    print("\n4️⃣  ACWR Analysis (Most Recent Week)")
    print("-" * 80)
    
    acwr_stats = db.query_to_dict("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN acwr < 0.8 THEN 1 END) as detraining,
            COUNT(CASE WHEN acwr >= 0.8 AND acwr <= 1.3 THEN 1 END) as optimal,
            COUNT(CASE WHEN acwr > 1.3 AND acwr <= 1.5 THEN 1 END) as elevated,
            COUNT(CASE WHEN acwr > 1.5 THEN 1 END) as overtraining,
            ROUND(AVG(acwr), 2) as avg_acwr,
            ROUND(AVG(carga_aguda), 0) as avg_acute,
            ROUND(AVG(carga_cronica), 0) as avg_chronic
        FROM metricas_carga
        WHERE semana_inicio = (SELECT MAX(semana_inicio) FROM metricas_carga)
          AND acwr IS NOT NULL
    """)[0]
    
    print(f"Total athletes: {acwr_stats['total']}")
    print(f"  🔴 Detraining (<0.8): {acwr_stats['detraining']} ({acwr_stats['detraining']/acwr_stats['total']*100:.1f}%)")
    print(f"  🟢 Optimal (0.8-1.3): {acwr_stats['optimal']} ({acwr_stats['optimal']/acwr_stats['total']*100:.1f}%)")
    print(f"  🟡 Elevated (1.3-1.5): {acwr_stats['elevated']} ({acwr_stats['elevated']/acwr_stats['total']*100:.1f}%)")
    print(f"  🔴 Overtraining (>1.5): {acwr_stats['overtraining']} ({acwr_stats['overtraining']/acwr_stats['total']*100:.1f}%)")
    print(f"\nAverage ACWR: {acwr_stats['avg_acwr']}")
    print(f"Average Acute Load (7d): {acwr_stats['avg_acute']}")
    print(f"Average Chronic Load (28d): {acwr_stats['avg_chronic']}")
    print(f"\n⚠️  If chronic > acute, this suggests recent load DROP (detraining)")
    
    # 5. Check if this is early in season (not enough history)
    print("\n5️⃣  Historical Data Availability")
    print("-" * 80)
    
    data_range = db.query_to_dict("""
        SELECT 
            MIN(DATE(time)) as first_pse,
            MAX(DATE(time)) as last_pse
        FROM dados_pse
        WHERE pse > 0
    """)[0]
    
    days_span = (data_range['last_pse'] - data_range['first_pse']).days
    print(f"PSE Data Range: {data_range['first_pse']} to {data_range['last_pse']}")
    print(f"Total Span: {days_span} days")
    print(f"\n⚠️  ACWR requires 28+ days of history for reliable chronic workload")
    print(f"⚠️  If data span < 28 days, ACWR will be unreliable")
    
    # 6. Summary and recommendations
    print("\n" + "=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    
    print("\n🔍 Key Findings:")
    print("  1. High monotony = Low variability in daily training loads")
    print("     → Athletes doing very similar workouts day-to-day")
    print("  2. Low ACWR = Chronic load > Acute load")
    print("     → Recent training volume has DECREASED compared to 28-day average")
    
    print("\n💡 Possible Explanations:")
    print("  1. Early season / insufficient historical data")
    print("  2. Off-season or taper period (intended load reduction)")
    print("  3. Injuries/absences reducing training participation")
    print("  4. Data collection issues (missing sessions)")
    print("  5. Training is genuinely too repetitive (needs variation)")
    
    print("\n✅ Recommendations:")
    print("  1. Verify PSE data completeness (all sessions recorded?)")
    print("  2. If early season: Wait for 28+ days of consistent data")
    print("  3. If mid-season: Review actual training variation")
    print("  4. Consider adjusting thresholds for your team's context")
    print("  5. Review risk levels with coaching staff (are they accurate?)")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
