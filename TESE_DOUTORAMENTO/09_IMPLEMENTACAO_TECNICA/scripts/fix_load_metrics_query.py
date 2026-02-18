#!/usr/bin/env python3
"""Fix the load metrics query to use correct column names"""

import os

metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Corrigindo query de métricas de carga...")

# Fix the load query with correct column names
old_load_query = '''        load_query = """
            SELECT 
                semana_inicio,
                carga_total,
                carga_aguda,
                carga_cronica,
                ratio_ac,
                monotonia,
                strain,
                freshness_index,
                risco_lesao
            FROM metricas_carga
            WHERE atleta_id = %s
            ORDER BY semana_inicio DESC
            LIMIT 12
        """'''

new_load_query = '''        load_query = """
            SELECT 
                semana_inicio,
                carga_total_semanal,
                carga_aguda,
                carga_cronica,
                acwr,
                monotonia,
                tensao,
                media_carga,
                nivel_risco_acwr
            FROM metricas_carga
            WHERE atleta_id = %s
            ORDER BY semana_inicio DESC
            LIMIT 12
        """'''

content = content.replace(old_load_query, new_load_query)

# Fix the load chart data mapping
old_chart_mapping = '''        # Format load data for chart
        load_chart_data = []
        for metric in reversed(load_metrics):  # Reverse for chronological order
            load_chart_data.append({
                'week': metric['semana_inicio'].strftime('%Y-%m-%d'),
                'acute_load': float(metric['carga_aguda']) if metric['carga_aguda'] else 0,
                'chronic_load': float(metric['carga_cronica']) if metric['carga_cronica'] else 0,
                'ac_ratio': float(metric['ratio_ac']) if metric['ratio_ac'] else 0,
                'monotony': float(metric['monotonia']) if metric['monotonia'] else 0,
                'strain': float(metric['strain']) if metric['strain'] else 0
            })'''

new_chart_mapping = '''        # Format load data for chart
        load_chart_data = []
        for metric in reversed(load_metrics):  # Reverse for chronological order
            load_chart_data.append({
                'week': metric['semana_inicio'].strftime('%Y-%m-%d'),
                'acute_load': float(metric['carga_aguda']) if metric['carga_aguda'] else 0,
                'chronic_load': float(metric['carga_cronica']) if metric['carga_cronica'] else 0,
                'ac_ratio': float(metric['acwr']) if metric['acwr'] else 0,
                'monotony': float(metric['monotonia']) if metric['monotonia'] else 0,
                'strain': float(metric['tensao']) if metric['tensao'] else 0,
                'total_load': float(metric['carga_total_semanal']) if metric['carga_total_semanal'] else 0
            })'''

content = content.replace(old_chart_mapping, new_chart_mapping)

# Write the corrected content back
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Query de métricas de carga corrigida:")
print("   • carga_total → carga_total_semanal")
print("   • ratio_ac → acwr")
print("   • strain → tensao")
print("   • risco_lesao → nivel_risco_acwr")
print("   • Adicionado total_load aos dados do gráfico")
print("\n🔄 Reinicie o backend para aplicar as correções")
