import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export function LoadTrendChart({ data }) {
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
}

export function WellnessChart({ data }) {
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
}