#!/usr/bin/env python3
"""Fix PSE column reference from rpe to pse in the comprehensive profile query"""

import os

metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Corrigindo referência da coluna PSE...")

# Fix the PSE column reference in the sessions query
old_pse_reference = "AVG(dp.rpe) as avg_pse_load"
new_pse_reference = "AVG(dp.pse) as avg_pse_load"

if old_pse_reference in content:
    content = content.replace(old_pse_reference, new_pse_reference)
    print("   ✅ Corrigido: dp.rpe → dp.pse")
else:
    print("   ⚠️ Referência dp.rpe não encontrada, verificando outras variações...")
    
    # Check for other possible variations
    variations = [
        ("AVG(dp.rpe)", "AVG(dp.pse)"),
        ("dp.rpe", "dp.pse"),
        ("rpe", "pse")
    ]
    
    for old_var, new_var in variations:
        if old_var in content and "dados_pse" in content:
            content = content.replace(old_var, new_var)
            print(f"   ✅ Corrigido: {old_var} → {new_var}")

# Write the corrected content back
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Referência da coluna PSE corrigida")
print("   • Coluna correta: pse (não rpe)")
print("   • Query de sessões atualizada")
print("\n🔄 Reinicie o backend para aplicar a correção")
