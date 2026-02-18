#!/usr/bin/env python3
"""Completely fix the metrics.py file by rewriting the problematic function"""

import os

# Read the current metrics.py file
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire comprehensive profile function
old_function_start = '@router.get("/athletes/{athlete_id}/comprehensive-profile")'
old_function_end = 'def _generate_opponent_recommendations'

# Split content to find the function
lines = content.split('\n')
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if old_function_start in line:
        start_idx = i
    elif start_idx != -1 and old_function_end in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Replace the problematic function with a corrected version
    new_function = '''@router.get("/athletes/{athlete_id}/comprehensive-profile")
def get_comprehensive_athlete_profile(
    athlete_id: int,
    days: int = Query(30, le=365),
    db: DatabaseConnection = Depends(get_db)
):
    """Get comprehensive athlete profile combining all data sources"""
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Basic athlete info
        athlete_query = """
            SELECT 
                a.*,
                EXTRACT(YEAR FROM AGE(a.data_nascimento)) as idade
            FROM atletas a
            WHERE a.id = %s
        """
        
        athlete_result = db.query_to_dict(athlete_query, (athlete_id,))
        if not athlete_result:
            raise HTTPException(status_code=404, detail="Athlete not found")
        
        athlete_info = athlete_result[0]
        
        # Latest training load metrics
        load_query = """
            SELECT *
            FROM metricas_carga
            WHERE atleta_id = %s
            ORDER BY semana_inicio DESC
            LIMIT 4
        """
        
        load_metrics = db.query_to_dict(load_query, (athlete_id,))
        
        # Recent wellness data
        wellness_query = """
            SELECT *
            FROM dados_wellness
            WHERE atleta_id = %s AND data >= %s
            ORDER BY data DESC
            LIMIT 14
        """
        
        wellness_data = db.query_to_dict(wellness_query, (athlete_id, start_date))
        
        # Physical evaluation data
        physical_query = """
            SELECT *
            FROM avaliacoes_fisicas
            WHERE atleta_id = %s
            ORDER BY data_avaliacao DESC
            LIMIT 3
        """
        
        physical_evals = db.query_to_dict(physical_query, (athlete_id,))
        
        # Latest risk assessment
        risk_query = """
            SELECT *
            FROM risk_assessment
            WHERE atleta_id = %s
            ORDER BY data_avaliacao DESC
            LIMIT 1
        """
        
        risk_assessment = db.query_to_dict(risk_query, (athlete_id,))
        
        # Recent session performance
        sessions_query = """
            SELECT 
                s.data,
                s.tipo,
                s.training_type,
                s.duracao_min,
                s.adversario,
                s.dificuldade_adversario,
                AVG(dp.carga_total) as avg_pse_load,
                AVG(dg.distancia_total) as avg_distance,
                AVG(dg.velocidade_max) as avg_max_speed,
                COUNT(DISTINCT dp.id) as pse_records,
                COUNT(DISTINCT dg.id) as gps_records
            FROM sessoes s
            LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
            LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
            WHERE s.data >= %s
            GROUP BY s.id, s.data, s.tipo, s.training_type, s.duracao_min, s.adversario, s.dificuldade_adversario
            ORDER BY s.data DESC
            LIMIT 20
        """
        
        recent_sessions = db.query_to_dict(sessions_query, (athlete_id, athlete_id, start_date))
        
        # Calculate wellness trends
        wellness_trends = None
        if len(wellness_data) >= 7:
            scores = [float(w['wellness_score']) for w in wellness_data if w['wellness_score']]
            if len(scores) >= 3:
                try:
                    trend_slope = np.polyfit(range(len(scores)), scores, 1)[0]
                except:
                    trend_slope = 0
                wellness_trends = {
                    "current_score": scores[0] if scores else None,
                    "avg_score_7d": round(np.mean(scores[:7]), 2) if len(scores) >= 7 else None,
                    "trend_direction": "improving" if trend_slope > 0.1 else "declining" if trend_slope < -0.1 else "stable",
                    "trend_slope": round(trend_slope, 3)
                }
        
        # Performance summary
        performance_summary = {
            "total_sessions": len([s for s in recent_sessions if s['pse_records'] > 0 or s['gps_records'] > 0]),
            "training_sessions": len([s for s in recent_sessions if s['tipo'] == 'treino']),
            "games": len([s for s in recent_sessions if s['tipo'] == 'jogo']),
            "avg_session_load": round(np.mean([float(s['avg_pse_load']) for s in recent_sessions if s['avg_pse_load'] is not None]), 2) if any(s['avg_pse_load'] is not None for s in recent_sessions) else None,
            "avg_distance": round(np.mean([float(s['avg_distance']) for s in recent_sessions if s['avg_distance'] is not None]), 2) if any(s['avg_distance'] is not None for s in recent_sessions) else None
        }
        
        return {
            "athlete_info": athlete_info,
            "training_load_metrics": load_metrics,
            "wellness_data": wellness_data,
            "wellness_trends": wellness_trends,
            "physical_evaluations": physical_evals,
            "risk_assessment": risk_assessment[0] if risk_assessment else None,
            "recent_sessions": recent_sessions,
            "performance_summary": performance_summary,
            "data_period": {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "days": days
            }
        }
    except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")


'''
    
    # Reconstruct the file
    new_lines = lines[:start_idx] + new_function.split('\n') + lines[end_idx:]
    new_content = '\n'.join(new_lines)
    
    # Write back to file
    with open(metrics_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Completely rewrote comprehensive athlete profile function")
    print("   • Fixed all indentation issues")
    print("   • Added proper try-except block")
    print("   • Corrected function structure")
else:
    print("❌ Could not find function boundaries to replace")
