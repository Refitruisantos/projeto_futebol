from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from database import get_db, DatabaseConnection
import logging
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/team/dashboard")
def team_dashboard(
    db: DatabaseConnection = Depends(get_db)
):
    """
    Enhanced team dashboard with decision support and risk integration.
    
    Answers three key questions:
    1. Who is at risk?
    2. Why (in simple terms)?
    3. Is the situation getting worse or better?
    """
    
    # Get most recent week from metricas_carga
    most_recent_week_query = """
        SELECT MAX(semana_inicio) as week_start
        FROM metricas_carga
    """
    week_result = db.query_to_dict(most_recent_week_query)
    most_recent_week = week_result[0]['week_start'] if week_result else None
    
    if not most_recent_week:
        # Fallback to simple dashboard if no metrics calculated yet
        simple_query = """
            SELECT 
                a.id as atleta_id,
                a.nome_completo,
                a.posicao,
                a.ativo,
                0 as weekly_load,
                0 as monotony,
                0 as strain,
                0 as acwr,
                'green' as risk_monotony,
                'green' as risk_strain,
                'green' as risk_acwr,
                0 as training_days,
                0 as num_sessoes,
                0 as distancia_total_media,
                0 as velocidade_max_media,
                0 as aceleracoes_media,
                'green' as risk_overall
            FROM atletas a
            WHERE a.ativo = TRUE
            ORDER BY a.nome_completo
        """
        athletes = db.query_to_dict(simple_query)
        return {
            "week_analyzed": None,
            "athletes_overview": athletes,
            "top_load_athletes": [],
            "at_risk_athletes": [],
            "risk_summary": {"red": 0, "yellow": 0, "green": len(athletes)},
            "team_context": {
                "total_athletes": len(athletes),
                "message": "No training data available. Add athletes and training sessions to see metrics."
            }
        }
    
    # Get team averages and std deviations for z-score calculation
    team_stats_query = """
        SELECT 
            AVG(carga_total_semanal) as mean_load,
            STDDEV(carga_total_semanal) as std_load,
            AVG(monotonia) as mean_monotony,
            STDDEV(monotonia) as std_monotony,
            AVG(tensao) as mean_strain,
            STDDEV(tensao) as std_strain,
            AVG(acwr) as mean_acwr,
            STDDEV(acwr) as std_acwr
        FROM metricas_carga
        WHERE semana_inicio = %s
    """
    team_stats = db.query_to_dict(team_stats_query, (most_recent_week,))[0]
    
    # Enhanced dashboard query with risk indicators
    dashboard_query = """
        WITH latest_metrics AS (
            SELECT 
                a.id as atleta_id,
                a.nome_completo,
                a.numero_camisola,
                a.posicao,
                a.ativo,
                mc.carga_total_semanal as weekly_load,
                mc.monotonia as monotony,
                mc.tensao as strain,
                mc.acwr,
                mc.nivel_risco_monotonia as risk_monotony,
                mc.nivel_risco_tensao as risk_strain,
                mc.nivel_risco_acwr as risk_acwr,
                mc.dias_treino as training_days
            FROM atletas a
            LEFT JOIN metricas_carga mc ON mc.atleta_id = a.id AND mc.semana_inicio = %s
            WHERE a.ativo = TRUE
        ),
        gps_summary AS (
            SELECT 
                g.atleta_id,
                COUNT(DISTINCT g.sessao_id) as num_sessoes,
                ROUND(AVG(g.distancia_total)::numeric, 2) as distancia_total_media,
                ROUND(AVG(g.velocidade_max)::numeric, 2) as velocidade_max_media,
                ROUND(AVG(g.aceleracoes)::numeric, 2) as aceleracoes_media
            FROM dados_gps g
            JOIN sessoes s ON s.id = g.sessao_id
            WHERE s.data >= %s AND s.data < %s + INTERVAL '7 days'
            GROUP BY g.atleta_id
        )
        SELECT 
            lm.*,
            COALESCE(gs.num_sessoes, 0) as num_sessoes,
            gs.distancia_total_media,
            gs.velocidade_max_media,
            gs.aceleracoes_media,
            -- Determine overall risk (worst of the three)
            CASE 
                WHEN lm.risk_monotony = 'red' OR lm.risk_strain = 'red' OR lm.risk_acwr = 'red' THEN 'red'
                WHEN lm.risk_monotony = 'yellow' OR lm.risk_strain = 'yellow' OR lm.risk_acwr = 'yellow' THEN 'yellow'
                WHEN lm.risk_monotony = 'green' OR lm.risk_strain = 'green' OR lm.risk_acwr = 'green' THEN 'green'
                ELSE 'unknown'
            END as risk_overall
        FROM latest_metrics lm
        LEFT JOIN gps_summary gs ON gs.atleta_id = lm.atleta_id
        ORDER BY 
            CASE 
                WHEN lm.risk_monotony = 'red' OR lm.risk_strain = 'red' OR lm.risk_acwr = 'red' THEN 1
                WHEN lm.risk_monotony = 'yellow' OR lm.risk_strain = 'yellow' OR lm.risk_acwr = 'yellow' THEN 2
                WHEN lm.risk_monotony = 'green' OR lm.risk_strain = 'green' OR lm.risk_acwr = 'green' THEN 3
                ELSE 4
            END,
            lm.nome_completo
    """
    
    athletes = db.query_to_dict(dashboard_query, (most_recent_week, most_recent_week, most_recent_week))
    
    # Calculate z-scores and enrich data
    risk_counts = {"red": 0, "yellow": 0, "green": 0, "unknown": 0}
    
    for athlete in athletes:
        # Calculate z-scores (standardized vs team)
        if team_stats['std_load'] and team_stats['std_load'] > 0:
            athlete['z_load'] = round((athlete['weekly_load'] - team_stats['mean_load']) / team_stats['std_load'], 2) if athlete['weekly_load'] else None
        else:
            athlete['z_load'] = None
            
        if team_stats['std_monotony'] and team_stats['std_monotony'] > 0:
            athlete['z_monotony'] = round((athlete['monotony'] - team_stats['mean_monotony']) / team_stats['std_monotony'], 2) if athlete['monotony'] else None
        else:
            athlete['z_monotony'] = None
            
        if team_stats['std_strain'] and team_stats['std_strain'] > 0:
            athlete['z_strain'] = round((athlete['strain'] - team_stats['mean_strain']) / team_stats['std_strain'], 2) if athlete['strain'] else None
        else:
            athlete['z_strain'] = None
            
        if team_stats['std_acwr'] and team_stats['std_acwr'] > 0:
            athlete['z_acwr'] = round((athlete['acwr'] - team_stats['mean_acwr']) / team_stats['std_acwr'], 2) if athlete['acwr'] else None
        else:
            athlete['z_acwr'] = None
        
        # Count risk levels
        risk_counts[athlete['risk_overall']] = risk_counts.get(athlete['risk_overall'], 0) + 1
    
    # Get top 5 athletes by load
    top_load_athletes = sorted(
        [a for a in athletes if a['weekly_load']],
        key=lambda x: x['weekly_load'],
        reverse=True
    )[:5]
    
    # Get at-risk athletes from risk_assessment table with detailed explanations
    risk_athletes_query = """
        SELECT DISTINCT
            a.id as atleta_id,
            a.nome_completo as nome,
            a.posicao,
            r.injury_risk_category as classificacao,
            r.acwr_risk_score,
            r.monotony_risk_score,
            r.strain_risk_score,
            r.wellness_risk_score,
            r.fatigue_accumulation_score,
            CASE 
                WHEN r.acwr_risk_score >= 4.0 THEN 'ACWR crítico (risco lesão)'
                WHEN r.acwr_risk_score >= 3.0 THEN 'ACWR elevado'
                ELSE ''
            END ||
            CASE 
                WHEN r.monotony_risk_score >= 4.0 THEN '; Monotonia excessiva (treino repetitivo)'
                WHEN r.monotony_risk_score >= 3.0 THEN '; Monotonia elevada'
                ELSE ''
            END ||
            CASE 
                WHEN r.strain_risk_score >= 4.0 THEN '; Tensão muito alta (fadiga acumulada)'
                WHEN r.strain_risk_score >= 3.0 THEN '; Tensão elevada'
                ELSE ''
            END ||
            CASE 
                WHEN r.wellness_risk_score >= 4.0 THEN '; Bem-estar comprometido'
                WHEN r.wellness_risk_score >= 3.0 THEN '; Bem-estar reduzido'
                ELSE ''
            END ||
            CASE 
                WHEN r.fatigue_accumulation_score >= 4.0 THEN '; Fadiga acumulada crítica'
                WHEN r.fatigue_accumulation_score >= 3.0 THEN '; Fadiga acumulada'
                ELSE ''
            END as risk_explanation
        FROM risk_assessment r
        JOIN atletas a ON r.atleta_id = a.id
        WHERE a.ativo = TRUE 
        AND (r.injury_risk_category = 'Alto' OR r.injury_risk_category = 'very_high')
        ORDER BY a.nome_completo
    """
    at_risk_athletes = db.query_to_dict(risk_athletes_query)
    
    return {
        "week_analyzed": most_recent_week.isoformat() if most_recent_week else None,
        "athletes_overview": athletes,
        "top_load_athletes": top_load_athletes,
        "at_risk_athletes": at_risk_athletes,
        "risk_summary": risk_counts,
        "team_context": {
            "mean_load": round(float(team_stats['mean_load']), 2) if team_stats['mean_load'] else None,
            "mean_monotony": round(float(team_stats['mean_monotony']), 2) if team_stats['mean_monotony'] else None,
            "mean_strain": round(float(team_stats['mean_strain']), 2) if team_stats['mean_strain'] else None,
            "mean_acwr": round(float(team_stats['mean_acwr']), 2) if team_stats['mean_acwr'] else None
        }
    }


