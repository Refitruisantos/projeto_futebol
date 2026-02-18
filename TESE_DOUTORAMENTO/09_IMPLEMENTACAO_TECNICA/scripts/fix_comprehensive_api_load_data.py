#!/usr/bin/env python3
"""Fix comprehensive API to include load chart data and expand session range"""

import os

# Read the metrics.py file
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Corrigindo API de perfil abrangente...")

# Find the comprehensive profile function
start_marker = "def get_comprehensive_athlete_profile"
end_marker = "return {"

start_pos = content.find(start_marker)
if start_pos == -1:
    print("❌ Função não encontrada")
    exit()

# Find the return statement
return_pos = content.find(end_marker, start_pos)
if return_pos == -1:
    print("❌ Return statement não encontrado")
    exit()

# Find the end of the return statement
return_end = content.find("}", return_pos)
brace_count = 1
i = return_end + 1
while i < len(content) and brace_count > 0:
    if content[i] == '{':
        brace_count += 1
    elif content[i] == '}':
        brace_count -= 1
    i += 1

function_end = i

# Extract the function
function_content = content[start_pos:function_end]

print("📊 Adicionando dados de carga e expandindo intervalo de sessões...")

# Replace the function with enhanced version
new_function = '''def get_comprehensive_athlete_profile(
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
                carga_total,
                carga_aguda,
                carga_cronica,
                ratio_ac,
                monotonia,
                strain,
                freshness_index,
                risco_lesao
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
                'ac_ratio': float(metric['ratio_ac']) if metric['ratio_ac'] else 0,
                'monotony': float(metric['monotonia']) if metric['monotonia'] else 0,
                'strain': float(metric['strain']) if metric['strain'] else 0
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
                AVG(dp.rpe) as avg_pse_load,
                COUNT(DISTINCT dp.atleta_id) as pse_records,
                COUNT(DISTINCT dg.atleta_id) as gps_records
            FROM sessoes s
            LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
            LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
            WHERE s.data >= %s
            AND (dg.atleta_id = %s OR dp.atleta_id = %s)
            GROUP BY s.id, s.data, s.tipo, s.adversario, s.dificuldade_adversario, s.jornada, s.resultado
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
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")'''

# Replace the function in the content
content = content[:start_pos] + new_function + content[function_end:]

# Write the updated content back
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ API de perfil abrangente corrigida:")
print("   • Intervalo de sessões expandido para 90 dias (50 sessões)")
print("   • Dados de carga formatados para gráficos")
print("   • Dados GPS completos incluídos (desacelerações, player load, etc.)")
print("   • Dados de wellness expandidos para 30 registros")
print("\n🔄 Reinicie o backend para aplicar as alterações")
