#!/usr/bin/env python3
"""
Add Unified API Endpoints to Metrics Router
===========================================
Adds comprehensive wellness and physical evaluation endpoints to the existing
metrics router, creating a unified API that cross-references all data sources.
"""

import os

# Read the current metrics.py file
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add the new unified endpoints at the end of the file
new_endpoints = '''

@router.get("/athletes/{athlete_id}/comprehensive-profile")
def get_comprehensive_athlete_profile(
    athlete_id: int,
    days: int = Query(30, le=365),
    db: DatabaseConnection = Depends(get_db)
):
    """Get comprehensive athlete profile combining all data sources"""
    
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
            trend_slope = np.polyfit(range(len(scores)), scores, 1)[0]
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
        "avg_session_load": round(np.mean([float(s['avg_pse_load']) for s in recent_sessions if s['avg_pse_load']]), 2) if any(s['avg_pse_load'] for s in recent_sessions) else None,
        "avg_distance": round(np.mean([float(s['avg_distance']) for s in recent_sessions if s['avg_distance']]), 2) if any(s['avg_distance'] for s in recent_sessions) else None
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


@router.get("/team/wellness-summary")
def get_team_wellness_summary(
    days: int = Query(7, le=30),
    db: DatabaseConnection = Depends(get_db)
):
    """Get comprehensive team wellness and risk summary"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Team wellness overview
    wellness_summary_query = """
        SELECT 
            COUNT(*) as total_reports,
            ROUND(AVG(wellness_score), 2) as avg_wellness_score,
            ROUND(AVG(readiness_score), 2) as avg_readiness_score,
            COUNT(CASE WHEN wellness_status = 'excellent' THEN 1 END) as excellent_count,
            COUNT(CASE WHEN wellness_status = 'good' THEN 1 END) as good_count,
            COUNT(CASE WHEN wellness_status = 'moderate' THEN 1 END) as moderate_count,
            COUNT(CASE WHEN wellness_status = 'poor' THEN 1 END) as poor_count,
            COUNT(CASE WHEN wellness_status = 'very_poor' THEN 1 END) as very_poor_count
        FROM dados_wellness dw
        WHERE dw.data >= %s AND dw.data <= %s
    """
    
    wellness_summary = db.query_to_dict(wellness_summary_query, (start_date, end_date))[0]
    
    # Current risk assessment summary
    risk_summary_query = """
        SELECT 
            COUNT(*) as total_assessments,
            COUNT(CASE WHEN injury_risk_category = 'very_high' THEN 1 END) as very_high_injury_risk,
            COUNT(CASE WHEN injury_risk_category = 'high' THEN 1 END) as high_injury_risk,
            COUNT(CASE WHEN substitution_risk_category IN ('high', 'very_high') THEN 1 END) as high_substitution_risk,
            ROUND(AVG(prediction_confidence), 2) as avg_confidence
        FROM risk_assessment ra
        WHERE ra.data_avaliacao = (SELECT MAX(data_avaliacao) FROM risk_assessment)
    """
    
    risk_summary = db.query_to_dict(risk_summary_query)[0]
    
    # Athletes needing attention
    attention_query = """
        SELECT 
            a.nome_completo,
            a.posicao,
            ra.injury_risk_score,
            ra.substitution_risk_score,
            ra.training_recommendation,
            dw.wellness_score,
            dw.wellness_status
        FROM risk_assessment ra
        JOIN atletas a ON ra.atleta_id = a.id
        LEFT JOIN dados_wellness dw ON dw.atleta_id = a.id AND dw.data = (SELECT MAX(data) FROM dados_wellness WHERE atleta_id = a.id)
        WHERE ra.data_avaliacao = (SELECT MAX(data_avaliacao) FROM risk_assessment)
        AND (ra.injury_risk_category IN ('high', 'very_high') OR ra.substitution_risk_category IN ('high', 'very_high'))
        ORDER BY ra.injury_risk_score DESC
    """
    
    attention_athletes = db.query_to_dict(attention_query)
    
    # Position-based wellness trends
    position_trends_query = """
        SELECT 
            a.posicao,
            COUNT(*) as reports,
            ROUND(AVG(dw.wellness_score), 2) as avg_wellness,
            ROUND(AVG(dw.readiness_score), 2) as avg_readiness,
            COUNT(CASE WHEN dw.wellness_status IN ('poor', 'very_poor') THEN 1 END) as at_risk_count
        FROM dados_wellness dw
        JOIN atletas a ON dw.atleta_id = a.id
        WHERE dw.data >= %s AND dw.data <= %s
        GROUP BY a.posicao
        ORDER BY avg_wellness DESC
    """
    
    position_trends = db.query_to_dict(position_trends_query, (start_date, end_date))
    
    # Next match readiness
    next_match_query = """
        SELECT 
            s.data as match_date,
            s.adversario,
            s.dificuldade_adversario,
            COUNT(mr.atleta_id) as assessed_players,
            COUNT(CASE WHEN mr.starting_recommendation = true THEN 1 END) as recommended_starters,
            COUNT(CASE WHEN mr.monitoring_priority = 'critical' THEN 1 END) as critical_monitoring,
            ROUND(AVG(mr.overall_readiness_score), 2) as avg_team_readiness
        FROM sessoes s
        LEFT JOIN match_readiness mr ON s.id = mr.sessao_id
        WHERE s.tipo = 'jogo' AND s.data >= %s
        GROUP BY s.id, s.data, s.adversario, s.dificuldade_adversario
        ORDER BY s.data ASC
        LIMIT 1
    """
    
    next_match = db.query_to_dict(next_match_query, (end_date,))
    
    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "days": days
        },
        "wellness_summary": wellness_summary,
        "risk_summary": risk_summary,
        "athletes_needing_attention": attention_athletes,
        "position_trends": position_trends,
        "next_match_readiness": next_match[0] if next_match else None
    }


@router.get("/opponents/{opponent_name}/analysis")
def get_opponent_analysis(
    opponent_name: str,
    db: DatabaseConnection = Depends(get_db)
):
    """Get comprehensive opponent analysis with historical performance"""
    
    # Opponent data
    opponent_query = """
        SELECT * FROM analise_adversarios
        WHERE nome_equipa = %s
    """
    
    opponent_result = db.query_to_dict(opponent_query, (opponent_name,))
    if not opponent_result:
        raise HTTPException(status_code=404, detail="Opponent not found")
    
    opponent_info = opponent_result[0]
    
    # Historical matches against this opponent
    history_query = """
        SELECT 
            s.data,
            s.resultado,
            s.local,
            s.dificuldade_adversario,
            COUNT(DISTINCT dp.atleta_id) as players_used,
            AVG(dp.carga_total) as avg_team_load,
            AVG(dg.distancia_total) as avg_team_distance,
            SUM(CASE WHEN dp.carga_total > 500 THEN 1 ELSE 0 END) as high_load_players
        FROM sessoes s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id
        WHERE s.tipo = 'jogo' AND s.adversario = %s
        GROUP BY s.id, s.data, s.resultado, s.local, s.dificuldade_adversario
        ORDER BY s.data DESC
    """
    
    match_history = db.query_to_dict(history_query, (opponent_name,))
    
    # Tactical recommendations based on opponent data
    tactical_recommendations = {
        "difficulty_rating": {
            "home": float(opponent_info["dificuldade_casa"]),
            "away": float(opponent_info["dificuldade_fora"])
        },
        "style_analysis": {
            "playing_style": opponent_info["estilo_jogo"],
            "pressure_intensity": opponent_info["intensidade_pressao"],
            "possession_avg": float(opponent_info["posse_bola_media"]),
            "pass_accuracy": float(opponent_info["passes_certos_percentagem"])
        },
        "key_metrics": {
            "goals_scored_home": float(opponent_info["golos_marcados_casa"]),
            "goals_conceded_home": float(opponent_info["golos_sofridos_casa"]),
            "goals_scored_away": float(opponent_info["golos_marcados_fora"]),
            "goals_conceded_away": float(opponent_info["golos_sofridos_fora"]),
            "recent_form_points": opponent_info["pontos_ultimos_5_jogos"]
        },
        "preparation_recommendations": _generate_opponent_recommendations(opponent_info)
    }
    
    return {
        "opponent_info": opponent_info,
        "match_history": match_history,
        "tactical_analysis": tactical_recommendations,
        "historical_performance": {
            "total_matches": len(match_history),
            "avg_difficulty": round(np.mean([float(m['dificuldade_adversario']) for m in match_history if m['dificuldade_adversario']]), 2) if match_history else None,
            "avg_team_load": round(np.mean([float(m['avg_team_load']) for m in match_history if m['avg_team_load']]), 2) if match_history else None
        }
    }


def _generate_opponent_recommendations(opponent_data: Dict) -> List[str]:
    """Generate tactical recommendations based on opponent analysis"""
    recommendations = []
    
    difficulty = max(float(opponent_data["dificuldade_casa"]), float(opponent_data["dificuldade_fora"]))
    style = opponent_data["estilo_jogo"]
    pressure = opponent_data["intensidade_pressao"]
    possession = float(opponent_data["posse_bola_media"])
    
    if difficulty >= 4.0:
        recommendations.append("High-difficulty opponent - consider squad rotation to manage load")
        recommendations.append("Implement intensive recovery protocols post-match")
    
    if style == "attacking":
        recommendations.append("Focus on defensive shape and counter-attacking opportunities")
    elif style == "defensive":
        recommendations.append("Emphasize patient build-up play and set-piece preparation")
    elif style == "counter_attack":
        recommendations.append("Maintain possession and avoid risky passes in dangerous areas")
    
    if pressure == "high":
        recommendations.append("Practice playing out from the back under pressure")
        recommendations.append("Consider players with better technical skills under pressure")
    
    if possession > 60:
        recommendations.append("Prepare for extended defensive periods - focus on fitness")
    elif possession < 45:
        recommendations.append("Expect more possession - prepare attacking patterns")
    
    return recommendations if recommendations else ["Standard preparation recommended"]


@router.get("/risk-assessment/current")
def get_current_risk_assessment(
    db: DatabaseConnection = Depends(get_db)
):
    """Get current team-wide risk assessment with substitution recommendations"""
    
    # Get latest risk assessments for all athletes
    risk_query = """
        SELECT 
            ra.*,
            a.nome_completo,
            a.posicao,
            a.numero_camisola
        FROM risk_assessment ra
        JOIN atletas a ON ra.atleta_id = a.id
        WHERE ra.data_avaliacao = (SELECT MAX(data_avaliacao) FROM risk_assessment)
        ORDER BY ra.injury_risk_score DESC
    """
    
    risk_assessments = db.query_to_dict(risk_query)
    
    # Get match readiness for next game
    readiness_query = """
        SELECT 
            mr.*,
            a.nome_completo,
            a.posicao,
            s.adversario,
            s.data as match_date
        FROM match_readiness mr
        JOIN atletas a ON mr.atleta_id = a.id
        JOIN sessoes s ON mr.sessao_id = s.id
        WHERE s.data = (SELECT MIN(data) FROM sessoes WHERE tipo = 'jogo' AND data >= CURRENT_DATE)
        ORDER BY mr.overall_readiness_score DESC
    """
    
    match_readiness = db.query_to_dict(readiness_query)
    
    # Summary statistics
    risk_summary = {
        "total_players": len(risk_assessments),
        "high_injury_risk": len([r for r in risk_assessments if r['injury_risk_category'] in ['high', 'very_high']]),
        "high_substitution_risk": len([r for r in risk_assessments if r['substitution_risk_category'] in ['high', 'very_high']]),
        "recommended_starters": len([r for r in match_readiness if r['starting_recommendation']]) if match_readiness else 0,
        "critical_monitoring": len([r for r in match_readiness if r['monitoring_priority'] == 'critical']) if match_readiness else 0
    }
    
    return {
        "assessment_date": risk_assessments[0]['data_avaliacao'] if risk_assessments else None,
        "risk_assessments": risk_assessments,
        "match_readiness": match_readiness,
        "summary": risk_summary,
        "next_match": {
            "opponent": match_readiness[0]['adversario'] if match_readiness else None,
            "date": match_readiness[0]['match_date'] if match_readiness else None
        }
    }
'''

# Insert the new endpoints before the final closing of the file
if content.endswith('\n'):
    new_content = content + new_endpoints
else:
    new_content = content + '\n' + new_endpoints

# Write the updated content back to the file
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Added unified API endpoints to metrics router:")
print("   • /api/metrics/athletes/{id}/comprehensive-profile")
print("   • /api/metrics/team/wellness-summary") 
print("   • /api/metrics/opponents/{name}/analysis")
print("   • /api/metrics/risk-assessment/current")
print("\n🔗 All data sources now cross-referenced in single API")
