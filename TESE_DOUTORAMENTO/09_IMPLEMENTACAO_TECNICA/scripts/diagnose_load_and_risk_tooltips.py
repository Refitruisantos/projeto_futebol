#!/usr/bin/env python3
"""Diagnose load values and risk tooltip issues"""

import requests
import psycopg2

print("🔍 Diagnosing load values and risk tooltip issues...")

# 1. Check dashboard API response for load data
print("\n1️⃣ Checking dashboard API load data...")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check top_load_athletes
        top_athletes = data.get('top_load_athletes', [])
        print(f"   Found {len(top_athletes)} top load athletes")
        
        if len(top_athletes) > 0:
            print("   Top athletes load data:")
            for i, athlete in enumerate(top_athletes[:3]):
                print(f"     {i+1}. {athlete.get('nome_completo', 'N/A')}")
                print(f"        weekly_load: {athlete.get('weekly_load')}")
                print(f"        load_7d: {athlete.get('load_7d')}")
                print(f"        carga_total_semanal: {athlete.get('carga_total_semanal')}")
        else:
            print("   ❌ No top load athletes found")
            
        # Check at_risk_athletes for tooltip data
        at_risk = data.get('at_risk_athletes', [])
        print(f"\n   Found {len(at_risk)} at-risk athletes")
        
        if len(at_risk) > 0:
            print("   At-risk athletes data:")
            for athlete in at_risk[:2]:
                print(f"     - {athlete.get('nome', 'N/A')} ({athlete.get('posicao', 'N/A')})")
                print(f"       classificacao: {athlete.get('classificacao')}")
                # Check if we have risk explanation data
                risk_fields = ['risk_monotony', 'risk_strain', 'risk_acwr', 'monotony', 'strain', 'acwr']
                for field in risk_fields:
                    if field in athlete:
                        print(f"       {field}: {athlete.get(field)}")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

# 2. Check database for load metrics
print("\n2️⃣ Checking database for load metrics...")
try:
    conn = psycopg2.connect(
        host='localhost', port='5433', database='futebol_tese',
        user='postgres', password='desporto.20'
    )
    cursor = conn.cursor()
    
    # Check metricas_carga table
    cursor.execute("""
        SELECT 
            a.nome_completo,
            mc.carga_total_semanal,
            mc.monotonia,
            mc.tensao,
            mc.acwr,
            mc.nivel_risco_monotonia,
            mc.nivel_risco_tensao,
            mc.nivel_risco_acwr
        FROM metricas_carga mc
        JOIN atletas a ON mc.atleta_id = a.id
        WHERE a.ativo = TRUE
        ORDER BY mc.carga_total_semanal DESC NULLS LAST
        LIMIT 5
    """)
    
    load_results = cursor.fetchall()
    print(f"   Found {len(load_results)} athletes with load data:")
    
    for nome, carga, monotonia, tensao, acwr, risk_mono, risk_tensao, risk_acwr in load_results:
        print(f"     - {nome}: {carga} AU")
        print(f"       Monotonia: {monotonia} ({risk_mono})")
        print(f"       Tensão: {tensao} ({risk_tensao})")
        print(f"       ACWR: {acwr} ({risk_acwr})")
    
    # Check risk_assessment table for detailed explanations
    cursor.execute("""
        SELECT 
            a.nome_completo,
            r.injury_risk_category,
            r.acwr_risk_score,
            r.monotony_risk_score,
            r.strain_risk_score,
            r.wellness_risk_score,
            r.fatigue_accumulation_score
        FROM risk_assessment r
        JOIN atletas a ON r.atleta_id = a.id
        WHERE r.injury_risk_category IN ('Alto', 'very_high')
        AND a.ativo = TRUE
        LIMIT 3
    """)
    
    risk_results = cursor.fetchall()
    print(f"\n   Found {len(risk_results)} high-risk athletes with detailed scores:")
    
    for nome, category, acwr_score, mono_score, strain_score, wellness_score, fatigue_score in risk_results:
        print(f"     - {nome} ({category}):")
        print(f"       ACWR Risk: {acwr_score}")
        print(f"       Monotony Risk: {mono_score}")
        print(f"       Strain Risk: {strain_score}")
        print(f"       Wellness Risk: {wellness_score}")
        print(f"       Fatigue Score: {fatigue_score}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database Error: {e}")

print("\n3️⃣ Issues Identified:")
print("   1. Load values (AU) may not be properly mapped in frontend")
print("   2. Risk tooltips need detailed explanation with specific factors")
print("   3. Backend may need to include more risk detail in API response")

print("\n🔧 Next steps:")
print("   1. Fix load value mapping in dashboard API")
print("   2. Add detailed risk explanations to at-risk athletes")
print("   3. Update frontend to show hover tooltips with risk factors")
