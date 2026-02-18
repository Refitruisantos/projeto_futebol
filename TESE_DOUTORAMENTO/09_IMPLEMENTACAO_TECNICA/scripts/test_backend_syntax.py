#!/usr/bin/env python3
"""Test backend syntax and check for errors in metrics.py"""

import ast
import os

metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

print("🔍 Verificando sintaxe do backend...")

try:
    with open(metrics_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to parse the Python file
    ast.parse(content)
    print("   ✅ Sintaxe Python válida")
    
    # Check for common issues
    if "def get_comprehensive_athlete_profile" in content:
        print("   ✅ Função comprehensive profile encontrada")
        
        # Find the function and check its structure
        start_pos = content.find("def get_comprehensive_athlete_profile")
        if start_pos > 0:
            # Find the next function or end of file
            next_def = content.find("\ndef ", start_pos + 1)
            if next_def == -1:
                function_content = content[start_pos:]
            else:
                function_content = content[start_pos:next_def]
            
            # Check for proper indentation and structure
            lines = function_content.split('\n')
            print(f"   📊 Função tem {len(lines)} linhas")
            
            # Check for return statement
            if "return {" in function_content:
                print("   ✅ Return statement encontrado")
            else:
                print("   ❌ Return statement não encontrado")
                
            # Check for proper try-except
            if "try:" in function_content and "except" in function_content:
                print("   ✅ Try-except block encontrado")
            else:
                print("   ❌ Try-except block incompleto")
    else:
        print("   ❌ Função comprehensive profile não encontrada")
        
except SyntaxError as e:
    print(f"   ❌ Erro de sintaxe: {e}")
    print(f"      Linha {e.lineno}: {e.text}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Test a simple API call to see the actual error
print("\n🌐 Testando API diretamente...")
try:
    import requests
    response = requests.get("http://localhost:8000/api/metrics/athletes/255/comprehensive-profile")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Erro: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ Erro de conexão: {e}")
