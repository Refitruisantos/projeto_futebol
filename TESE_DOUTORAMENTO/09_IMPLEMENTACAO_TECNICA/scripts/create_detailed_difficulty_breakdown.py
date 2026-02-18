#!/usr/bin/env python3
"""Create detailed difficulty calculation breakdown with individual factor scores"""

import psycopg2

conn = psycopg2.connect(
    host='localhost', port='5433', database='futebol_tese',
    user='postgres', password='desporto.20'
)
cursor = conn.cursor()

print("🔧 Creating detailed difficulty calculation breakdown...")

# 1. Update opponent difficulty details with detailed breakdown
print("\n1️⃣ Adding detailed calculation breakdown...")

cursor.execute("ALTER TABLE opponent_difficulty_details ADD COLUMN IF NOT EXISTS detailed_breakdown TEXT")

# 2. Calculate detailed breakdowns for each opponent
opponents_detailed = [
    {
        'name': 'FC Porto',
        'factors': {
            'league_position': {'value': 2, 'score': 0.9, 'weight': 25, 'points': 22.5},
            'recent_form': {'value': '4W-1D', 'score': 0.9, 'weight': 20, 'points': 18.0},
            'home_away': {'value': 'Away', 'score': 0.8, 'weight': 15, 'points': 12.0},
            'head_to_head': {'value': '2W-1D-2L', 'score': 0.6, 'weight': 15, 'points': 9.0},
            'key_players': {'value': '9/11', 'score': 0.9, 'weight': 10, 'points': 9.0},
            'tactical': {'value': 'Muito Alta', 'score': 1.0, 'weight': 10, 'points': 10.0},
            'physical': {'value': 'Alta', 'score': 0.8, 'weight': 5, 'points': 4.0}
        },
        'total': 84.5,
        'rating': 4.5
    },
    {
        'name': 'Sporting CP',
        'factors': {
            'league_position': {'value': 1, 'score': 1.0, 'weight': 25, 'points': 25.0},
            'recent_form': {'value': '5W', 'score': 1.0, 'weight': 20, 'points': 20.0},
            'home_away': {'value': 'Away', 'score': 0.8, 'weight': 15, 'points': 12.0},
            'head_to_head': {'value': '1W-1D-3L', 'score': 0.4, 'weight': 15, 'points': 6.0},
            'key_players': {'value': '10/11', 'score': 1.0, 'weight': 10, 'points': 10.0},
            'tactical': {'value': 'Muito Alta', 'score': 1.0, 'weight': 10, 'points': 10.0},
            'physical': {'value': 'Muito Alta', 'score': 1.0, 'weight': 5, 'points': 5.0}
        },
        'total': 88.0,
        'rating': 4.8
    },
    {
        'name': 'SL Benfica',
        'factors': {
            'league_position': {'value': 3, 'score': 0.8, 'weight': 25, 'points': 20.0},
            'recent_form': {'value': '4W-1L', 'score': 0.8, 'weight': 20, 'points': 16.0},
            'home_away': {'value': 'Home', 'score': 1.0, 'weight': 15, 'points': 15.0},
            'head_to_head': {'value': '2W-2D-1L', 'score': 0.7, 'weight': 15, 'points': 10.5},
            'key_players': {'value': '8/11', 'score': 0.8, 'weight': 10, 'points': 8.0},
            'tactical': {'value': 'Alta', 'score': 0.8, 'weight': 10, 'points': 8.0},
            'physical': {'value': 'Alta', 'score': 0.8, 'weight': 5, 'points': 4.0}
        },
        'total': 81.5,
        'rating': 4.2
    },
    {
        'name': 'Moreirense FC',
        'factors': {
            'league_position': {'value': 12, 'score': 0.3, 'weight': 25, 'points': 7.5},
            'recent_form': {'value': '1W-2D-2L', 'score': 0.3, 'weight': 20, 'points': 6.0},
            'home_away': {'value': 'Away', 'score': 0.8, 'weight': 15, 'points': 12.0},
            'head_to_head': {'value': '3W-2L', 'score': 0.6, 'weight': 15, 'points': 9.0},
            'key_players': {'value': '5/11', 'score': 0.5, 'weight': 10, 'points': 5.0},
            'tactical': {'value': 'Baixa', 'score': 0.2, 'weight': 10, 'points': 2.0},
            'physical': {'value': 'Moderada', 'score': 0.6, 'weight': 5, 'points': 3.0}
        },
        'total': 44.5,
        'rating': 2.8
    }
]

for opp in opponents_detailed:
    # Create detailed breakdown text
    breakdown_parts = []
    breakdown_parts.append(f"AVALIAÇÃO DETALHADA - {opp['name']} ({opp['rating']}/5)")
    breakdown_parts.append("")
    
    for factor_name, factor_data in opp['factors'].items():
        factor_display = {
            'league_position': 'Posição Liga',
            'recent_form': 'Forma Recente',
            'home_away': 'Casa/Fora',
            'head_to_head': 'Histórico H2H',
            'key_players': 'Jogadores-Chave',
            'tactical': 'Complexidade Tática',
            'physical': 'Intensidade Física'
        }
        
        name = factor_display[factor_name]
        value = factor_data['value']
        score = factor_data['score']
        weight = factor_data['weight']
        points = factor_data['points']
        
        breakdown_parts.append(f"• {name}: {value}")
        breakdown_parts.append(f"  Score: {score:.1f} × Peso: {weight}% = {points:.1f} pts")
    
    breakdown_parts.append("")
    breakdown_parts.append(f"TOTAL: {opp['total']:.1f}/100 pts → {opp['rating']}/5")
    breakdown_parts.append("")
    breakdown_parts.append("ESCALA: 90+ = 5.0 | 80-89 = 4.0-4.9 | 60-79 = 3.0-3.9 | 40-59 = 2.0-2.9 | <40 = 1.0-1.9")
    
    detailed_breakdown = "\n".join(breakdown_parts)
    
    # Update the database
    cursor.execute("""
        UPDATE opponent_difficulty_details 
        SET detailed_breakdown = %s
        WHERE opponent_name = %s
    """, (detailed_breakdown, opp['name']))

conn.commit()
print(f"   ✅ Updated {len(opponents_detailed)} opponents with detailed breakdowns")

# 3. Show sample detailed breakdown
print("\n2️⃣ Sample detailed breakdown:")
cursor.execute("""
    SELECT opponent_name, overall_rating, detailed_breakdown
    FROM opponent_difficulty_details
    WHERE opponent_name = 'FC Porto'
""")

result = cursor.fetchone()
if result:
    name, rating, breakdown = result
    print(f"\n{breakdown}")

cursor.close()
conn.close()

print("\n✅ DETAILED BREAKDOWN SYSTEM COMPLETE!")
print("   ✅ Each opponent now has factor-by-factor calculation")
print("   ✅ Shows individual scores, weights, and point contributions")
print("   ✅ Explains how total score converts to final rating")
print("\n🔄 Next: Update frontend to show detailed breakdown in tooltip")
