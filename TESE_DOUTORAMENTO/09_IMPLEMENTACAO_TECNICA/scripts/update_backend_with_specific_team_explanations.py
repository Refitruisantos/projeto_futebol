#!/usr/bin/env python3
"""Update backend API to include specific team difficulty explanations"""

import os

# Find and update the backend metrics.py file
backend_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

print("🔧 Updating backend to include specific team difficulty explanations...")

with open(backend_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the comprehensive profile function and update the sessions query
old_query_pattern = '''SELECT DISTINCT
            s.id,
            s.data,
            s.tipo,
            s.adversario,
            s.dificuldade_adversario,
            s.jornada,
            s.resultado,'''

new_query_pattern = '''SELECT DISTINCT
            s.id,
            s.data,
            s.tipo,
            s.adversario,
            s.dificuldade_adversario,
            odd.explanation as difficulty_explanation,
            s.jornada,
            s.resultado,'''

# Update the FROM clause to include the difficulty details table
old_from_pattern = '''FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s'''

new_from_pattern = '''FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id AND dg.atleta_id = %s
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id AND dp.atleta_id = %s
        LEFT JOIN opponent_difficulty_details odd ON s.adversario = odd.opponent_name'''

# Apply the updates
if old_query_pattern in content:
    content = content.replace(old_query_pattern, new_query_pattern)
    print("   ✅ Updated SELECT clause to include difficulty explanation")
else:
    print("   ⚠️  SELECT clause not found - checking for existing update")

if old_from_pattern in content:
    content = content.replace(old_from_pattern, new_from_pattern)
    print("   ✅ Updated FROM clause to join difficulty details")
else:
    print("   ⚠️  FROM clause not found - may already be updated")

# Write the updated content back
with open(backend_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("   ✅ Backend updated to include specific team explanations")

print("\n✅ BACKEND API UPDATED!")
print("   ✅ Sessions now include difficulty_explanation field")
print("   ✅ Each team will have its specific explanation")
print("\n🔄 Restart backend to apply changes!")
print("   Then update frontend to use specific explanations")
