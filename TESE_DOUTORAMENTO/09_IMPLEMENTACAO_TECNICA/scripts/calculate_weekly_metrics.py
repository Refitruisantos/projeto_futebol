"""
Calculate and populate weekly training load metrics
Processes existing PSE data to generate advanced metrics
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'utils'))

from importlib.machinery import SourceFileLoader
db_module = SourceFileLoader('conexao_db', 'python/01_conexao_db.py').load_module()

try:
    from metrics_calculator import MetricsCalculator, calcular_metricas_semana
except ImportError:
    print("❌ Could not import metrics_calculator. Make sure backend/utils/metrics_calculator.py exists")
    sys.exit(1)


def get_week_boundaries(date):
    """Get Monday (start) and Sunday (end) of the week containing the date"""
    # Get Monday of the week (weekday() returns 0 for Monday)
    days_since_monday = date.weekday()
    week_start = date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def main():
    db = db_module.DatabaseConnection()
    calc = MetricsCalculator()
    
    print("=" * 80)
    print("CALCULATE WEEKLY TRAINING LOAD METRICS")
    print("=" * 80)
    
    # Step 1: Get all athletes
    print("\n📋 Step 1: Loading athletes...")
    athletes = db.query_to_dict("SELECT id, nome_completo, posicao FROM atletas ORDER BY nome_completo")
    print(f"   Found {len(athletes)} athletes")
    
    # Step 2: Get all PSE data with session info
    print("\n📊 Step 2: Loading PSE data...")
    pse_data = db.query_to_dict("""
        SELECT 
            p.atleta_id,
            DATE(p.time) as data,
            p.pse,
            p.duracao_min,
            (p.pse * p.duracao_min) as carga_total,
            s.tipo as tipo_sessao
        FROM dados_pse p
        JOIN sessoes s ON s.id = p.sessao_id
        WHERE p.pse IS NOT NULL AND p.pse > 0
          AND p.duracao_min IS NOT NULL AND p.duracao_min > 0
        ORDER BY p.atleta_id, p.time
    """)
    print(f"   Found {len(pse_data)} PSE records")
    
    # Step 3: Group by athlete and week
    print("\n🗂️  Step 3: Organizing data by athlete and week...")
    athlete_weeks = defaultdict(lambda: defaultdict(list))
    
    for record in pse_data:
        atleta_id = record['atleta_id']
        data = record['data']
        carga = record['carga_total']
        
        week_start, week_end = get_week_boundaries(data)
        week_key = week_start.strftime('%Y-%m-%d')
        
        athlete_weeks[atleta_id][week_key].append({
            'data': data,
            'carga_total': carga
        })
    
    print(f"   Organized into {sum(len(weeks) for weeks in athlete_weeks.values())} athlete-weeks")
    
    # Step 4: Calculate metrics for each athlete-week
    print("\n🧮 Step 4: Calculating metrics...")
    print("-" * 80)
    
    metrics_calculated = 0
    metrics_inserted = 0
    
    # Clear existing metrics
    db.execute_query("DELETE FROM metricas_carga")
    print("   Cleared existing metrics\n")
    
    for atleta_id, weeks_data in athlete_weeks.items():
        athlete = next(a for a in athletes if a['id'] == atleta_id)
        athlete_name = athlete['nome_completo']
        
        print(f"👤 {athlete_name} ({len(weeks_data)} weeks)")
        
        # Sort weeks chronologically
        sorted_weeks = sorted(weeks_data.items())
        
        # Keep track of all weekly loads for ACWR calculation
        all_weekly_loads = []
        
        # Build chronological list of ALL workouts for rolling 7-workout monotony
        all_workouts_chronological = []
        for week_str, records in sorted_weeks:
            for record in sorted(records, key=lambda x: x['data']):
                all_workouts_chronological.append({
                    'data': record['data'],
                    'carga_total': record['carga_total']
                })
        
        for week_start_str, daily_records in sorted_weeks:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
            week_end = week_start + timedelta(days=6)
            
            # Extract daily loads for this week
            daily_loads = [r['carga_total'] for r in daily_records]
            carga_total = sum(daily_loads)
            all_weekly_loads.append({'data': week_start, 'carga_total': carga_total})
            
            # Get last 7 workouts up to and including this week (for monotony)
            workouts_up_to_week = [w for w in all_workouts_chronological if w['data'] <= week_end]
            last_7_workouts = workouts_up_to_week[-7:] if len(workouts_up_to_week) >= 7 else workouts_up_to_week
            workout_loads_for_monotony = [w['carga_total'] for w in last_7_workouts]
            
            # Calculate ACWR (need at least 28 days of history)
            carga_aguda = calc.calcular_carga_rolante(
                all_weekly_loads, 7, week_end
            )
            carga_cronica = calc.calcular_carga_rolante(
                all_weekly_loads, 28, week_end
            )
            
            # Get previous week load for variation %
            carga_semana_anterior = None
            if len(all_weekly_loads) >= 2:
                carga_semana_anterior = all_weekly_loads[-2]['carga_total']
            
            # Calculate all metrics (using rolling 7-workout loads for monotony)
            metricas = calcular_metricas_semana(
                workout_loads_for_monotony,  # Changed: now passes last 7 workouts instead of daily loads
                carga_total,
                carga_aguda,
                carga_cronica,
                carga_semana_anterior
            )
            
            metrics_calculated += 1
            
            # Insert into database
            try:
                db.execute_query("""
                    INSERT INTO metricas_carga (
                        atleta_id, semana_inicio, semana_fim,
                        carga_total_semanal, media_carga, desvio_padrao, dias_treino,
                        monotonia, tensao, variacao_percentual,
                        carga_aguda, carga_cronica, acwr,
                        nivel_risco_monotonia, nivel_risco_tensao, nivel_risco_acwr
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    atleta_id, week_start, week_end,
                    metricas['carga_total_semanal'],
                    metricas['media_carga'],
                    metricas['desvio_padrao'],
                    metricas['dias_treino'],
                    metricas['monotonia'],
                    metricas['tensao'],
                    metricas['variacao_percentual'],
                    metricas['carga_aguda'],
                    metricas['carga_cronica'],
                    metricas['acwr'],
                    metricas['nivel_risco_monotonia'],
                    metricas['nivel_risco_tensao'],
                    metricas['nivel_risco_acwr']
                ))
                metrics_inserted += 1
                
                # Show key metrics
                print(f"   Week {week_start}: Load={carga_total:.0f}, "
                      f"Monotony={metricas['monotonia']:.2f if metricas['monotonia'] else 'N/A'}, "
                      f"ACWR={metricas['acwr']:.2f if metricas['acwr'] else 'N/A'}")
                
            except Exception as e:
                print(f"   ❌ Error inserting week {week_start}: {e}")
        
        print()  # Blank line between athletes
    
    # Step 5: Calculate Z-scores (standardized scores relative to team)
    print("📊 Step 5: Calculating Z-scores...")
    print("-" * 80)
    
    # Get all metrics for each week to calculate team averages
    weeks = db.query_to_dict("""
        SELECT DISTINCT semana_inicio 
        FROM metricas_carga 
        ORDER BY semana_inicio
    """)
    
    for week_record in weeks:
        semana = week_record['semana_inicio']
        
        # Get all metrics for this week
        week_metrics = db.query_to_dict("""
            SELECT 
                id, atleta_id,
                carga_total_semanal, monotonia, tensao, acwr
            FROM metricas_carga
            WHERE semana_inicio = %s
        """, (semana,))
        
        if not week_metrics:
            continue
        
        # Calculate team averages and std devs
        cargas = [m['carga_total_semanal'] for m in week_metrics if m['carga_total_semanal']]
        monotonias = [m['monotonia'] for m in week_metrics if m['monotonia']]
        tensoes = [m['tensao'] for m in week_metrics if m['tensao']]
        acwrs = [m['acwr'] for m in week_metrics if m['acwr']]
        
        media_carga, desvio_carga = calc.calcular_media_desvio(cargas)
        media_monotonia, desvio_monotonia = calc.calcular_media_desvio(monotonias)
        media_tensao, desvio_tensao = calc.calcular_media_desvio(tensoes)
        media_acwr, desvio_acwr = calc.calcular_media_desvio(acwrs)
        
        # Update Z-scores for each athlete
        for metric in week_metrics:
            z_carga = calc.calcular_z_score(
                metric['carga_total_semanal'], media_carga, desvio_carga
            ) if media_carga and desvio_carga else None
            
            z_monotonia = calc.calcular_z_score(
                metric['monotonia'], media_monotonia, desvio_monotonia
            ) if metric['monotonia'] and media_monotonia and desvio_monotonia else None
            
            z_tensao = calc.calcular_z_score(
                metric['tensao'], media_tensao, desvio_tensao
            ) if metric['tensao'] and media_tensao and desvio_tensao else None
            
            z_acwr = calc.calcular_z_score(
                metric['acwr'], media_acwr, desvio_acwr
            ) if metric['acwr'] and media_acwr and desvio_acwr else None
            
            db.execute_query("""
                UPDATE metricas_carga
                SET z_score_carga = %s,
                    z_score_monotonia = %s,
                    z_score_tensao = %s,
                    z_score_acwr = %s
                WHERE id = %s
            """, (z_carga, z_monotonia, z_tensao, z_acwr, metric['id']))
        
        print(f"   Week {semana}: Updated Z-scores for {len(week_metrics)} athletes")
    
    # Step 6: Verification
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    total_metrics = db.query_to_dict("SELECT COUNT(*) as count FROM metricas_carga")[0]['count']
    print(f"\n✅ Total metrics calculated: {metrics_calculated}")
    print(f"✅ Total metrics inserted: {metrics_inserted}")
    print(f"✅ Total metrics in database: {total_metrics}")
    
    # Show risk distribution
    risk_summary = db.query_to_dict("""
        SELECT 
            nivel_risco_monotonia,
            COUNT(*) as count
        FROM metricas_carga
        WHERE nivel_risco_monotonia IS NOT NULL
        GROUP BY nivel_risco_monotonia
        ORDER BY 
            CASE nivel_risco_monotonia 
                WHEN 'green' THEN 1
                WHEN 'yellow' THEN 2
                WHEN 'red' THEN 3
            END
    """)
    
    print("\n📊 Monotony Risk Distribution:")
    for risk in risk_summary:
        icon = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}.get(risk['nivel_risco_monotonia'], '⚪')
        print(f"   {icon} {risk['nivel_risco_monotonia'].upper()}: {risk['count']} athlete-weeks")
    
    # Show sample metrics
    print("\n📋 Sample Metrics (Most Recent Week):")
    samples = db.query_to_dict("""
        SELECT 
            a.nome_completo,
            a.posicao,
            mc.semana_inicio,
            mc.carga_total_semanal,
            mc.monotonia,
            mc.tensao,
            mc.acwr,
            mc.nivel_risco_monotonia,
            mc.nivel_risco_tensao,
            mc.nivel_risco_acwr
        FROM metricas_carga mc
        JOIN atletas a ON a.id = mc.atleta_id
        ORDER BY mc.semana_inicio DESC, a.nome_completo
        LIMIT 5
    """)
    
    for s in samples:
        monotony_str = f"{s['monotonia']:.2f}" if s['monotonia'] else 'N/A'
        strain_str = f"{s['tensao']:.0f}" if s['tensao'] else 'N/A'
        acwr_str = f"{s['acwr']:.2f}" if s['acwr'] else 'N/A'
        
        print(f"\n   {s['nome_completo']} ({s['posicao']}) - Week {s['semana_inicio']}")
        print(f"      Load: {s['carga_total_semanal']:.0f}")
        print(f"      Monotony: {monotony_str} ({s['nivel_risco_monotonia']})")
        print(f"      Strain: {strain_str} ({s['nivel_risco_tensao']})")
        print(f"      ACWR: {acwr_str} ({s['nivel_risco_acwr']})")
    
    print("\n" + "=" * 80)
    print("✅ METRICS CALCULATION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Backend API endpoints will serve these metrics")
    print("  2. Frontend will visualize with color-coded risk zones")
    print("  3. Position and team averages will be calculated on demand")
    print("=" * 80)


if __name__ == '__main__':
    main()
