import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']

export function TopAthletesChart({ athletes }) {
  if (!athletes || athletes.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados disponíveis</p>
  }

  const chartData = athletes.map(a => ({
    nome: a.nome_completo?.split(' ')[0] || 'N/A',
    carga: Math.round(a.weekly_load || 0),
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="nome" style={{ fontSize: '12px' }} />
        <YAxis style={{ fontSize: '12px' }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="carga" fill="#6366f1" name="Carga (AU)" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function PositionDistributionChart({ athletes }) {
  if (!athletes || athletes.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados disponíveis</p>
  }

  // Count athletes by position
  const positionCounts = athletes.reduce((acc, athlete) => {
    const pos = athlete.posicao || 'N/A'
    acc[pos] = (acc[pos] || 0) + 1
    return acc
  }, {})

  const chartData = Object.entries(positionCounts).map(([name, value]) => ({
    name,
    value
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function DistanceDistributionChart({ athletes }) {
  if (!athletes || athletes.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados de GPS disponíveis</p>
  }

  // Filter athletes with GPS data and sort by distance
  const athletesWithGPS = athletes
    .filter(a => a.distancia_total_media > 0)
    .sort((a, b) => (b.distancia_total_media || 0) - (a.distancia_total_media || 0))
    .slice(0, 10)

  if (athletesWithGPS.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados de GPS disponíveis</p>
  }

  const chartData = athletesWithGPS.map(a => ({
    nome: a.nome_completo?.split(' ')[0] || 'N/A',
    distancia: Math.round(a.distancia_total_media || 0),
    velocidade: a.velocidade_max_media || 0,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" style={{ fontSize: '12px' }} />
        <YAxis dataKey="nome" type="category" style={{ fontSize: '11px' }} width={80} />
        <Tooltip />
        <Legend />
        <Bar dataKey="distancia" fill="#10b981" name="Distância Média (m)" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function SpeedDistributionChart({ athletes }) {
  if (!athletes || athletes.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados de velocidade</p>
  }

  const athletesWithSpeed = athletes
    .filter(a => a.velocidade_max_media > 0)
    .sort((a, b) => (b.velocidade_max_media || 0) - (a.velocidade_max_media || 0))
    .slice(0, 10)

  if (athletesWithSpeed.length === 0) {
    return <p className="text-sm text-gray-500">Sem dados de velocidade</p>
  }

  const chartData = athletesWithSpeed.map(a => ({
    nome: a.nome_completo?.split(' ')[0] || 'N/A',
    velocidade: a.velocidade_max_media || 0,
  }))

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="nome" style={{ fontSize: '12px' }} />
        <YAxis domain={[0, 35]} style={{ fontSize: '12px' }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="velocidade" stroke="#f59e0b" strokeWidth={2} name="Vel. Máxima (km/h)" />
      </LineChart>
    </ResponsiveContainer>
  )
}
