#!/usr/bin/env python3
"""Verify that backend fixes are applied and test the API"""

import requests
import time

print("🔍 Verificando se o backend foi reiniciado com as correções...")

# Test the API multiple times to see if it's fixed
for attempt in range(3):
    try:
        print(f"\n🌐 Tentativa {attempt + 1}/3...")
        response = requests.get("http://localhost:8000/api/metrics/athletes/255/comprehensive-profile", timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API funcionando corretamente!")
            
            # Check if we have the expected data
            wellness_count = len(data.get('wellness_data', []))
            load_count = len(data.get('load_chart_data', []))
            sessions_count = len(data.get('recent_sessions', []))
            
            print(f"   📊 Dados recebidos:")
            print(f"      • Wellness: {wellness_count} registros")
            print(f"      • Load chart: {load_count} registros")
            print(f"      • Sessões: {sessions_count} registros")
            
            if load_count > 0:
                print(f"      • Primeira semana: {data['load_chart_data'][0].get('week', 'N/A')}")
                print(f"      • Carga aguda: {data['load_chart_data'][0].get('acute_load', 'N/A')}")
            
            break
            
        elif response.status_code == 500:
            error_text = response.text
            if "carga_total" in error_text:
                print("   ❌ Backend ainda não foi reiniciado - usando código antigo")
                print("   🔄 REINICIE O BACKEND para aplicar as correções")
            else:
                print(f"   ❌ Novo erro 500: {error_text[:200]}")
        else:
            print(f"   ❌ Status inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Backend não está rodando")
        break
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    if attempt < 2:
        print("   ⏳ Aguardando 2 segundos...")
        time.sleep(2)

print("\n🎯 Instruções:")
print("1. PARE o backend atual (Ctrl+C no terminal)")
print("2. REINICIE com: python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
print("3. Aguarde a mensagem 'Application startup complete'")
print("4. Recarregue a página do atleta no navegador")
print("\n✅ Após o reinício, todos os dados devem aparecer corretamente!")
