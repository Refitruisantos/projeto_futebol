#!/usr/bin/env python3
"""Test load values and risk tooltip fixes"""

import requests
import json

print("🧪 Testing load values and risk tooltip fixes...")

# Test the team dashboard endpoint
print("\n1️⃣ Testing dashboard API with fixes...")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check top_load_athletes
        top_athletes = data.get('top_load_athletes', [])
        print(f"   ✅ Found {len(top_athletes)} top load athletes")
        
        if len(top_athletes) > 0:
            print("   📊 Top athletes with load values:")
            for i, athlete in enumerate(top_athletes[:3]):
                weekly_load = athlete.get('weekly_load', 0)
                print(f"     {i+1}. {athlete.get('nome_completo', 'N/A')}: {weekly_load:.0f} AU")
                
            if all(athlete.get('weekly_load', 0) > 0 for athlete in top_athletes):
                print("   ✅ All top athletes have proper load values")
            else:
                print("   ❌ Some athletes still have 0 load values")
        
        # Check at_risk_athletes with detailed explanations
        at_risk = data.get('at_risk_athletes', [])
        print(f"\n   ✅ Found {len(at_risk)} at-risk athletes")
        
        if len(at_risk) > 0:
            print("   🚨 At-risk athletes with explanations:")
            for athlete in at_risk[:2]:
                print(f"     - {athlete.get('nome', 'N/A')} ({athlete.get('posicao', 'N/A')})")
                print(f"       Classificação: {athlete.get('classificacao')}")
                
                # Check if risk explanation exists
                explanation = athlete.get('risk_explanation', '')
                if explanation:
                    print(f"       ✅ Has risk explanation: {explanation[:50]}...")
                    
                    # Check individual scores
                    scores = []
                    if athlete.get('acwr_risk_score'):
                        scores.append(f"ACWR: {athlete.get('acwr_risk_score'):.1f}")
                    if athlete.get('monotony_risk_score'):
                        scores.append(f"Monotonia: {athlete.get('monotony_risk_score'):.1f}")
                    if athlete.get('strain_risk_score'):
                        scores.append(f"Tensão: {athlete.get('strain_risk_score'):.1f}")
                    
                    if scores:
                        print(f"       📊 Scores: {', '.join(scores)}")
                else:
                    print("       ❌ No risk explanation")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

print("\n2️⃣ Expected frontend behavior after fixes:")
print("   ✅ Top 5 - Carga de Treino:")
print("     - Should show actual AU values (5165, 5045, 5025, etc.)")
print("     - Instead of 0 AU for all athletes")
print("")
print("   ✅ Atletas em Risco hover tooltips:")
print("     - Hover over athlete names to see detailed risk factors")
print("     - Shows specific scores (ACWR, Monotonia, Tensão)")
print("     - Explains why each athlete is at risk")
print("     - Includes recommended actions")

print("\n🔄 Next steps:")
print("   1. Restart backend to apply API changes")
print("   2. Refresh dashboard page")
print("   3. Verify load values show correctly")
print("   4. Test hover tooltips on at-risk athletes")
