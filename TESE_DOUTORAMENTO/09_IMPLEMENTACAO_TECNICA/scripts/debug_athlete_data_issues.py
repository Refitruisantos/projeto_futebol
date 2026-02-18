#!/usr/bin/env python3
"""Debug why load trends, wellness charts, and sessions are not showing properly"""

import requests
import json
from datetime import datetime, timedelta

print("🔍 Diagnosticando problemas de dados do atleta...")

# Test athlete ID 251
athlete_id = 251

print(f"\n1️⃣ Testando API de métricas para atleta {athlete_id}...")
try:
    # Test metrics API (for load trends)
    metrics_response = requests.get(f"http://localhost:8000/api/athletes/{athlete_id}/metrics?days=30")
    print(f"   Status: {metrics_response.status_code}")
    
    if metrics_response.status_code == 200:
        metrics_data = metrics_response.json()
        print(f"   ✅ Dados de métricas recebidos")
        
        # Check load chart data
        if 'load_chart_data' in metrics_data.get('data', {}):
            load_data = metrics_data['data']['load_chart_data']
            print(f"   📊 Load chart data: {len(load_data)} registros")
            if load_data:
                print(f"      Primeiro registro: {load_data[0]}")
        else:
            print("   ❌ Sem dados de load_chart_data")
            
        # Check wellness data in metrics
        if 'wellness_data' in metrics_data.get('data', {}):
            wellness_data = metrics_data['data']['wellness_data']
            print(f"   💚 Wellness data: {len(wellness_data)} registros")
        else:
            print("   ❌ Sem dados de wellness nas métricas")
            
    else:
        print(f"   ❌ Erro: {metrics_response.text}")
        
except Exception as e:
    print(f"   ❌ Exceção: {e}")

print(f"\n2️⃣ Testando API de perfil abrangente para atleta {athlete_id}...")
try:
    # Test comprehensive profile API
    profile_response = requests.get(f"http://localhost:8000/api/metrics/athletes/{athlete_id}/comprehensive-profile")
    print(f"   Status: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print(f"   ✅ Perfil abrangente recebido")
        
        # Check wellness data
        wellness_data = profile_data.get('wellness_data', [])
        print(f"   💚 Wellness data: {len(wellness_data)} registros")
        if wellness_data:
            latest = wellness_data[0]
            print(f"      Último registro: {latest.get('data')} - Score: {latest.get('wellness_score')}")
            
        # Check sessions
        sessions_data = profile_data.get('recent_sessions', [])
        print(f"   📅 Sessões: {len(sessions_data)} registros")
        if sessions_data:
            dates = [s.get('data') for s in sessions_data[:5]]
            print(f"      Datas das sessões: {dates}")
            
        # Check load metrics
        load_metrics = profile_data.get('load_metrics', [])
        print(f"   📊 Load metrics: {len(load_metrics)} registros")
        
    else:
        print(f"   ❌ Erro: {profile_response.text}")
        
except Exception as e:
    print(f"   ❌ Exceção: {e}")

print(f"\n3️⃣ Verificando dados de sessões na base de dados...")
try:
    import psycopg2
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Check sessions for athlete
    cursor.execute("""
        SELECT data, tipo, adversario, dificuldade_adversario
        FROM sessoes 
        WHERE id IN (
            SELECT DISTINCT sessao_id 
            FROM dados_gps 
            WHERE atleta_id = %s
        )
        ORDER BY data DESC
        LIMIT 10
    """, (athlete_id,))
    
    sessions = cursor.fetchall()
    print(f"   📅 Sessões na BD: {len(sessions)} registros")
    for session in sessions:
        print(f"      {session[0]} - {session[1]} - {session[2] or 'Sem adversário'}")
        
    # Check date range
    cursor.execute("""
        SELECT MIN(data) as min_date, MAX(data) as max_date, COUNT(*) as total
        FROM sessoes 
        WHERE id IN (
            SELECT DISTINCT sessao_id 
            FROM dados_gps 
            WHERE atleta_id = %s
        )
    """, (athlete_id,))
    
    date_range = cursor.fetchone()
    print(f"   📊 Intervalo de datas: {date_range[0]} a {date_range[1]} ({date_range[2]} sessões)")
    
    # Check wellness data
    cursor.execute("""
        SELECT COUNT(*), MIN(data), MAX(data)
        FROM dados_wellness 
        WHERE atleta_id = %s
    """, (athlete_id,))
    
    wellness_stats = cursor.fetchone()
    print(f"   💚 Wellness na BD: {wellness_stats[0]} registros ({wellness_stats[1]} a {wellness_stats[2]})")
    
    # Check load metrics
    cursor.execute("""
        SELECT COUNT(*), MIN(semana_inicio), MAX(semana_inicio)
        FROM metricas_carga 
        WHERE atleta_id = %s
    """, (athlete_id,))
    
    load_stats = cursor.fetchone()
    print(f"   📊 Métricas de carga na BD: {load_stats[0]} registros ({load_stats[1]} a {load_stats[2]})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Erro na BD: {e}")

print("\n🎯 Resumo dos problemas identificados:")
print("   • Verificar se as APIs estão retornando dados corretos")
print("   • Confirmar se o frontend está processando os dados adequadamente")
print("   • Expandir intervalo de datas para mostrar mais sessões")
print("   • Adicionar dados GPS completos (desacelerações, player load, etc.)")
