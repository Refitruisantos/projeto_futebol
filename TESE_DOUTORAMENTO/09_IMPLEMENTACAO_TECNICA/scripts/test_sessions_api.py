#!/usr/bin/env python3
"""Test the sessions API endpoint"""

import requests
import json

print("🔍 Testing Sessions API\n")

response = requests.get("http://localhost:8000/api/metrics/games/data")

if response.status_code == 200:
    data = response.json()
    games = data.get('games', [])
    
    print(f"Total games returned: {len(games)}")
    
    if games:
        # Group by month
        from collections import defaultdict
        by_month = defaultdict(int)
        
        for game in games:
            month = game['data'][:7]  # YYYY-MM
            by_month[month] += 1
        
        print("\n📅 Sessions by Month:")
        for month in sorted(by_month.keys()):
            print(f"   {month}: {by_month[month]} sessions")
        
        # Show first 10
        print("\n📋 First 10 sessions (chronological):")
        sorted_games = sorted(games, key=lambda x: x['data'])
        for game in sorted_games[:10]:
            tipo = game.get('tipo', 'treino')
            adversario = game.get('adversario', '-')
            data = game['data']
            print(f"   {data} | {tipo:8} | {adversario}")
        
        # Show last 10
        print("\n📋 Last 10 sessions:")
        for game in sorted_games[-10:]:
            tipo = game.get('tipo', 'treino')
            adversario = game.get('adversario', '-')
            data = game['data']
            print(f"   {data} | {tipo:8} | {adversario}")
    else:
        print("No games returned!")
else:
    print(f"API Error: {response.status_code}")
    print(response.text[:500])
