#!/usr/bin/env python3
"""Test chart data fixes"""

import requests
import json

print("🧪 Testing chart data fixes...")

# Test the dashboard API for chart data
print("\n1️⃣ Testing dashboard API chart data...")
try:
    response = requests.get("http://localhost:8000/api/metrics/team/dashboard")
    
    if response.status_code == 200:
        data = response.json()
        
        # Test Top Athletes Chart data
        top_athletes = data.get('top_load_athletes', [])
        print(f"   📊 Top Athletes Chart Data ({len(top_athletes)} athletes):")
        
        if len(top_athletes) > 0:
            for i, athlete in enumerate(top_athletes[:3]):
                nome = athlete.get('nome_completo', 'N/A')
                weekly_load = athlete.get('weekly_load', 0)
                print(f"     {i+1}. {nome.split(' ')[0]}: {weekly_load:.0f} AU")
                
            print("   ✅ Top Athletes Chart should now show bars with values")
        else:
            print("   ❌ No top athletes data")
        
        # Test Distance Chart data
        athletes_overview = data.get('athletes_overview', [])
        distance_athletes = [a for a in athletes_overview if a.get('distancia_total_media', 0) > 0]
        distance_athletes.sort(key=lambda x: x.get('distancia_total_media', 0), reverse=True)
        
        print(f"\n   🏃 Distance Chart Data ({len(distance_athletes)} athletes with GPS):")
        
        if len(distance_athletes) > 0:
            for i, athlete in enumerate(distance_athletes[:5]):
                nome = athlete.get('nome_completo', 'N/A')
                distance = athlete.get('distancia_total_media', 0)
                print(f"     {i+1}. {nome.split(' ')[0]}: {distance:.0f}m")
                
            print("   ✅ Distance Chart should now show athlete names and distances")
        else:
            print("   ❌ No GPS distance data")
        
        # Test Speed Chart data
        speed_athletes = [a for a in athletes_overview if a.get('velocidade_max_media', 0) > 0]
        speed_athletes.sort(key=lambda x: x.get('velocidade_max_media', 0), reverse=True)
        
        print(f"\n   🏃‍♂️ Speed Chart Data ({len(speed_athletes)} athletes with speed):")
        
        if len(speed_athletes) > 0:
            for i, athlete in enumerate(speed_athletes[:5]):
                nome = athlete.get('nome_completo', 'N/A')
                speed = athlete.get('velocidade_max_media', 0)
                print(f"     {i+1}. {nome.split(' ')[0]}: {speed:.1f} km/h")
                
            print("   ✅ Speed Chart should now show athlete names and speeds")
        else:
            print("   ❌ No speed data")
        
        # Test Position Distribution
        positions = {}
        for athlete in athletes_overview:
            pos = athlete.get('posicao', 'N/A')
            positions[pos] = positions.get(pos, 0) + 1
            
        print(f"\n   📊 Position Distribution ({len(positions)} positions):")
        for pos, count in positions.items():
            percentage = (count / len(athletes_overview)) * 100
            print(f"     {pos}: {count} athletes ({percentage:.0f}%)")
            
        print("   ✅ Position Chart should show proper distribution")
        
    else:
        print(f"   ❌ API Error: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Connection Error: {e}")

print("\n2️⃣ Expected chart improvements:")
print("   ✅ Top 5 - Carga:")
print("     - Shows bars with actual load values (5165, 5045, 5025 AU)")
print("     - Displays athlete first names (Luís, Rafael, Bruno)")
print("")
print("   ✅ Top 10 - Distância Média:")
print("     - Shows athlete names instead of 'N/A'")
print("     - Displays actual distance values in meters")
print("     - Horizontal bar chart with proper data")
print("")
print("   ✅ Top 10 - Velocidade Máxima:")
print("     - Shows athlete names and speed values")
print("     - Line chart with actual km/h values")
print("     - No more 'Sem dados de velocidade'")
print("")
print("   ✅ Distribuição por Posição:")
print("     - Pie chart with proper percentages")
print("     - Position labels (MC, AV, DL, etc.)")

print("\n🔄 Next steps:")
print("   1. Refresh dashboard page")
print("   2. Navigate to 'Gráficos' tab")
print("   3. Verify all charts show proper data")
print("   4. Charts should be informative and explicit")
