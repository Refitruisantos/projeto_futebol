#!/usr/bin/env python3
"""Create readable written explanations for team difficulty ratings"""

import psycopg2

conn = psycopg2.connect(
    host='localhost', port='5433', database='futebol_tese',
    user='postgres', password='desporto.20'
)
cursor = conn.cursor()

print("🔧 Creating readable team difficulty explanations...")

# Create readable explanations for each team
team_explanations = {
    'SL Benfica': {
        'rating': 4.2,
        'explanation': 'SL Benfica é classificado como DIFÍCIL (4.2/5). Atualmente em 3º lugar na liga, demonstra excelente forma recente com 4 vitórias nos últimos 5 jogos. O facto de jogar em casa representa uma vantagem significativa. O histórico direto é equilibrado (2V-2E-1D), mas a equipa mantém 8 dos 11 jogadores-chave disponíveis. A complexidade tática é alta, exigindo preparação especial, e a intensidade física esperada é elevada.'
    },
    'FC Porto': {
        'rating': 4.5,
        'explanation': 'FC Porto é classificado como MUITO DIFÍCIL (4.5/5). Ocupando o 2º lugar na liga, apresenta forma recente excelente com 4 vitórias e 1 empate nos últimos 5 jogos. Jogar fora de casa aumenta a dificuldade. O histórico direto é equilibrado (2V-1E-2D), mas a equipa tem 9 dos 11 jogadores-chave disponíveis. A complexidade tática é muito alta, sendo uma das equipas mais organizadas taticamente, e a intensidade física é elevada.'
    },
    'Sporting CP': {
        'rating': 4.8,
        'explanation': 'Sporting CP é classificado como MUITO DIFÍCIL (4.8/5). Líder da liga (1º lugar), demonstra forma perfeita com 5 vitórias consecutivas nos últimos jogos. Jogar fora de casa adiciona dificuldade extra. Apesar do histórico direto desfavorável (1V-1E-3D), a equipa está no seu melhor momento com todos os 10 jogadores-chave disponíveis. A complexidade tática é muito alta e a intensidade física é máxima.'
    },
    'Moreirense FC': {
        'rating': 2.8,
        'explanation': 'Moreirense FC é classificado como MODERADO (2.8/5). Posicionado em 12º lugar na liga, apresenta forma recente fraca com apenas 1 vitória, 2 empates e 2 derrotas nos últimos 5 jogos. Jogar fora de casa mantém alguma dificuldade. O histórico direto é favorável (3V-2D), mas a equipa tem apenas 5 dos 11 jogadores-chave disponíveis. A complexidade tática é baixa e a intensidade física é moderada.'
    },
    'SC Braga': {
        'rating': 3.8,
        'explanation': 'SC Braga é classificado como DIFÍCIL (3.8/5). Em 4º lugar na liga, mostra boa forma recente com 3 vitórias, 1 empate e 1 derrota nos últimos 5 jogos. Jogar fora de casa aumenta a dificuldade. O histórico direto é muito favorável (3V-1E-1D), mas a equipa mantém 7 dos 11 jogadores-chave disponíveis. A complexidade tática é alta e a intensidade física é moderada.'
    },
    'Vitória SC': {
        'rating': 3.2,
        'explanation': 'Vitória SC é classificado como MODERADO (3.2/5). Posicionado em 6º lugar na liga, apresenta forma recente moderada com 2 vitórias, 2 empates e 1 derrota nos últimos 5 jogos. Jogar em casa representa vantagem para eles. O histórico direto é muito favorável para nós (4V-1D), e a equipa tem 6 dos 11 jogadores-chave disponíveis. A complexidade tática é moderada e a intensidade física é moderada.'
    }
}

# Update database with readable explanations
print("\n1️⃣ Updating database with readable explanations...")

for team_name, data in team_explanations.items():
    cursor.execute("""
        UPDATE opponent_difficulty_details 
        SET explanation = %s
        WHERE opponent_name = %s
    """, (data['explanation'], team_name))

conn.commit()
print(f"   ✅ Updated {len(team_explanations)} teams with readable explanations")

# 2. Verify the updates
print("\n2️⃣ Sample readable explanations:")
cursor.execute("""
    SELECT opponent_name, overall_rating, explanation
    FROM opponent_difficulty_details
    WHERE explanation IS NOT NULL
    ORDER BY overall_rating DESC
    LIMIT 3
""")

results = cursor.fetchall()
for name, rating, explanation in results:
    print(f"\n🔵 {name} ({rating}/5):")
    print(f"   {explanation}")

cursor.close()
conn.close()

print("\n✅ READABLE EXPLANATIONS COMPLETE!")
print("   ✅ Each team now has a clear written explanation")
print("   ✅ Explains league position, form, tactical complexity")
print("   ✅ Uses Portuguese language with football terminology")
print("\n🔄 Restart backend to serve new explanations!")
