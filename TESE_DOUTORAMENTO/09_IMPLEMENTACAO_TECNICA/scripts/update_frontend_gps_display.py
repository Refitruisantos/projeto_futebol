#!/usr/bin/env python3
"""Update frontend to display all GPS data and add hover explanations"""

import os

athlete_detail_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetail.jsx"

with open(athlete_detail_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Atualizando frontend com dados GPS completos e hover explicativo...")

# Find the sessions table and add GPS columns
old_table_header = '''                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Desacelerações
                </th>'''

new_table_header = '''                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Player Load
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Acelerações
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Desacelerações
                </th>'''

content = content.replace(old_table_header, new_table_header)

# Update table body to show GPS data
old_table_body = '''                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-900 text-right">
                    -
                  </td>'''

new_table_body = '''                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-900 text-right">
                    {session.avg_player_load ? session.avg_player_load.toFixed(1) : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-900 text-right">
                    {session.avg_accelerations ? Math.round(session.avg_accelerations) : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-900 text-right">
                    {session.avg_high_decelerations ? Math.round(session.avg_high_decelerations) : '-'}
                  </td>'''

content = content.replace(old_table_body, new_table_body)

# Add hover explanations for wellness scores
old_wellness_score = '''                    <div 
                      className="text-2xl font-semibold text-gray-900 cursor-help"
                      title={`Ranking: ${comprehensiveProfile.wellness_data[0]?.ranking_wellness || 'N/A'}º de 20 atletas`}
                    >
                      {comprehensiveProfile.wellness_data[0]?.wellness_score?.toFixed(1) || 'N/A'}
                    </div>'''

new_wellness_score = '''                    <div 
                      className="text-2xl font-semibold text-gray-900 cursor-help"
                      title={`Pontuação baseada em sono (${comprehensiveProfile.wellness_data[0]?.sleep_quality || 'N/A'}/7), fadiga (${comprehensiveProfile.wellness_data[0]?.fatigue_level || 'N/A'}/7), stress e humor. Ranking: ${comprehensiveProfile.wellness_data[0]?.ranking_wellness || 'N/A'}º de 20 atletas`}
                    >
                      {comprehensiveProfile.wellness_data[0]?.wellness_score?.toFixed(1) || 'N/A'}
                    </div>'''

content = content.replace(old_wellness_score, new_wellness_score)

# Add explanation for recommendation
old_recommendation = '''                      <p className="text-sm text-gray-900 font-medium">
                        {comprehensiveProfile.wellness_data[0].training_recommendation === 'modified_training' ? 'Treino Modificado' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'normal_training' ? 'Treino Normal' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'light_training' ? 'Treino Leve' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'rest' ? 'Descanso' :
                         comprehensiveProfile.wellness_data[0].training_recommendation}
                      </p>'''

new_recommendation = '''                      <p 
                        className="text-sm text-gray-900 font-medium cursor-help"
                        title="Baseado na pontuação de wellness: >6.0=Normal, 4.0-6.0=Modificado, 2.0-4.0=Leve, <2.0=Descanso"
                      >
                        {comprehensiveProfile.wellness_data[0].training_recommendation === 'modified_training' ? 'Treino Modificado' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'normal_training' ? 'Treino Normal' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'light_training' ? 'Treino Leve' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'rest' ? 'Descanso' :
                         comprehensiveProfile.wellness_data[0].training_recommendation}
                      </p>'''

content = content.replace(old_recommendation, new_recommendation)

# Add explanation for readiness
old_readiness = '''                      <p className="text-2xl font-semibold text-gray-900">
                        {comprehensiveProfile.wellness_data[0].readiness_score.toFixed(1)}
                      </p>'''

new_readiness = '''                      <p 
                        className="text-2xl font-semibold text-gray-900 cursor-help"
                        title="Prontidão calculada: (Wellness × 0.4) + (Sono × 0.3) + (HRV × 0.3). >8.0=Excelente, 6.0-8.0=Bom, 4.0-6.0=Moderado, <4.0=Baixo"
                      >
                        {comprehensiveProfile.wellness_data[0].readiness_score.toFixed(1)}
                      </p>'''

content = content.replace(old_readiness, new_readiness)

# Fix load chart data source
old_load_chart = '''              {metrics.load_chart_data && metrics.load_chart_data.length > 0 ? (
                <LoadTrendChart data={metrics.load_chart_data} />
              ) : (
                <p className="text-gray-500">Sem dados de carga disponíveis</p>
              )}'''

new_load_chart = '''              {comprehensiveProfile?.load_chart_data && comprehensiveProfile.load_chart_data.length > 0 ? (
                <LoadTrendChart data={comprehensiveProfile.load_chart_data} />
              ) : (
                <p className="text-gray-500">Sem dados de carga disponíveis</p>
              )}'''

content = content.replace(old_load_chart, new_load_chart)

with open(athlete_detail_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Frontend atualizado:")
print("   • Colunas GPS adicionadas (Player Load, Acelerações, Desacelerações)")
print("   • Hover explicativo para pontuação de wellness")
print("   • Hover explicativo para recomendações de treino")
print("   • Hover explicativo para prontidão")
print("   • Gráfico de carga corrigido para usar dados do perfil abrangente")
print("\n🔄 A página será atualizada automaticamente")