@router.get("/team/summary")
def team_summary(
    db: DatabaseConnection = Depends(get_db)
):
    # Get team summary metrics using ALL available data (no date filtering for historical data)
    summary_query = """
        SELECT 
            COUNT(DISTINCT a.id) as total_athletes,
            COUNT(DISTINCT s.id) as total_sessions_7d,
            ROUND(AVG(p.carga_total)::numeric, 2) as avg_player_load_7d,
            ROUND(AVG(g.distancia_total)::numeric, 2) as avg_distance,
            ROUND(AVG(g.velocidade_max)::numeric, 2) as avg_max_speed,
            ROUND(AVG(g.aceleracoes)::numeric, 2) as avg_accelerations,
            ROUND(AVG(g.desaceleracoes)::numeric, 2) as avg_decelerations,
            ROUND(AVG(g.sprints)::numeric, 2) as avg_sprints,
            ROUND(AVG(g.dist_19_8_kmh)::numeric, 2) as avg_high_speed_distance,
            ROUND(AVG(g.rhie)::numeric, 2) as avg_rhie
        FROM atletas a
        LEFT JOIN dados_gps g ON g.atleta_id = a.id
        LEFT JOIN dados_pse p ON p.atleta_id = a.id
        LEFT JOIN sessoes s ON s.id = g.sessao_id OR s.id = p.sessao_id
        WHERE a.ativo = TRUE
    """
    summary = db.query_to_dict(summary_query)[0]
    
    # Get high-risk athletes count
    risk_query = """
        SELECT COUNT(DISTINCT r.atleta_id) as high_risk_athletes
        FROM risk_assessment r
        JOIN atletas a ON r.atleta_id = a.id
        WHERE a.ativo = TRUE 
        AND (r.injury_risk_category = 'Alto' OR r.injury_risk_category = 'very_high')
    """
    risk_result = db.query_to_dict(risk_query)
    summary['high_risk_athletes'] = risk_result[0]['high_risk_athletes'] if risk_result else 0
    
    return summary


