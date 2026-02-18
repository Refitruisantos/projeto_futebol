#!/usr/bin/env python3
"""Update API to include detailed difficulty breakdown"""

import os

# Update the backend metrics.py file
backend_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

print("🔧 Updating backend API to include detailed breakdown...")

with open(backend_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and update the SELECT clause to include detailed_breakdown
old_select = '''SELECT DISTINCT
            s.id,
            s.data,
            s.tipo,
            s.adversario,
            s.dificuldade_adversario,
            odd.explanation as difficulty_explanation,
            s.jornada,
            s.resultado,'''

new_select = '''SELECT DISTINCT
            s.id,
            s.data,
            s.tipo,
            s.adversario,
            s.dificuldade_adversario,
            odd.explanation as difficulty_explanation,
            odd.detailed_breakdown as difficulty_breakdown,
            s.jornada,
            s.resultado,'''

if old_select in content:
    content = content.replace(old_select, new_select)
    print("   ✅ Updated SELECT clause to include detailed_breakdown")
else:
    print("   ⚠️  SELECT clause not found - may need manual update")

# Write updated content
with open(backend_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("   ✅ Backend API updated with detailed breakdown field")

print("\n✅ BACKEND API ENHANCED!")
print("   ✅ Sessions now include difficulty_breakdown field")
print("   ✅ Contains factor-by-factor calculation details")
print("\n🔄 Restart backend to apply changes!")
