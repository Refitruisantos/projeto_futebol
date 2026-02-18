from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from database import get_db, DatabaseConnection

router = APIRouter()


@router.get("/athletes/{athlete_id}/wellness", response_model=List[Dict[str, Any]])
def get_athlete_wellness(
    athlete_id: int,
    days: int = Query(30, le=365),
    db: DatabaseConnection = Depends(get_db)
):
    """Get wellness data for an athlete over specified days"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    query = """
        SELECT 
            dw.*,
            a.nome_completo,
            a.posicao
        FROM dados_wellness dw
        JOIN atletas a ON dw.atleta_id = a.id
        WHERE dw.atleta_id = %s 
        AND dw.data >= %s 
        AND dw.data <= %s
        ORDER BY dw.data DESC
    """
    
    return db.query_to_dict(query, (athlete_id, start_date, end_date))


@router.get("/athletes/{athlete_id}/wellness/latest", response_model=Dict[str, Any])
def get_latest_wellness(
    athlete_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Get latest wellness data for an athlete"""
    
    query = """
        SELECT 
            dw.*,
            a.nome_completo,
            a.posicao
        FROM dados_wellness dw
        JOIN atletas a ON dw.atleta_id = a.id
        WHERE dw.atleta_id = %s
        ORDER BY dw.data DESC
        LIMIT 1
    """
    
    result = db.query_to_dict(query, (athlete_id,))
    if not result:
        raise HTTPException(status_code=404, detail="No wellness data found")
    
    return result[0]


