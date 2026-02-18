#!/usr/bin/env python3
"""Fix frontend chart components to match API data structure"""

import os

# Fix LoadChart.jsx to work with the correct data structure
loadchart_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\components\LoadChart.jsx"

with open(loadchart_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Fixing LoadChart.jsx to match API data structure...")

# Replace the LoadTrendChart component to work with load_chart_data
new_load_trend_chart = '''export function LoadTrendChart({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados para visualizar</p>
  }

  // Use the load_chart_data from comprehensive profile API
  const chartData = data.map(item => ({
    week: new Date(item.week).toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit' }),
    acute_load: item.acute_load || 0,
    chronic_load: item.chronic_load || 0,
    ac_ratio: item.ac_ratio || 0,
    monotony: item.monotony || 0,
    strain: item.strain || 0
  }))

  return (
    <div className="space-y-6">
      {/* Acute vs Chronic Load Chart */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Carga Aguda vs Crónica (12 semanas)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" style={{ fontSize: '12px' }} />
            <YAxis style={{ fontSize: '12px' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="acute_load" stroke="#ef4444" strokeWidth={2} name="Carga Aguda" />
            <Line type="monotone" dataKey="chronic_load" stroke="#3b82f6" strokeWidth={2} name="Carga Crónica" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ACWR Chart */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Ratio Aguda:Crónica (ACWR)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" style={{ fontSize: '12px' }} />
            <YAxis domain={[0.5, 2.0]} style={{ fontSize: '12px' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="ac_ratio" stroke="#8b5cf6" strokeWidth={2} name="ACWR" />
            {/* Add danger zones */}
            <Line type="monotone" dataKey={() => 1.5} stroke="#f59e0b" strokeDasharray="5 5" strokeWidth={1} name="Zona de Risco" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Monotony and Strain */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Monotonia e Tensão</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" style={{ fontSize: '12px' }} />
            <YAxis style={{ fontSize: '12px' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="monotony" fill="#10b981" name="Monotonia" />
            <Bar dataKey="strain" fill="#f59e0b" name="Tensão" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}'''

# Replace the WellnessChart component to work with wellness_data
new_wellness_chart = '''export function WellnessChart({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados de wellness</p>
  }

  // Use the wellness_data from comprehensive profile API
  const chartData = data
    .slice(0, 14)
    .reverse()
    .map(item => ({
      date: new Date(item.data).toLocaleDateString('pt-PT', { day: '2-digit', month: '2-digit' }),
      wellness_score: item.wellness_score || 0,
      sleep_hours: item.sleep_hours || 0,
      fatigue_level: item.fatigue_level || 0,
      stress_level: item.stress_level || 0,
      mood: item.mood || 0
    }))

  return (
    <div className="space-y-6">
      {/* Wellness Score Trend */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Pontuação de Wellness (últimos 14 dias)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" style={{ fontSize: '12px' }} />
            <YAxis domain={[1, 7]} style={{ fontSize: '12px' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="wellness_score" stroke="#3b82f6" strokeWidth={3} name="Wellness Score" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Sleep and Recovery Indicators */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Indicadores de Recuperação</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" style={{ fontSize: '12px' }} />
            <YAxis domain={[0, 10]} style={{ fontSize: '12px' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="sleep_hours" stroke="#10b981" strokeWidth={2} name="Horas de Sono" />
            <Line type="monotone" dataKey="fatigue_level" stroke="#f59e0b" strokeWidth={2} name="Nível de Fadiga" />
            <Line type="monotone" dataKey="stress_level" stroke="#ef4444" strokeWidth={2} name="Nível de Stress" />
            <Line type="monotone" dataKey="mood" stroke="#8b5cf6" strokeWidth={2} name="Humor" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}'''

# Find and replace the LoadTrendChart function
start_marker = "export function LoadTrendChart({ sessions }) {"
end_marker = "export function WellnessChart({ sessions }) {"

start_pos = content.find(start_marker)
end_pos = content.find(end_marker)

if start_pos != -1 and end_pos != -1:
    # Replace LoadTrendChart
    new_content = content[:start_pos] + new_load_trend_chart + "\n\n" + content[end_pos:]
    
    # Now replace WellnessChart
    wellness_start = new_content.find("export function WellnessChart({ sessions }) {")
    if wellness_start != -1:
        # Find the end of the file or next export
        wellness_end = len(new_content)  # Go to end of file
        
        new_content = new_content[:wellness_start] + new_wellness_chart
    
    # Write the updated content
    with open(loadchart_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("   ✅ LoadTrendChart updated to use load_chart_data")
    print("   ✅ WellnessChart updated to use wellness_data")
else:
    print("   ❌ Could not find chart functions to replace")

print("\n🔧 Chart components fixed to match API data structure!")
print("   • LoadTrendChart now displays ACWR, acute/chronic load trends")
print("   • WellnessChart now displays wellness scores and recovery indicators")
print("   • Both charts use correct data from comprehensive profile API")
print("\n🔄 Refresh the frontend to see working charts!")
