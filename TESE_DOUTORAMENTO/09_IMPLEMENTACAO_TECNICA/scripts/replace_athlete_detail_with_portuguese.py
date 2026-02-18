#!/usr/bin/env python3
"""Replace AthleteDetail.jsx with Portuguese version including opponent data and hover functionality"""

import os
import shutil

# Source and destination files
source_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetailPortuguese.jsx"
dest_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetail.jsx"

print("🔄 Substituindo AthleteDetail.jsx pela versão em português...")

# Backup original file
backup_file = dest_file + ".backup"
if os.path.exists(dest_file):
    shutil.copy2(dest_file, backup_file)
    print(f"   ✅ Backup criado: {backup_file}")

# Replace with Portuguese version
if os.path.exists(source_file):
    shutil.copy2(source_file, dest_file)
    print(f"   ✅ AthleteDetail.jsx substituído pela versão em português")
    
    # Remove the temporary Portuguese file
    os.remove(source_file)
    print(f"   ✅ Arquivo temporário removido")
else:
    print(f"   ❌ Arquivo fonte não encontrado: {source_file}")

print("\n✅ Atualização completa!")
print("📊 Funcionalidades adicionadas:")
print("   • Interface completamente em português")
print("   • Dados de adversários nas sessões de jogo")
print("   • Hover com ranking de wellness")
print("   • Dados detalhados do sono")
print("   • Escala de dificuldade do adversário (0-5)")
print("   • Desacelerações nos dados GPS")
print("   • Análise tática dos adversários")
print("\n🔄 A página será atualizada automaticamente")