@router.get("/athletes/{athlete_id}/physical-evaluation", response_model=List[Dict[str, Any]])
def get_athlete_physical_evaluations(
    athlete_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Get physical evaluation history for an athlete"""
    
    query = """
        SELECT 
            af.*,
            a.nome_completo,
            a.posicao,
            a.altura_cm,
            a.massa_kg
        FROM avaliacoes_fisicas af
        JOIN atletas a ON af.atleta_id = a.id
        WHERE af.atleta_id = %s
        ORDER BY af.data_avaliacao DESC
    """
    
    return db.query_to_dict(query, (athlete_id,))


@router.get("/team/wellness/summary", response_model=Dict[str, Any])
def get_team_wellness_summary(
    days: int = Query(7, le=30),
    db: DatabaseConnection = Depends(get_db)
):
    """Get team wellness summary for recent days"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Overall team wellness
    summary_query = """
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
    
    summary = db.query_to_dict(summary_query, (start_date, end_date))[0]
    
    # Athletes needing attention
    attention_query = """
        SELECT DISTINCT
            a.id,
            a.nome_completo,
            a.posicao,
            dw.wellness_score,
            dw.wellness_status,
            dw.training_recommendation,
            dw.data
        FROM dados_wellness dw
        JOIN atletas a ON dw.atleta_id = a.id
        WHERE dw.data >= %s 
        AND dw.wellness_status IN ('poor', 'very_poor')
        ORDER BY dw.wellness_score ASC, dw.data DESC
    """
    
    attention_athletes = db.query_to_dict(attention_query, (start_date,))
    
    # Wellness trends by position
    position_query = """
        SELECT 
            a.posicao,
            COUNT(*) as reports,
            ROUND(AVG(dw.wellness_score), 2) as avg_wellness,
            ROUND(AVG(dw.readiness_score), 2) as avg_readiness
        FROM dados_wellness dw
        JOIN atletas a ON dw.atleta_id = a.id
        WHERE dw.data >= %s AND dw.data <= %s
        GROUP BY a.posicao
        ORDER BY avg_wellness DESC
    """
    
    position_trends = db.query_to_dict(position_query, (start_date, end_date))
    
    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "days": days
        },
        "summary": summary,
        "athletes_needing_attention": attention_athletes,
        "position_trends": position_trends
    }


@router.get("/team/physical-evaluations/summary", response_model=Dict[str, Any])
def get_team_physical_summary(
    evaluation_type: str = Query("pre_season"),
    db: DatabaseConnection = Depends(get_db)
):
    """Get team physical evaluation summary"""
    
    # Team averages by position
    position_query = """
        SELECT 
            a.posicao,
            COUNT(*) as athlete_count,
            ROUND(AVG(af.sprint_35m_seconds), 2) as avg_sprint_35m,
            ROUND(AVG(af.test_5_0_5_seconds), 2) as avg_5_0_5,
            ROUND(AVG(af.cmj_height_cm), 1) as avg_cmj,
            ROUND(AVG(af.vo2_max_ml_kg_min), 1) as avg_vo2_max,
            ROUND(AVG(af.percentile_speed), 0) as avg_speed_percentile,
            ROUND(AVG(af.percentile_power), 0) as avg_power_percentile,
            ROUND(AVG(af.percentile_endurance), 0) as avg_endurance_percentile
        FROM avaliacoes_fisicas af
        JOIN atletas a ON af.atleta_id = a.id
        WHERE af.tipo_avaliacao = %s
        GROUP BY a.posicao
        ORDER BY a.posicao
    """
    
    position_summary = db.query_to_dict(position_query, (evaluation_type,))
    
    # Top performers
    top_performers_query = """
        SELECT 
            a.nome_completo,
            a.posicao,
            af.sprint_35m_seconds,
            af.cmj_height_cm,
            af.vo2_max_ml_kg_min,
            af.percentile_speed,
            af.percentile_power,
            af.percentile_endurance,
            ROUND((af.percentile_speed + af.percentile_power + af.percentile_endurance) / 3.0, 1) as overall_percentile
        FROM avaliacoes_fisicas af
        JOIN atletas a ON af.atleta_id = a.id
        WHERE af.tipo_avaliacao = %s
        ORDER BY overall_percentile DESC
        LIMIT 10
    """
    
    top_performers = db.query_to_dict(top_performers_query, (evaluation_type,))
    
    # Areas needing improvement
    improvement_query = """
        SELECT 
            a.nome_completo,
            a.posicao,
            af.percentile_speed,
            af.percentile_power,
            af.percentile_endurance,
            CASE 
                WHEN af.percentile_speed < 25 THEN 'Speed'
                WHEN af.percentile_power < 25 THEN 'Power'
                WHEN af.percentile_endurance < 25 THEN 'Endurance'
                ELSE 'General Fitness'
            END as improvement_area
        FROM avaliacoes_fisicas af
        JOIN atletas a ON af.atleta_id = a.id
        WHERE af.tipo_avaliacao = %s
        AND (af.percentile_speed < 25 OR af.percentile_power < 25 OR af.percentile_endurance < 25)
        ORDER BY (af.percentile_speed + af.percentile_power + af.percentile_endurance) ASC
    """
    
    improvement_needed = db.query_to_dict(improvement_query, (evaluation_type,))
    
    return {
        "evaluation_type": evaluation_type,
        "position_summary": position_summary,
        "top_performers": top_performers,
        "improvement_needed": improvement_needed
    }


@router.get("/opponents/{opponent_name}/analysis", response_model=Dict[str, Any])
def get_opponent_analysis(
    opponent_name: str,
    db: DatabaseConnection = Depends(get_db)
):
    """Get detailed opponent analysis"""
    
    query = """
        SELECT * FROM analise_adversarios
        WHERE nome_equipa = %s
    """
    
    result = db.query_to_dict(query, (opponent_name,))
    if not result:
        raise HTTPException(status_code=404, detail="Opponent not found")
    
    opponent = result[0]
    
    # Get historical performance against this opponent
    history_query = """
        SELECT 
            s.data,
            s.resultado,
            s.local,
            s.dificuldade_adversario,
            COUNT(DISTINCT dp.atleta_id) as players_used,
            AVG(dp.carga_total) as avg_load
        FROM sessoes s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id
        WHERE s.tipo = 'jogo' AND s.adversario = %s
        GROUP BY s.id, s.data, s.resultado, s.local, s.dificuldade_adversario
        ORDER BY s.data DESC
    """
    
    history = db.query_to_dict(history_query, (opponent_name,))
    
    return {
        "opponent_info": opponent,
        "match_history": history,
        "tactical_recommendations": {
            "difficulty_home": opponent["dificuldade_casa"],
            "difficulty_away": opponent["dificuldade_fora"],
            "style": opponent["estilo_jogo"],
            "pressure_intensity": opponent["intensidade_pressao"],
            "key_strengths": _get_opponent_strengths(opponent),
            "key_weaknesses": _get_opponent_weaknesses(opponent)
        }
    }


def _get_opponent_strengths(opponent: Dict) -> List[str]:
    """Analyze opponent strengths based on data"""
    strengths = []
    
    if opponent["posse_bola_media"] > 55:
        strengths.append("High possession play")
    if opponent["passes_certos_percentagem"] > 85:
        strengths.append("Accurate passing")
    if opponent["finalizacoes_por_jogo"] > 12:
        strengths.append("High shot volume")
    if opponent["golos_marcados_casa"] > 2.0:
        strengths.append("Strong home attack")
    if opponent["golos_sofridos_casa"] < 1.0:
        strengths.append("Solid home defense")
    
    return strengths if strengths else ["Balanced team"]


def _get_opponent_weaknesses(opponent: Dict) -> List[str]:
    """Analyze opponent weaknesses based on data"""
    weaknesses = []
    
    if opponent["golos_sofridos_fora"] > 1.8:
        weaknesses.append("Vulnerable away defense")
    if opponent["golos_marcados_fora"] < 1.2:
        weaknesses.append("Poor away attack")
    if opponent["passes_certos_percentagem"] < 75:
        weaknesses.append("Inaccurate passing")
    if opponent["pontos_ultimos_5_jogos"] < 6:
        weaknesses.append("Poor recent form")
    
    return weaknesses if weaknesses else ["No clear weaknesses"]


@router.get("/wellness/risk-assessment", response_model=Dict[str, Any])
def get_wellness_risk_assessment(
    days: int = Query(7, le=14),
    db: DatabaseConnection = Depends(get_db)
):
    """Get wellness-based risk assessment for upcoming matches"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Athletes with declining wellness trends
    trend_query = """
        WITH wellness_trends AS (
            SELECT 
                dw.atleta_id,
                a.nome_completo,
                a.posicao,
                AVG(CASE WHEN dw.data >= %s - INTERVAL '3 days' THEN dw.wellness_score END) as recent_wellness,
                AVG(CASE WHEN dw.data < %s - INTERVAL '3 days' THEN dw.wellness_score END) as previous_wellness,
                COUNT(*) as reports
            FROM dados_wellness dw
            JOIN atletas a ON dw.atleta_id = a.id
            WHERE dw.data >= %s
            GROUP BY dw.atleta_id, a.nome_completo, a.posicao
            HAVING COUNT(*) >= 4
        )
        SELECT 
            *,
            ROUND(recent_wellness - previous_wellness, 2) as wellness_change,
            CASE 
                WHEN recent_wellness - previous_wellness < -1.0 THEN 'high_risk'
                WHEN recent_wellness - previous_wellness < -0.5 THEN 'moderate_risk'
                ELSE 'low_risk'
            END as risk_level
        FROM wellness_trends
        WHERE recent_wellness IS NOT NULL AND previous_wellness IS NOT NULL
        ORDER BY wellness_change ASC
    """
    
    risk_trends = db.query_to_dict(trend_query, (end_date, end_date, start_date))
    
    # Current high-risk athletes
    current_risk_query = """
        SELECT 
            a.nome_completo,
            a.posicao,
            dw.wellness_score,
            dw.readiness_score,
            dw.wellness_status,
            dw.training_recommendation,
            dw.data
        FROM dados_wellness dw
        JOIN atletas a ON dw.atleta_id = a.id
        WHERE dw.data = (
            SELECT MAX(data) 
            FROM dados_wellness dw2 
            WHERE dw2.atleta_id = dw.atleta_id
        )
        AND dw.wellness_status IN ('poor', 'very_poor')
        ORDER BY dw.wellness_score ASC
    """
    
    current_risks = db.query_to_dict(current_risk_query)
    
    return {
        "assessment_period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },
        "declining_trends": [r for r in risk_trends if r["risk_level"] in ["high_risk", "moderate_risk"]],
        "current_high_risk": current_risks,
        "recommendations": {
            "high_risk_count": len([r for r in risk_trends if r["risk_level"] == "high_risk"]),
            "moderate_risk_count": len([r for r in risk_trends if r["risk_level"] == "moderate_risk"]),
            "total_at_risk": len(current_risks),
            "suggested_actions": _get_risk_recommendations(risk_trends, current_risks)
        }
    }


def _get_risk_recommendations(trends: List[Dict], current_risks: List[Dict]) -> List[str]:
    """Generate risk-based recommendations"""
    recommendations = []
    
    high_risk_count = len([r for r in trends if r["risk_level"] == "high_risk"])
    if high_risk_count > 3:
        recommendations.append("Consider rotating squad heavily for next match")
    elif high_risk_count > 1:
        recommendations.append("Monitor high-risk players closely in training")
    
    if len(current_risks) > 2:
        recommendations.append("Implement team recovery protocols")
    
    if any(r["posicao"] in ["MC", "DL"] for r in current_risks):
        recommendations.append("Prepare backup options for key positions")
    
    return recommendations if recommendations else ["Team wellness levels are acceptable"]
