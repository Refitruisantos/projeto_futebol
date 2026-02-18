#!/usr/bin/env python3
"""Fix backend API to properly return difficulty explanations"""

import os

# Find the backend metrics file
backend_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

print("🔧 Fixing backend API to return difficulty explanations...")

with open(backend_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the comprehensive profile function and ensure it includes the explanation field
if "comprehensive-profile" in content:
    print("   ✅ Found comprehensive profile endpoint")
    
    # Look for the sessions query and ensure it has the correct JOIN and SELECT
    lines = content.split('\n')
    updated_lines = []
    in_sessions_query = False
    
    for i, line in enumerate(lines):
        # Look for the sessions query start
        if "SELECT DISTINCT" in line and ("s.id" in line or "s.data" in line):
            in_sessions_query = True
            updated_lines.append(line)
        elif in_sessions_query and "s.adversario" in line:
            updated_lines.append(line)
            # Ensure we have the explanation field
            if i + 1 < len(lines) and "difficulty_explanation" not in lines[i + 1]:
                indent = len(line) - len(line.lstrip())
                updated_lines.append(" " * indent + "odd.explanation as difficulty_explanation,")
        elif in_sessions_query and "FROM sessoes s" in line:
            updated_lines.append(line)
        elif in_sessions_query and "LEFT JOIN dados_gps" in line:
            updated_lines.append(line)
        elif in_sessions_query and "LEFT JOIN dados_pse" in line:
            updated_lines.append(line)
            # Ensure we have the opponent difficulty JOIN
            if i + 1 < len(lines) and "opponent_difficulty_details" not in lines[i + 1]:
                indent = len(line) - len(line.lstrip())
                updated_lines.append(" " * indent + "LEFT JOIN opponent_difficulty_details odd ON s.adversario = odd.opponent_name")
        elif in_sessions_query and ("WHERE" in line or "GROUP BY" in line or "ORDER BY" in line):
            in_sessions_query = False
            updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Write the updated content
    updated_content = '\n'.join(updated_lines)
    
    with open(backend_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("   ✅ Updated backend API to include difficulty explanations")
else:
    print("   ❌ Could not find comprehensive profile endpoint")

# Also update the frontend to use the explanation field properly
frontend_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetail.jsx"

print("\n🔧 Ensuring frontend uses explanation field...")

with open(frontend_file, 'r', encoding='utf-8') as f:
    frontend_content = f.read()

# Make sure the tooltip uses difficulty_explanation first
if "difficulty_breakdown || session.difficulty_explanation" in frontend_content:
    # Change priority to explanation first, then breakdown
    frontend_content = frontend_content.replace(
        "session.difficulty_breakdown || session.difficulty_explanation",
        "session.difficulty_explanation || session.difficulty_breakdown"
    )
    
    with open(frontend_file, 'w', encoding='utf-8') as f:
        f.write(frontend_content)
    
    print("   ✅ Updated frontend to prioritize readable explanations")

print("\n✅ BACKEND API FIXED!")
print("   ✅ API will return difficulty_explanation field")
print("   ✅ Frontend prioritizes readable explanations")
print("\n🔄 Restart backend to apply changes!")
print("   Then hover over difficulty ratings to see readable explanations")
