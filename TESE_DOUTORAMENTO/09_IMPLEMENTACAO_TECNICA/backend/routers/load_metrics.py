"""
Load Metrics Router
API endpoints for advanced training load metrics (Monotony, Strain, ACWR, Z-Scores)
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, date
from database import get_db, DatabaseConnection

router = APIRouter(prefix="/api/load-metrics", tags=["Load Metrics"])


@router.get("/athlete/{athlete_id}")
async def get_athlete_metrics(
    athlete_id: int,
    weeks: Optional[int] = Query(None, description="Number of recent weeks to return"),
    db: DatabaseConnection = Depends(get_db)
):
    """
    Get weekly load metrics for a specific athlete
    
    Returns:
    - Weekly load, monotony, strain, ACWR
    - Risk levels for each metric
    - Z-scores (standardized vs team)
    """
    
    # Build query
    query = """
        SELECT 
            mc.id,
            mc.semana_inicio,
            mc.semana_fim,
            mc.carga_total_semanal,
            mc.media_carga,
            mc.desvio_padrao,
            mc.dias_treino,
            mc.monotonia,
            mc.tensao,
            mc.variacao_percentual,
            mc.carga_aguda,
            mc.carga_cronica,
            mc.acwr,
            mc.z_score_carga,
            mc.z_score_monotonia,
            mc.z_score_tensao,
            mc.z_score_acwr,
            mc.nivel_risco_monotonia,
            mc.nivel_risco_tensao,
            mc.nivel_risco_acwr,
            a.nome_completo,
            a.posicao
        FROM metricas_carga mc
        JOIN atletas a ON a.id = mc.atleta_id
        WHERE mc.atleta_id = %s
        ORDER BY mc.semana_inicio DESC
    """
    
    params = [athlete_id]
    
    if weeks:
        query += " LIMIT %s"
        params.append(weeks)
    
    try:
        results = db.query_to_dict(query, tuple(params))
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No metrics found for athlete {athlete_id}")
        
        # Format response
        athlete_info = {
            "athlete_id": athlete_id,
            "name": results[0]['nome_completo'],
            "position": results[0]['posicao']
        }
        
        weeks_data = []
        for row in results:
            weeks_data.append({
                "week_start": row['semana_inicio'].isoformat() if row['semana_inicio'] else None,
                "week_end": row['semana_fim'].isoformat() if row['semana_fim'] else None,
                "load": {
                    "total": float(row['carga_total_semanal']) if row['carga_total_semanal'] else None,
                    "average": float(row['media_carga']) if row['media_carga'] else None,
                    "std_dev": float(row['desvio_padrao']) if row['desvio_padrao'] else None,
                    "training_days": row['dias_treino']
                },
                "monotony": {
                    "value": float(row['monotonia']) if row['monotonia'] else None,
                    "risk_level": row['nivel_risco_monotonia'],
                    "z_score": float(row['z_score_monotonia']) if row['z_score_monotonia'] else None
                },
                "strain": {
                    "value": float(row['tensao']) if row['tensao'] else None,
                    "risk_level": row['nivel_risco_tensao'],
                    "z_score": float(row['z_score_tensao']) if row['z_score_tensao'] else None
                },
                "acwr": {
                    "value": float(row['acwr']) if row['acwr'] else None,
                    "acute_load": float(row['carga_aguda']) if row['carga_aguda'] else None,
                    "chronic_load": float(row['carga_cronica']) if row['carga_cronica'] else None,
                    "risk_level": row['nivel_risco_acwr'],
                    "z_score": float(row['z_score_acwr']) if row['z_score_acwr'] else None
                },
                "variation_pct": float(row['variacao_percentual']) if row['variacao_percentual'] else None
            })
        
        return {
            "athlete": athlete_info,
            "weeks": weeks_data,
            "total_weeks": len(weeks_data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team/overview")
async def get_team_overview(
    week_start: Optional[date] = Query(None, description="Specific week to analyze (defaults to most recent)"),
    db: DatabaseConnection = Depends(get_db)
):
    """
    Get team-wide load metrics overview
    
    Returns all athletes' metrics for a specific week with risk indicators
    """
    
    # Get the week to analyze
    if week_start:
        week_filter = "mc.semana_inicio = %s"
        params = (week_start,)
    else:
        # Get most recent week
        week_filter = "mc.semana_inicio = (SELECT MAX(semana_inicio) FROM metricas_carga)"
        params = ()
    
    query = f"""
        SELECT 
            a.id as athlete_id,
            a.nome_completo as name,
            a.posicao as position,
            mc.semana_inicio,
            mc.carga_total_semanal,
            mc.monotonia,
            mc.tensao,
            mc.acwr,
            mc.z_score_carga,
            mc.z_score_monotonia,
            mc.z_score_tensao,
            mc.z_score_acwr,
            mc.nivel_risco_monotonia,
            mc.nivel_risco_tensao,
            mc.nivel_risco_acwr
        FROM metricas_carga mc
        JOIN atletas a ON a.id = mc.atleta_id
        WHERE {week_filter}
        ORDER BY 
            CASE 
                WHEN mc.nivel_risco_monotonia = 'red' OR 
                     mc.nivel_risco_tensao = 'red' OR 
                     mc.nivel_risco_acwr = 'red' THEN 1
                WHEN mc.nivel_risco_monotonia = 'yellow' OR 
                     mc.nivel_risco_tensao = 'yellow' OR 
                     mc.nivel_risco_acwr = 'yellow' THEN 2
                ELSE 3
            END,
            a.nome_completo
    """
    
    try:
        results = db.query_to_dict(query, params)
        
        if not results:
            raise HTTPException(status_code=404, detail="No metrics found for the specified week")
        
        week = results[0]['semana_inicio'].isoformat() if results[0]['semana_inicio'] else None
        
        athletes = []
        risk_counts = {"green": 0, "yellow": 0, "red": 0, "unknown": 0}
        
        for row in results:
            # Determine overall risk level (worst of the three metrics)
            risks = [row['nivel_risco_monotonia'], row['nivel_risco_tensao'], row['nivel_risco_acwr']]
            if 'red' in risks:
                overall_risk = 'red'
                risk_counts['red'] += 1
            elif 'yellow' in risks:
                overall_risk = 'yellow'
                risk_counts['yellow'] += 1
            elif 'green' in risks:
                overall_risk = 'green'
                risk_counts['green'] += 1
            else:
                overall_risk = 'unknown'
                risk_counts['unknown'] += 1
            
            athletes.append({
                "athlete_id": row['athlete_id'],
                "name": row['name'],
                "position": row['position'],
                "load": float(row['carga_total_semanal']) if row['carga_total_semanal'] else None,
                "monotony": {
                    "value": float(row['monotonia']) if row['monotonia'] else None,
                    "risk": row['nivel_risco_monotonia'],
                    "z_score": float(row['z_score_monotonia']) if row['z_score_monotonia'] else None
                },
                "strain": {
                    "value": float(row['tensao']) if row['tensao'] else None,
                    "risk": row['nivel_risco_tensao'],
                    "z_score": float(row['z_score_tensao']) if row['z_score_tensao'] else None
                },
                "acwr": {
                    "value": float(row['acwr']) if row['acwr'] else None,
                    "risk": row['nivel_risco_acwr'],
                    "z_score": float(row['z_score_acwr']) if row['z_score_acwr'] else None
                },
                "overall_risk": overall_risk
            })
        
        return {
            "week": week,
            "athletes": athletes,
            "total_athletes": len(athletes),
            "risk_distribution": risk_counts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team/by-position")
async def get_metrics_by_position(
    week_start: Optional[date] = Query(None, description="Specific week (defaults to most recent)"),
    db: DatabaseConnection = Depends(get_db)
):
    """
    Get average metrics grouped by position
    
    Returns team averages for each position (GR, DC, DL, MC, EX, AV)
    """
    
    if week_start:
        week_filter = "mc.semana_inicio = %s"
        params = (week_start,)
    else:
        week_filter = "mc.semana_inicio = (SELECT MAX(semana_inicio) FROM metricas_carga)"
        params = ()
    
    query = f"""
        SELECT 
            a.posicao,
            COUNT(*) as athlete_count,
            AVG(mc.carga_total_semanal) as avg_load,
            AVG(mc.monotonia) as avg_monotony,
            AVG(mc.tensao) as avg_strain,
            AVG(mc.acwr) as avg_acwr,
            STDDEV(mc.carga_total_semanal) as std_load,
            STDDEV(mc.monotonia) as std_monotony,
            STDDEV(mc.tensao) as std_strain,
            STDDEV(mc.acwr) as std_acwr,
            mc.semana_inicio
        FROM metricas_carga mc
        JOIN atletas a ON a.id = mc.atleta_id
        WHERE {week_filter}
        GROUP BY a.posicao, mc.semana_inicio
        ORDER BY a.posicao
    """
    
    try:
        results = db.query_to_dict(query, params)
        
        if not results:
            raise HTTPException(status_code=404, detail="No metrics found")
        
        week = results[0]['semana_inicio'].isoformat() if results[0]['semana_inicio'] else None
        
        positions = {}
        for row in results:
            positions[row['posicao']] = {
                "position": row['posicao'],
                "athlete_count": row['athlete_count'],
                "load": {
                    "average": round(float(row['avg_load']), 2) if row['avg_load'] else None,
                    "std_dev": round(float(row['std_load']), 2) if row['std_load'] else None
                },
                "monotony": {
                    "average": round(float(row['avg_monotony']), 2) if row['avg_monotony'] else None,
                    "std_dev": round(float(row['std_monotony']), 2) if row['std_monotony'] else None
                },
                "strain": {
                    "average": round(float(row['avg_strain']), 2) if row['avg_strain'] else None,
                    "std_dev": round(float(row['std_strain']), 2) if row['std_strain'] else None
                },
                "acwr": {
                    "average": round(float(row['avg_acwr']), 2) if row['avg_acwr'] else None,
                    "std_dev": round(float(row['std_acwr']), 2) if row['std_acwr'] else None
                }
            }
        
        return {
            "week": week,
            "positions": positions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_team_trends(
    weeks: int = Query(5, description="Number of recent weeks to analyze"),
    db: DatabaseConnection = Depends(get_db)
):
    """
    Get team-wide trends over time
    
    Returns weekly averages for the entire team
    """
    
    query = """
        SELECT 
            mc.semana_inicio,
            COUNT(*) as athlete_count,
            AVG(mc.carga_total_semanal) as avg_load,
            AVG(mc.monotonia) as avg_monotony,
            AVG(mc.tensao) as avg_strain,
            AVG(mc.acwr) as avg_acwr,
            SUM(CASE WHEN mc.nivel_risco_monotonia = 'red' THEN 1 ELSE 0 END) as monotony_red_count,
            SUM(CASE WHEN mc.nivel_risco_tensao = 'red' THEN 1 ELSE 0 END) as strain_red_count,
            SUM(CASE WHEN mc.nivel_risco_acwr = 'red' THEN 1 ELSE 0 END) as acwr_red_count
        FROM metricas_carga mc
        GROUP BY mc.semana_inicio
        ORDER BY mc.semana_inicio DESC
        LIMIT %s
    """
    
    try:
        results = db.query_to_dict(query, (weeks,))
        
        trends = []
        for row in results:
            trends.append({
                "week": row['semana_inicio'].isoformat() if row['semana_inicio'] else None,
                "athlete_count": row['athlete_count'],
                "averages": {
                    "load": round(float(row['avg_load']), 2) if row['avg_load'] else None,
                    "monotony": round(float(row['avg_monotony']), 2) if row['avg_monotony'] else None,
                    "strain": round(float(row['avg_strain']), 2) if row['avg_strain'] else None,
                    "acwr": round(float(row['avg_acwr']), 2) if row['avg_acwr'] else None
                },
                "at_risk": {
                    "monotony": row['monotony_red_count'],
                    "strain": row['strain_red_count'],
                    "acwr": row['acwr_red_count']
                }
            })
        
        # Reverse to show chronological order
        trends.reverse()
        
        return {
            "weeks_analyzed": len(trends),
            "trends": trends
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/athlete/{athlete_id}/week/{week_start}/details")
async def get_calculation_details(
    athlete_id: int,
    week_start: date,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Get detailed calculation breakdown for a specific athlete and week
    
    Returns all the raw data used in metric calculations:
    - Daily workout loads for the week
    - Last 7 workouts for monotony calculation
    - 7-day and 28-day loads for ACWR
    - Team averages for Z-score calculation
    """
    
    try:
        # Get the metric record for this athlete/week
        metric_query = """
            SELECT 
                mc.*,
                a.nome_completo,
                a.posicao
            FROM metricas_carga mc
            JOIN atletas a ON a.id = mc.atleta_id
            WHERE mc.atleta_id = %s AND mc.semana_inicio = %s
        """
        
        metric_result = db.query_to_dict(metric_query, (athlete_id, week_start))
        
        if not metric_result:
            raise HTTPException(status_code=404, detail="No metrics found for this athlete/week")
        
        metric = metric_result[0]
        week_end = metric['semana_fim']
        
        # Get daily workout loads for this week
        daily_loads_query = """
            SELECT 
                DATE(time) as data,
                carga_total
            FROM dados_pse
            WHERE atleta_id = %s 
            AND DATE(time) BETWEEN %s AND %s
            ORDER BY time
        """
        
        daily_loads = db.query_to_dict(daily_loads_query, (athlete_id, week_start, week_end))
        
        # Get all workouts chronologically to find last 7 for monotony
        all_workouts_query = """
            SELECT 
                DATE(time) as data,
                carga_total
            FROM dados_pse
            WHERE atleta_id = %s 
            AND DATE(time) <= %s
            ORDER BY time
        """
        
        all_workouts = db.query_to_dict(all_workouts_query, (athlete_id, week_end))
        last_7_workouts = all_workouts[-7:] if len(all_workouts) >= 7 else all_workouts
        
        # Get team averages for Z-score context
        team_avg_query = """
            SELECT 
                AVG(carga_total_semanal) as avg_load,
                AVG(monotonia) as avg_monotony,
                AVG(tensao) as avg_strain,
                AVG(acwr) as avg_acwr,
                STDDEV(carga_total_semanal) as std_load,
                STDDEV(monotonia) as std_monotony,
                STDDEV(tensao) as std_strain,
                STDDEV(acwr) as std_acwr
            FROM metricas_carga
            WHERE semana_inicio = %s
        """
        
        team_avg = db.query_to_dict(team_avg_query, (week_start,))
        
        return {
            "athlete": {
                "id": athlete_id,
                "name": metric['nome_completo'],
                "position": metric['posicao']
            },
            "week": {
                "start": metric['semana_inicio'].isoformat(),
                "end": metric['semana_fim'].isoformat()
            },
            "calculated_metrics": {
                "load": float(metric['carga_total_semanal']) if metric['carga_total_semanal'] else None,
                "monotony": float(metric['monotonia']) if metric['monotonia'] else None,
                "strain": float(metric['tensao']) if metric['tensao'] else None,
                "acwr": float(metric['acwr']) if metric['acwr'] else None,
                "acute_load": float(metric['carga_aguda']) if metric['carga_aguda'] else None,
                "chronic_load": float(metric['carga_cronica']) if metric['carga_cronica'] else None
            },
            "calculation_data": {
                "daily_loads_this_week": [
                    {
                        "date": row['data'].isoformat(),
                        "load": float(row['carga_total'])
                    } for row in daily_loads
                ],
                "last_7_workouts_for_monotony": [
                    {
                        "date": row['data'].isoformat(),
                        "load": float(row['carga_total'])
                    } for row in last_7_workouts
                ],
                "monotony_calculation": {
                    "workout_loads": [float(row['carga_total']) for row in last_7_workouts],
                    "mean": float(metric['media_carga']) if metric['media_carga'] else None,
                    "std_dev": float(metric['desvio_padrao']) if metric['desvio_padrao'] else None,
                    "formula": "mean / std_dev",
                    "result": float(metric['monotonia']) if metric['monotonia'] else None
                },
                "strain_calculation": {
                    "weekly_load": float(metric['carga_total_semanal']) if metric['carga_total_semanal'] else None,
                    "monotony": float(metric['monotonia']) if metric['monotonia'] else None,
                    "formula": "weekly_load * monotony",
                    "result": float(metric['tensao']) if metric['tensao'] else None
                },
                "acwr_calculation": {
                    "acute_load_7_days": float(metric['carga_aguda']) if metric['carga_aguda'] else None,
                    "chronic_load_28_days": float(metric['carga_cronica']) if metric['carga_cronica'] else None,
                    "formula": "acute_load / chronic_load",
                    "result": float(metric['acwr']) if metric['acwr'] else None
                }
            },
            "team_context": {
                "averages": {
                    "load": round(float(team_avg[0]['avg_load']), 2) if team_avg[0]['avg_load'] else None,
                    "monotony": round(float(team_avg[0]['avg_monotony']), 2) if team_avg[0]['avg_monotony'] else None,
                    "strain": round(float(team_avg[0]['avg_strain']), 2) if team_avg[0]['avg_strain'] else None,
                    "acwr": round(float(team_avg[0]['avg_acwr']), 2) if team_avg[0]['avg_acwr'] else None
                },
                "std_deviations": {
                    "load": round(float(team_avg[0]['std_load']), 2) if team_avg[0]['std_load'] else None,
                    "monotony": round(float(team_avg[0]['std_monotony']), 2) if team_avg[0]['std_monotony'] else None,
                    "strain": round(float(team_avg[0]['std_strain']), 2) if team_avg[0]['std_strain'] else None,
                    "acwr": round(float(team_avg[0]['std_acwr']), 2) if team_avg[0]['std_acwr'] else None
                }
            },
            "risk_levels": {
                "monotony": metric['nivel_risco_monotonia'],
                "strain": metric['nivel_risco_tensao'],
                "acwr": metric['nivel_risco_acwr']
            },
            "z_scores": {
                "load": float(metric['z_score_carga']) if metric['z_score_carga'] else None,
                "monotony": float(metric['z_score_monotonia']) if metric['z_score_monotonia'] else None,
                "strain": float(metric['z_score_tensao']) if metric['z_score_tensao'] else None,
                "acwr": float(metric['z_score_acwr']) if metric['z_score_acwr'] else None
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weeks")
async def get_available_weeks(db: DatabaseConnection = Depends(get_db)):
    """
    Get list of all available weeks with metrics data
    
    Returns weeks in descending order (most recent first)
    """
    
    query = """
        SELECT DISTINCT 
            semana_inicio,
            semana_fim,
            COUNT(DISTINCT atleta_id) as athlete_count
        FROM metricas_carga
        GROUP BY semana_inicio, semana_fim
        ORDER BY semana_inicio DESC
    """
    
    try:
        results = db.query_to_dict(query)
        
        weeks = []
        for row in results:
            weeks.append({
                "week_start": row['semana_inicio'].isoformat() if row['semana_inicio'] else None,
                "week_end": row['semana_fim'].isoformat() if row['semana_fim'] else None,
                "athlete_count": row['athlete_count'],
                "label": f"Semana {row['semana_inicio'].strftime('%d/%m/%Y')}" if row['semana_inicio'] else "Unknown"
            })
        
        return {
            "total_weeks": len(weeks),
            "weeks": weeks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thresholds")
async def get_risk_thresholds():
    """
    Get the risk threshold values for each metric
    
    Useful for frontend visualization (color zones, gauge charts, etc.)
    """
    return {
        "monotony": {
            "green": {"max": 1.0, "description": "Good load variation"},
            "yellow": {"min": 1.0, "max": 2.0, "description": "Moderate variation - monitor"},
            "red": {"min": 2.0, "description": "Low variation - high injury risk"}
        },
        "strain": {
            "green": {"max": 4000, "description": "Low strain"},
            "yellow": {"min": 4000, "max": 6000, "description": "Moderate strain"},
            "red": {"min": 6000, "description": "High strain - care needed"}
        },
        "acwr": {
            "red_low": {"max": 0.8, "description": "Detraining risk"},
            "green": {"min": 0.8, "max": 1.3, "description": "Sweet spot - optimal"},
            "yellow": {"min": 1.3, "max": 1.5, "description": "Elevated - monitor"},
            "red_high": {"min": 1.5, "description": "Overtraining risk"}
        },
        "z_score": {
            "green": {"min": -1.0, "max": 1.0, "description": "Within team normality"},
            "yellow": {"ranges": [[-2.0, -1.0], [1.0, 2.0]], "description": "Outside normal range"},
            "red": {"ranges": [[-999, -2.0], [2.0, 999]], "description": "Far outside normal range"}
        }
    }