@router.get("/games/data")
def get_games_data(
    db: DatabaseConnection = Depends(get_db)
):
    """
    Get all games with combined GPS and PSE metrics for visualization
    Returns game-by-game data with key performance metrics
    """
    
    try:
        # First, test if we can get sessions at all
        logger.info("Fetching games data...")
        
        query = """
            SELECT 
                s.id as sessao_id,
                s.data::text as data,
                COALESCE(s.tipo, 'treino') as tipo,
                COALESCE(s.adversario, '') as adversario,
                s.local,
                s.resultado,
                COUNT(DISTINCT g.atleta_id) as num_atletas,
                COALESCE(ROUND(AVG(g.distancia_total)::numeric, 2), 0) as avg_distance,
                COALESCE(ROUND(AVG(g.velocidade_max)::numeric, 2), 0) as avg_max_speed,
                COALESCE(ROUND(AVG(g.aceleracoes)::numeric, 2), 0) as avg_accelerations,
                COALESCE(ROUND(AVG(g.desaceleracoes)::numeric, 2), 0) as avg_decelerations,
                COALESCE(ROUND(AVG(g.sprints)::numeric, 2), 0) as avg_sprints,
                COALESCE(ROUND(AVG(g.dist_19_8_kmh)::numeric, 2), 0) as avg_high_speed_distance,
                COALESCE(ROUND(AVG(g.player_load)::numeric, 2), 0) as avg_player_load,
                COALESCE(ROUND(AVG(p.carga_total)::numeric, 2), 0) as avg_pse_load,
                COALESCE(ROUND(AVG(p.pse)::numeric, 2), 0) as avg_pse,
                COALESCE(ROUND(AVG(p.duracao_min)::numeric, 2), 0) as avg_duration
            FROM sessoes s
            LEFT JOIN dados_gps g ON g.sessao_id = s.id
            LEFT JOIN dados_pse p ON p.sessao_id = s.id
            GROUP BY s.id, s.data, s.tipo, s.adversario, s.local, s.resultado
            HAVING COUNT(DISTINCT g.atleta_id) > 0 OR COUNT(DISTINCT p.atleta_id) > 0
            ORDER BY s.data DESC
            LIMIT 200
        """
        
        logger.info(f"Executing query: {query}")
        games = db.query_to_dict(query)
        logger.info(f"Query returned {len(games)} games")
        
        return {
            "total_games": len(games),
            "games": games
        }
    except Exception as e:
        logger.error(f"Error fetching games data: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/games/player/{athlete_id}")
