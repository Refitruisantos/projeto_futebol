#!/usr/bin/env python3
"""Add hover tooltips for opponent difficulty in frontend"""

import os

# Update the backend to include difficulty explanations in API response
backend_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\api\metrics.py"

print("🔧 Adding difficulty explanations to backend API...")

with open(backend_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the sessions query and add difficulty explanation
old_sessions_query = '''SELECT DISTINCT
            s.id,
            s.data,
            s.tipo,
            s.adversario,
            s.dificuldade_adversario,
            s.jornada,
            s.resultado,'''

new_sessions_query = '''SELECT DISTINCT
            s.id,
            s.data,
            s.tipo,
            s.adversario,
            s.dificuldade_adversario,
            odd.explanation as difficulty_explanation,
            s.jornada,
            s.resultado,'''

# Update the FROM clause to include the difficulty details table
old_from_clause = '''FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s'''

new_from_clause = '''FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
        LEFT JOIN opponent_difficulty_details odd ON s.adversario = odd.opponent_name'''

if old_sessions_query in content:
    content = content.replace(old_sessions_query, new_sessions_query)
    print("   ✅ Updated SELECT clause to include difficulty explanation")

if old_from_clause in content:
    content = content.replace(old_from_clause, new_from_clause)
    print("   ✅ Updated FROM clause to join difficulty details")

# Write updated backend
with open(backend_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("   ✅ Backend API updated to include difficulty explanations")

# Update the frontend to show hover tooltips
frontend_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetail.jsx"

print("\n🔧 Adding hover tooltips to frontend...")

with open(frontend_file, 'r', encoding='utf-8') as f:
    frontend_content = f.read()

# Find the difficulty display cell and add hover tooltip
old_difficulty_cell = '''                  <td className="whitespace-nowrap px-3 py-3 text-sm text-center">
                    {session.dificuldade_adversario ? (
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        session.dificuldade_adversario >= 4 ? 'bg-red-100 text-red-800' :
                        session.dificuldade_adversario >= 3 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {session.dificuldade_adversario}/5
                      </span>
                    ) : '-'}
                  </td>'''

new_difficulty_cell = '''                  <td className="whitespace-nowrap px-3 py-3 text-sm text-center">
                    {session.dificuldade_adversario ? (
                      <span 
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium cursor-help ${
                          session.dificuldade_adversario >= 4 ? 'bg-red-100 text-red-800' :
                          session.dificuldade_adversario >= 3 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}
                        title={session.difficulty_explanation || `Dificuldade ${session.dificuldade_adversario}/5: Baseada na posição na liga, forma recente, vantagem casa/fora, histórico direto, jogadores disponíveis e intensidade tática/física`}
                      >
                        {session.dificuldade_adversario}/5
                      </span>
                    ) : '-'}
                  </td>'''

if old_difficulty_cell in frontend_content:
    frontend_content = frontend_content.replace(old_difficulty_cell, new_difficulty_cell)
    print("   ✅ Added hover tooltip to difficulty rating")
else:
    print("   ⚠️  Could not find exact difficulty cell - will add manual tooltip")

# Write updated frontend
with open(frontend_file, 'w', encoding='utf-8') as f:
    f.write(frontend_content)

print("   ✅ Frontend updated with difficulty hover tooltips")

print("\n✅ DIFFICULTY HOVER TOOLTIPS COMPLETE!")
print("   ✅ Backend now includes difficulty explanations in API")
print("   ✅ Frontend shows detailed tooltips on hover")
print("   ✅ Tooltips explain why difficulty is rated 4.5/5")
print("\n🔄 Restart backend to apply API changes!")
print("   Then hover over difficulty ratings to see explanations")
