#!/usr/bin/env python3
"""Test what the dashboard endpoint actually returns"""

import requests
import json

response = requests.get("http://localhost:8000/api/metrics/team/dashboard")
data = response.json()

print("📊 DASHBOARD ENDPOINT RESPONSE")
print("="*50)
print(f"\nStatus: {response.status_code}")
print(f"\nTop-level keys: {list(data.keys())}\n")

# Check athletes overview
if 'athletes_overview' in data:
    overview = data['athletes_overview']
    print(f"Athletes Overview:")
    print(f"  Total athletes: {len(overview)}")
    if overview:
        print(f"\n  First athlete sample:")
        athlete = overview[0]
        for key, value in athlete.items():
            print(f"    {key}: {value}")

# Check top load athletes
if 'top_load_athletes' in data:
    top_load = data['top_load_athletes']
    print(f"\n\nTop Load Athletes: {len(top_load)}")
    if top_load:
        print("  Sample:")
        for athlete in top_load[:3]:
            nome = athlete.get('nome_completo', 'N/A')
            numero = athlete.get('numero_camisola', 'N/A')
            load = athlete.get('carga_total_semanal', 'N/A')
            print(f"    AU {numero} | {nome} | Load: {load}")

# Check at risk athletes
if 'at_risk_athletes' in data:
    at_risk = data['at_risk_athletes']
    print(f"\n\nAt Risk Athletes: {len(at_risk)}")
    if at_risk:
        print("  Sample:")
        for athlete in at_risk[:3]:
            nome = athlete.get('nome_completo', 'N/A')
            numero = athlete.get('numero_camisola', 'N/A')
            posicao = athlete.get('posicao', 'N/A')
            print(f"    AU {numero} | {nome} | {posicao}")

# Check risk summary
if 'risk_summary' in data:
    print(f"\n\nRisk Summary:")
    for key, value in data['risk_summary'].items():
        print(f"  {key}: {value}")

# Check week analyzed
if 'week_analyzed' in data:
    print(f"\n\nWeek Analyzed: {data['week_analyzed']}")

# Check team context
if 'team_context' in data:
    print(f"\n\nTeam Context:")
    for key, value in data['team_context'].items():
        print(f"  {key}: {value}")

print("\n" + "="*50)