def get_player_games_data(
    athlete_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Get game-by-game data for a specific player
    Includes roster verification
    """
    
    try:
        # First, verify player exists and get info
        player_query = """
            SELECT 
                id,
                nome_completo,
                posicao,
                numero_camisola,
                ativo
            FROM atletas
            WHERE id = %s
        """
        
        player_result = db.query_to_dict(player_query, (athlete_id,))
        
        if not player_result:
            raise HTTPException(status_code=404, detail=f"Player with ID {athlete_id} not found")
        
        player_info = player_result[0]
        
        # Get player's game-by-game data
        games_query = """
            SELECT 
                s.id as sessao_id,
                s.data::text as data,
                COALESCE(s.tipo, 'treino') as tipo,
                COALESCE(s.adversario, '') as adversario,
                s.local,
                s.resultado,
                COALESCE(g.distancia_total, 0) as distance,
                COALESCE(g.velocidade_max, 0) as max_speed,
                COALESCE(g.aceleracoes, 0) as accelerations,
                COALESCE(g.desaceleracoes, 0) as decelerations,
                COALESCE(g.sprints, 0) as sprints,
                COALESCE(g.dist_19_8_kmh, 0) as high_speed_distance,
                COALESCE(g.player_load, 0) as player_load,
                COALESCE(p.carga_total, 0) as pse_load,
                COALESCE(p.pse, 0) as pse,
                COALESCE(p.duracao_min, 0) as duration,
                CASE 
                    WHEN g.atleta_id IS NOT NULL THEN TRUE
                    ELSE FALSE
                END as has_gps_data,
                CASE 
                    WHEN p.atleta_id IS NOT NULL THEN TRUE
                    ELSE FALSE
                END as has_pse_data
            FROM sessoes s
            LEFT JOIN dados_gps g ON g.sessao_id = s.id AND g.atleta_id = %s
            LEFT JOIN dados_pse p ON p.sessao_id = s.id AND p.atleta_id = %s
            WHERE (g.atleta_id IS NOT NULL OR p.atleta_id IS NOT NULL)
            ORDER BY s.data DESC
            LIMIT 200
        """
        
        games = db.query_to_dict(games_query, (athlete_id, athlete_id))
        
        return {
            "player_info": player_info,
            "is_active_roster": player_info['ativo'],
            "total_games": len(games),
            "games": games
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player games data: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/athletes/{athlete_id}/comprehensive-profile")
def get_comprehensive_athlete_profile(
    athlete_id: int,
    days: int = Query(90, le=365),  # Increased from 30 to 90 days
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
        
        # Latest training load metrics with chart data
        load_query = """
            SELECT 
                semana_inicio,
                carga_total_semanal,
                carga_aguda,
                carga_cronica,
                acwr,
                monotonia,
                tensao,
                media_carga,
                nivel_risco_acwr
            FROM metricas_carga
            WHERE atleta_id = %s
            ORDER BY semana_inicio DESC
            LIMIT 12
        """
        
        load_metrics = db.query_to_dict(load_query, (athlete_id,))
        
        # Format load data for chart
        load_chart_data = []
        for metric in reversed(load_metrics):  # Reverse for chronological order
            load_chart_data.append({
                'week': metric['semana_inicio'].strftime('%Y-%m-%d'),
                'acute_load': float(metric['carga_aguda']) if metric['carga_aguda'] else 0,
                'chronic_load': float(metric['carga_cronica']) if metric['carga_cronica'] else 0,
                'ac_ratio': float(metric['acwr']) if metric['acwr'] else 0,
                'monotony': float(metric['monotonia']) if metric['monotonia'] else 0,
                'strain': float(metric['tensao']) if metric['tensao'] else 0,
                'total_load': float(metric['carga_total_semanal']) if metric['carga_total_semanal'] else 0
            })

        # Recent wellness data (expanded range)
        wellness_query = """
            SELECT *
            FROM dados_wellness
            WHERE atleta_id = %s AND data >= %s
            ORDER BY data DESC
            LIMIT 30
        """
        
        wellness_data = db.query_to_dict(wellness_query, (athlete_id, start_date))
        
        # Physical evaluation data
        physical_query = """
            SELECT *
            FROM avaliacoes_fisicas
            WHERE atleta_id = %s
            ORDER BY data_avaliacao DESC
            LIMIT 5
        """
        
        physical_evaluations = db.query_to_dict(physical_query, (athlete_id,))
        
        # Wellness trends calculation
        wellness_trends = None
        if len(wellness_data) >= 7:
            recent_7d = wellness_data[:7]
            previous_7d = wellness_data[7:14] if len(wellness_data) >= 14 else []
            
            avg_score_7d = np.mean([w['wellness_score'] for w in recent_7d if w['wellness_score']])
            
            if previous_7d:
                avg_score_prev_7d = np.mean([w['wellness_score'] for w in previous_7d if w['wellness_score']])
                trend_slope = avg_score_7d - avg_score_prev_7d
                
                if trend_slope > 0.2:
                    trend_direction = 'improving'
                elif trend_slope < -0.2:
                    trend_direction = 'declining'
                else:
                    trend_direction = 'stable'
            else:
                trend_direction = 'stable'
                
            wellness_trends = {
                'avg_score_7d': round(avg_score_7d, 1),
                'trend_direction': trend_direction
            }

        # Risk assessment
        risk_query = """
            SELECT *
            FROM risk_assessment
            WHERE atleta_id = %s
            ORDER BY data_avaliacao DESC
            LIMIT 1
        """
        
        risk_assessment = db.query_to_dict(risk_query, (athlete_id,))
        risk_data = risk_assessment[0] if risk_assessment else None

        # Recent sessions with GPS data (expanded range and more data)
        sessions_query = """
            SELECT DISTINCT
                s.id,
                s.data,
                s.tipo,
                s.adversario,
                s.dificuldade_adversario,
                odd.explanation as difficulty_explanation,
                s.jornada,
                s.resultado,
                AVG(dg.distancia_total) as avg_distance,
                AVG(dg.velocidade_max) as avg_max_speed,
                AVG(dg.velocidade_media) as avg_avg_speed,
                AVG(dg.sprints) as avg_sprints,
                AVG(dg.aceleracoes) as avg_accelerations,
                AVG(dg.desaceleracoes) as avg_decelerations,
                AVG(dg.player_load) as avg_player_load,
                AVG(dg.num_desaceleracoes_altas) as avg_high_decelerations,
                AVG(dg.desaceleracao_maxima) as avg_max_deceleration,
                AVG(dp.pse) as avg_pse_load,
                COUNT(DISTINCT dp.atleta_id) as pse_records,
                COUNT(DISTINCT dg.atleta_id) as gps_records
            FROM sessoes s
            LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
            LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
            LEFT JOIN opponent_difficulty_details odd ON s.adversario = odd.opponent_name
            WHERE s.data >= %s
            AND (dg.atleta_id = %s OR dp.atleta_id = %s)
            GROUP BY s.id, s.data, s.tipo, s.adversario, s.dificuldade_adversario, odd.explanation, s.jornada, s.resultado
            ORDER BY s.data DESC
            LIMIT 50
        """
        
        recent_sessions = db.query_to_dict(sessions_query, (athlete_id, athlete_id, start_date, athlete_id, athlete_id))

        return {
            "athlete_info": athlete_info,
            "load_metrics": load_metrics,
            "load_chart_data": load_chart_data,  # Added for frontend charts
            "wellness_data": wellness_data,
            "wellness_trends": wellness_trends,
            "physical_evaluations": physical_evaluations,
            "risk_assessment": risk_data,
            "recent_sessions": recent_sessions
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")
    except HTTPException:
        # Re-raise HTTPExceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")



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
