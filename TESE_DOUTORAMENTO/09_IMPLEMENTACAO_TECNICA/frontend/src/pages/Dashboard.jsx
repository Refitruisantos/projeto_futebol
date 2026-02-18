import { useState, useEffect } from 'react'
import { metricsApi, computerVisionApi, xgboostApi, sessionsApi } from '../api/client'
import { Activity, TrendingUp, AlertTriangle, Users, BarChart3, Zap, Shield, Eye, Brain, ArrowUpRight, ArrowDownRight, Minus, ChevronDown, ChevronUp, Heart, MapPin, Video } from 'lucide-react'
import { TopAthletesChart, PositionDistributionChart, DistanceDistributionChart, SpeedDistributionChart } from '../components/TeamCharts'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(null)
  const [dashboard, setDashboard] = useState(null)
  const [cvSummary, setCvSummary] = useState(null)
  const [substitutions, setSubstitutions] = useState(null)
  const [performanceDrop, setPerformanceDrop] = useState(null)
  const [sessionCount, setSessionCount] = useState(0)
  const [error, setError] = useState(null)
  const [expandedPlayer, setExpandedPlayer] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [summaryRes, dashboardRes, cvRes, subRes, sessRes, perfDropRes] = await Promise.allSettled([
        metricsApi.getTeamSummary(),
        metricsApi.getTeamDashboard(),
        computerVisionApi.getAllAnalyses(5),
        xgboostApi.getSubstitutionRecommendations(),
        sessionsApi.getAll({ limit: 1 }),
        xgboostApi.getPerformanceDropPredictions(),
      ])
      if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value.data)
      if (dashboardRes.status === 'fulfilled') setDashboard(dashboardRes.value.data)
      if (cvRes.status === 'fulfilled') setCvSummary(cvRes.value.data)
      if (subRes.status === 'fulfilled') setSubstitutions(subRes.value.data)
      if (sessRes.status === 'fulfilled') setSessionCount(sessRes.value.data?.length || 0)
      if (perfDropRes.status === 'fulfilled') setPerformanceDrop(perfDropRes.value.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', bar: 'bg-red-500', glow: 'glow-red' }
      case 'high': return { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', bar: 'bg-orange-500', glow: 'glow-gold' }
      case 'moderate': return { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', bar: 'bg-yellow-500', glow: '' }
      default: return { bg: 'bg-pitch-500/10', border: 'border-pitch-500/30', text: 'text-pitch-400', bar: 'bg-pitch-500', glow: 'glow-green' }
    }
  }

  const getFactorBarColor = (direction) => {
    if (direction === 'negative') return 'bg-red-500'
    if (direction === 'positive') return 'bg-pitch-500'
    return 'bg-gray-500'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-pitch-500/30 border-t-pitch-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400 text-sm">A carregar dados...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return <div className="text-red-400 py-12 text-center">Erro: {error}</div>
  }

  const riskRed = dashboard?.risk_summary?.red || 0
  const riskYellow = dashboard?.risk_summary?.yellow || 0
  const riskGreen = dashboard?.risk_summary?.green || 0
  const totalAthletes = riskRed + riskYellow + riskGreen

  return (
    <div className="space-y-6">

      {/* === TOP SUMMARY CARDS === */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Athletes */}
        <div className="card-dark rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-pitch-500/10 flex items-center justify-center">
              <Users className="w-5 h-5 text-pitch-400" />
            </div>
            <span className="text-xs font-medium text-pitch-400 bg-pitch-500/10 px-2 py-1 rounded-full">Ativos</span>
          </div>
          <div className="text-3xl font-bold text-white">{summary?.total_athletes || 0}</div>
          <p className="text-xs text-gray-500 mt-1">Atletas no plantel</p>
        </div>

        {/* Sessions */}
        <div className="card-dark rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-accent-cyan/10 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-accent-cyan" />
            </div>
            <span className="text-xs font-medium text-accent-cyan bg-accent-cyan/10 px-2 py-1 rounded-full">Total</span>
          </div>
          <div className="text-3xl font-bold text-white">{summary?.total_sessions_7d || 0}</div>
          <p className="text-xs text-gray-500 mt-1">Sessões registadas</p>
        </div>

        {/* Player Load */}
        <div className="card-dark rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-accent-gold/10 flex items-center justify-center">
              <Activity className="w-5 h-5 text-accent-gold" />
            </div>
          </div>
          <div className="text-3xl font-bold text-white">{summary?.avg_player_load_7d ? Math.round(summary.avg_player_load_7d) : '-'}</div>
          <p className="text-xs text-gray-500 mt-1">Player Load médio</p>
        </div>

        {/* Risk */}
        <div className="card-dark rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-lg bg-accent-red/10 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-accent-red" />
            </div>
            {riskRed > 0 && <span className="text-xs font-medium text-red-400 bg-red-500/10 px-2 py-1 rounded-full animate-pulse">Alerta</span>}
          </div>
          <div className="text-3xl font-bold text-white">{riskRed}</div>
          <p className="text-xs text-gray-500 mt-1">Atletas em alto risco</p>
        </div>
      </div>

      {/* === RISK DISTRIBUTION BAR === */}
      {totalAthletes > 0 && (
        <div className="card-dark rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Shield className="w-4 h-4 text-pitch-400" />
              Distribuição de Risco da Equipa
            </h3>
            <span className="text-xs text-gray-500">{totalAthletes} atletas</span>
          </div>
          <div className="flex rounded-full h-3 overflow-hidden bg-dark-300">
            {riskRed > 0 && <div className="bg-red-500 transition-all" style={{ width: `${(riskRed / totalAthletes) * 100}%` }}></div>}
            {riskYellow > 0 && <div className="bg-yellow-500 transition-all" style={{ width: `${(riskYellow / totalAthletes) * 100}%` }}></div>}
            {riskGreen > 0 && <div className="bg-pitch-500 transition-all" style={{ width: `${(riskGreen / totalAthletes) * 100}%` }}></div>}
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-xs text-red-400">{riskRed} Alto Risco</span>
            <span className="text-xs text-yellow-400">{riskYellow} Atenção</span>
            <span className="text-xs text-pitch-400">{riskGreen} Normal</span>
          </div>
        </div>
      )}

      {/* === TAB NAVIGATION === */}
      <div className="flex gap-1 bg-dark-300/50 p-1 rounded-lg w-fit">
        {[
          { id: 'overview', label: 'Visão Geral', icon: Users },
          { id: 'ml_prediction', label: 'ML Predição Queda', icon: Brain },
          { id: 'substitution', label: 'Substituição', icon: Zap },
          { id: 'charts', label: 'Gráficos', icon: BarChart3 },
          { id: 'performance', label: 'Performance', icon: TrendingUp },
        ].map(tab => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-pitch-600/20 text-pitch-400 border border-pitch-600/30'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* === OVERVIEW TAB === */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* GPS Metrics */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Métricas GPS</h3>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Acelerações', value: summary?.avg_accelerations, unit: '/sessão', color: 'text-accent-cyan', bgColor: 'bg-accent-cyan/10', icon: Zap },
                { label: 'Desacelerações', value: summary?.avg_decelerations, unit: '/sessão', color: 'text-accent-orange', bgColor: 'bg-accent-orange/10', icon: AlertTriangle },
                { label: 'Sprints', value: summary?.avg_sprints, unit: '/sessão', color: 'text-pitch-400', bgColor: 'bg-pitch-500/10', icon: TrendingUp },
                { label: 'Dist. Alta Vel.', value: summary?.avg_high_speed_distance, unit: 'm/sessão', color: 'text-purple-400', bgColor: 'bg-purple-500/10', icon: Activity },
              ].map((metric, i) => {
                const Icon = metric.icon
                return (
                  <div key={i} className="card-dark rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-8 h-8 rounded-lg ${metric.bgColor} flex items-center justify-center`}>
                        <Icon className={`w-4 h-4 ${metric.color}`} />
                      </div>
                      <span className="text-xs text-gray-500">{metric.label}</span>
                    </div>
                    <div className="text-2xl font-bold text-white">{metric.value ? Math.round(metric.value) : '-'}</div>
                    <p className="text-[10px] text-gray-600 mt-0.5">{metric.unit}</p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Two Column: Top Load + At Risk */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top 5 Load */}
            <div className="card-dark rounded-xl p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-accent-gold" />
                Top 5 — Carga de Treino
              </h3>
              <div className="space-y-2">
                {dashboard?.top_load_athletes?.map((athlete, idx) => {
                  const maxLoad = dashboard.top_load_athletes[0]?.weekly_load || 1
                  const pct = ((athlete.weekly_load || 0) / maxLoad) * 100
                  return (
                    <div key={athlete.atleta_id || idx} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors">
                      <span className="text-xs font-bold text-gray-600 w-5">{idx + 1}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-gray-200 truncate">{athlete.nome_completo}</span>
                          <span className="text-sm font-bold text-accent-gold ml-2">{Math.round(athlete.weekly_load || 0)}</span>
                        </div>
                        <div className="h-1.5 bg-dark-300 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-accent-gold/60 to-accent-gold rounded-full transition-all" style={{ width: `${pct}%` }}></div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* At Risk Athletes */}
            <div className="card-dark rounded-xl p-5">
              <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-accent-red" />
                Atletas em Risco
              </h3>
              {dashboard?.at_risk_athletes?.length > 0 ? (
                <div className="space-y-2">
                  {dashboard.at_risk_athletes.slice(0, 5).map((athlete) => (
                    <div key={athlete.atleta_id} className="flex items-center justify-between p-3 rounded-lg bg-red-500/5 border border-red-500/10 hover:border-red-500/20 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                        <div>
                          <p className="text-sm font-medium text-gray-200">{athlete.nome}</p>
                          <p className="text-xs text-gray-500">{athlete.posicao}</p>
                        </div>
                      </div>
                      <span className="text-xs px-2 py-1 bg-red-500/10 text-red-400 rounded-full font-medium border border-red-500/20">
                        {athlete.classificacao || 'Alto'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-12 h-12 rounded-full bg-pitch-500/10 flex items-center justify-center mx-auto mb-3">
                    <Shield className="w-6 h-6 text-pitch-400" />
                  </div>
                  <p className="text-sm text-gray-500">Nenhum atleta em risco</p>
                </div>
              )}
            </div>
          </div>

          {/* ML Performance Drop Preview */}
          {performanceDrop?.predictions?.length > 0 && (
            <div className="card-dark rounded-xl p-5 border border-purple-500/10">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  Predição ML — Queda de Performance
                </h3>
                <button
                  onClick={() => setActiveTab('ml_prediction')}
                  className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
                >
                  Ver detalhes →
                </button>
              </div>
              {/* Data sources badges */}
              {performanceDrop.data_sources && (
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {performanceDrop.data_sources.map((ds, i) => (
                    <span key={i} className={`text-[10px] px-2 py-0.5 rounded-full border ${
                      ds.status === 'active'
                        ? 'bg-pitch-500/10 text-pitch-400 border-pitch-500/20'
                        : 'bg-dark-300/50 text-gray-600 border-white/5'
                    }`}>
                      {ds.name}
                    </span>
                  ))}
                </div>
              )}
              {/* Summary counters */}
              <div className="grid grid-cols-4 gap-2 mb-4">
                <div className="text-center p-2 rounded-lg bg-red-500/5 border border-red-500/10">
                  <div className="text-lg font-bold text-red-400">{performanceDrop.summary?.critical || 0}</div>
                  <div className="text-[10px] text-gray-500">Crítico</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-orange-500/5 border border-orange-500/10">
                  <div className="text-lg font-bold text-orange-400">{performanceDrop.summary?.high || 0}</div>
                  <div className="text-[10px] text-gray-500">Alto</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-yellow-500/5 border border-yellow-500/10">
                  <div className="text-lg font-bold text-yellow-400">{performanceDrop.summary?.moderate || 0}</div>
                  <div className="text-[10px] text-gray-500">Atenção</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-pitch-500/5 border border-pitch-500/10">
                  <div className="text-lg font-bold text-pitch-400">{performanceDrop.summary?.low || 0}</div>
                  <div className="text-[10px] text-gray-500">Estável</div>
                </div>
              </div>
              {/* Top 3 at-risk players */}
              <div className="space-y-2">
                {performanceDrop.predictions.filter(p => p.severity !== 'low').slice(0, 3).map((player) => {
                  const colors = getPriorityColor(player.severity)
                  return (
                    <div key={player.atleta_id} className={`flex items-center justify-between p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${colors.bar} ${player.severity === 'critical' ? 'animate-pulse' : ''}`}></div>
                        <div>
                          <p className="text-sm font-medium text-gray-200">{player.nome}</p>
                          <p className="text-xs text-gray-500">{player.posicao} • {player.top_factors?.[0]?.label}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <span className={`text-sm font-bold ${colors.text}`}>{player.drop_probability}%</span>
                          <p className="text-[10px] text-gray-600">prob. queda</p>
                        </div>
                        <span className={`text-[10px] px-2 py-1 rounded-full font-medium ${colors.bg} ${colors.text} border ${colors.border}`}>
                          {player.severity_label}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* === ML PERFORMANCE DROP PREDICTION TAB === */}
      {activeTab === 'ml_prediction' && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="card-dark rounded-xl p-5 border border-purple-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-accent-cyan flex items-center justify-center" style={{ boxShadow: '0 0 15px rgba(168,85,247,0.3)' }}>
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Predição de Queda de Performance</h3>
                  <p className="text-xs text-gray-500">XGBoost + SHAP — Análise multi-fonte com Machine Learning</p>
                </div>
              </div>
              {performanceDrop?.week_analyzed && (
                <span className="text-xs text-gray-500 bg-dark-300/50 px-3 py-1 rounded-full">
                  Semana: {new Date(performanceDrop.week_analyzed).toLocaleDateString('pt-PT')}
                </span>
              )}
            </div>

            {/* Data Sources */}
            {performanceDrop?.data_sources && (
              <div className="mt-4 flex flex-wrap gap-2">
                {performanceDrop.data_sources.map((ds, i) => {
                  const iconMap = { activity: Activity, map: MapPin, heart: Heart, shield: Shield, video: Video }
                  const DsIcon = iconMap[ds.icon] || Activity
                  return (
                    <span key={i} className={`flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-full border ${
                      ds.status === 'active'
                        ? 'bg-pitch-500/10 text-pitch-400 border-pitch-500/20'
                        : 'bg-dark-300/50 text-gray-600 border-white/5 line-through'
                    }`}>
                      <DsIcon className="w-3 h-3" />
                      {ds.name}
                    </span>
                  )
                })}
              </div>
            )}

            {/* Model info */}
            {performanceDrop?.model_info && (
              <div className="mt-3 flex items-center gap-4 text-[10px] text-gray-600">
                <span>Modelo: {performanceDrop.model_info.type}</span>
                <span>{performanceDrop.model_info.features_used} features</span>
                <span>{performanceDrop.model_info.data_sources_count} fontes de dados ativas</span>
              </div>
            )}
          </div>

          {/* Summary Counters */}
          {performanceDrop?.summary && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card-dark rounded-xl p-4 border border-red-500/10">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                  <span className="text-xs text-gray-500">Queda Crítica</span>
                </div>
                <div className="text-2xl font-bold text-red-400">{performanceDrop.summary.critical}</div>
              </div>
              <div className="card-dark rounded-xl p-4 border border-orange-500/10">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                  <span className="text-xs text-gray-500">Queda Provável</span>
                </div>
                <div className="text-2xl font-bold text-orange-400">{performanceDrop.summary.high}</div>
              </div>
              <div className="card-dark rounded-xl p-4 border border-yellow-500/10">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <span className="text-xs text-gray-500">Atenção</span>
                </div>
                <div className="text-2xl font-bold text-yellow-400">{performanceDrop.summary.moderate}</div>
              </div>
              <div className="card-dark rounded-xl p-4 border border-pitch-500/10">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full bg-pitch-500"></div>
                  <span className="text-xs text-gray-500">Estável</span>
                </div>
                <div className="text-2xl font-bold text-pitch-400">{performanceDrop.summary.low}</div>
              </div>
            </div>
          )}

          {/* Player Prediction Cards */}
          {performanceDrop?.predictions?.length > 0 ? (
            <div className="space-y-3">
              {performanceDrop.predictions.map((player, idx) => {
                const colors = getPriorityColor(player.severity)
                const isExpanded = expandedPlayer === `ml_${player.atleta_id}`
                return (
                  <div key={player.atleta_id} className={`card-dark rounded-xl border ${colors.border} overflow-hidden transition-all`}>
                    {/* Main Row */}
                    <div
                      className="flex items-center gap-4 p-4 cursor-pointer hover:bg-white/[0.02] transition-colors"
                      onClick={() => setExpandedPlayer(isExpanded ? null : `ml_${player.atleta_id}`)}
                    >
                      {/* Rank */}
                      <div className="w-8 text-center">
                        <span className={`text-lg font-bold ${idx < 3 ? colors.text : 'text-gray-600'}`}>{idx + 1}</span>
                      </div>

                      {/* Player Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-white">{player.nome}</span>
                          {player.numero && <span className="text-xs text-gray-600">#{player.numero}</span>}
                        </div>
                        <p className="text-xs text-gray-500">{player.posicao} • {player.top_factors?.[0]?.label}</p>
                      </div>

                      {/* Drop Probability Bar */}
                      <div className="w-36 hidden sm:block">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-[10px] text-gray-600">Prob. Queda</span>
                          <span className={`text-xs font-bold ${colors.text}`}>{player.drop_probability}%</span>
                        </div>
                        <div className="h-2 bg-dark-300 rounded-full overflow-hidden">
                          <div className={`h-full ${colors.bar} rounded-full transition-all`} style={{ width: `${player.drop_probability}%` }}></div>
                        </div>
                      </div>

                      {/* Severity Badge */}
                      <span className={`text-xs px-3 py-1.5 rounded-full font-semibold ${colors.bg} ${colors.text} border ${colors.border} whitespace-nowrap`}>
                        {player.severity_label}
                      </span>

                      {/* Expand */}
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-600" /> : <ChevronDown className="w-4 h-4 text-gray-600" />}
                    </div>

                    {/* Expanded Detail */}
                    {isExpanded && (
                      <div className="px-4 pb-4 border-t border-white/5 pt-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {/* SHAP Factor Bars */}
                          <div>
                            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Fatores SHAP (contribuição para queda)</h4>
                            <div className="space-y-2.5">
                              {player.top_factors.map((factor) => {
                                const maxShap = Math.max(...player.top_factors.map(f => Math.abs(f.shap_value)), 0.01)
                                const barWidth = Math.min(100, (Math.abs(factor.shap_value) / maxShap) * 100)
                                return (
                                  <div key={factor.feature}>
                                    <div className="flex items-center justify-between mb-1">
                                      <div className="flex items-center gap-2">
                                        <span className={`w-1.5 h-1.5 rounded-full ${
                                          factor.category === 'gps' ? 'bg-accent-cyan' :
                                          factor.category === 'wellness' ? 'bg-pink-400' :
                                          factor.category === 'carga' ? 'bg-accent-gold' :
                                          factor.category === 'risco' ? 'bg-red-400' :
                                          factor.category === 'video' ? 'bg-purple-400' :
                                          'bg-gray-400'
                                        }`}></span>
                                        <span className="text-xs text-gray-400">{factor.label}</span>
                                        <span className="text-[10px] text-gray-600">({factor.raw_value})</span>
                                      </div>
                                      <span className={`text-xs font-medium ${
                                        factor.direction === 'negative' ? 'text-red-400' :
                                        factor.direction === 'positive' ? 'text-pitch-400' : 'text-gray-500'
                                      }`}>
                                        {factor.shap_value > 0 ? '+' : ''}{factor.shap_value.toFixed(3)}
                                      </span>
                                    </div>
                                    <div className="h-1.5 bg-dark-300 rounded-full overflow-hidden">
                                      <div
                                        className={`h-full rounded-full transition-all ${
                                          factor.direction === 'negative' ? 'bg-red-500' :
                                          factor.direction === 'positive' ? 'bg-pitch-500' : 'bg-gray-500'
                                        }`}
                                        style={{ width: `${barWidth}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                )
                              })}
                            </div>
                            {/* Category legend */}
                            <div className="flex flex-wrap gap-3 mt-4 pt-3 border-t border-white/5">
                              {[
                                { color: 'bg-accent-gold', label: 'Carga' },
                                { color: 'bg-accent-cyan', label: 'GPS' },
                                { color: 'bg-pink-400', label: 'Bem-estar' },
                                { color: 'bg-red-400', label: 'Risco' },
                                { color: 'bg-purple-400', label: 'Vídeo' },
                              ].map(cat => (
                                <span key={cat.label} className="flex items-center gap-1 text-[10px] text-gray-600">
                                  <span className={`w-1.5 h-1.5 rounded-full ${cat.color}`}></span>
                                  {cat.label}
                                </span>
                              ))}
                            </div>
                          </div>

                          {/* Key Metrics */}
                          <div>
                            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Métricas do Atleta</h4>
                            <div className="grid grid-cols-3 gap-2">
                              {[
                                { label: 'ACWR', value: player.metrics_summary.acwr, warn: player.metrics_summary.acwr > 1.5 || player.metrics_summary.acwr < 0.8 },
                                { label: 'Monotonia', value: player.metrics_summary.monotony, warn: player.metrics_summary.monotony > 2.0 },
                                { label: 'Tensão', value: player.metrics_summary.strain, warn: player.metrics_summary.strain > 6000 },
                                { label: 'Bem-estar', value: `${player.metrics_summary.wellness}/25`, warn: player.metrics_summary.wellness < 12 },
                                { label: 'Carga Sem.', value: player.metrics_summary.weekly_load, warn: false },
                                { label: 'Dist. Média', value: player.metrics_summary.avg_distance || '-', warn: false },
                                { label: 'Sprints', value: player.metrics_summary.avg_sprints || '-', warn: false },
                                { label: 'Risco Lesão', value: `${player.metrics_summary.injury_risk}/5`, warn: player.metrics_summary.injury_risk > 3 },
                                { label: 'Fadiga Acum.', value: `${player.metrics_summary.fatigue_score}/5`, warn: player.metrics_summary.fatigue_score > 3 },
                              ].map((m, i) => (
                                <div key={i} className={`p-2.5 rounded-lg ${m.warn ? 'bg-red-500/5 border border-red-500/10' : 'bg-dark-300/50'}`}>
                                  <p className="text-[10px] text-gray-500 uppercase">{m.label}</p>
                                  <p className={`text-sm font-bold ${m.warn ? 'text-red-400' : 'text-white'}`}>{m.value ?? '-'}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="card-dark rounded-xl p-12 text-center">
              <Brain className="w-12 h-12 text-gray-700 mx-auto mb-3" />
              <p className="text-gray-500">Sem dados suficientes para predições de performance</p>
              <p className="text-xs text-gray-600 mt-1">Adicione sessões de treino com dados GPS, PSE e vídeo</p>
            </div>
          )}
        </div>
      )}

      {/* === SUBSTITUTION TAB (XGBoost + SHAP) === */}
      {activeTab === 'substitution' && (
        <div className="space-y-6">
          {/* Header */}
          <div className="card-dark rounded-xl p-5 border border-pitch-600/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pitch-500 to-accent-cyan flex items-center justify-center glow-green">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Predição Tática XGBoost + SHAP</h3>
                  <p className="text-xs text-gray-500">Recomendação de substituição baseada em 6 fatores ponderados</p>
                </div>
              </div>
              {substitutions?.week_analyzed && (
                <span className="text-xs text-gray-500 bg-dark-300/50 px-3 py-1 rounded-full">
                  Semana: {new Date(substitutions.week_analyzed).toLocaleDateString('pt-PT')}
                </span>
              )}
            </div>
            {substitutions?.model_info && (
              <div className="mt-4 flex flex-wrap gap-2">
                {substitutions.model_info.factors?.map((f, i) => (
                  <span key={i} className="text-[10px] px-2 py-1 rounded-full bg-dark-300/50 text-gray-400 border border-white/5">
                    {f} ({substitutions.model_info.weights[i]}%)
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Player Cards */}
          {substitutions?.recommendations?.length > 0 ? (
            <div className="space-y-3">
              {substitutions.recommendations.map((player, idx) => {
                const colors = getPriorityColor(player.priority)
                const isExpanded = expandedPlayer === player.atleta_id
                return (
                  <div key={player.atleta_id} className={`card-dark rounded-xl border ${colors.border} overflow-hidden transition-all`}>
                    {/* Main Row */}
                    <div
                      className="flex items-center gap-4 p-4 cursor-pointer hover:bg-white/[0.02] transition-colors"
                      onClick={() => setExpandedPlayer(isExpanded ? null : player.atleta_id)}
                    >
                      {/* Rank */}
                      <div className="w-8 text-center">
                        <span className={`text-lg font-bold ${idx < 3 ? colors.text : 'text-gray-600'}`}>{idx + 1}</span>
                      </div>

                      {/* Player Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-white">{player.nome}</span>
                          {player.numero && <span className="text-xs text-gray-600">#{player.numero}</span>}
                        </div>
                        <p className="text-xs text-gray-500">{player.posicao} • {player.top_risk_factor}</p>
                      </div>

                      {/* Score Bar */}
                      <div className="w-32 hidden sm:block">
                        <div className="h-2 bg-dark-300 rounded-full overflow-hidden">
                          <div className={`h-full ${colors.bar} rounded-full transition-all`} style={{ width: `${player.substitution_score}%` }}></div>
                        </div>
                        <p className="text-[10px] text-gray-600 mt-0.5 text-right">{player.substitution_score.toFixed(0)}/100</p>
                      </div>

                      {/* Priority Badge */}
                      <span className={`text-xs px-3 py-1.5 rounded-full font-semibold ${colors.bg} ${colors.text} border ${colors.border} whitespace-nowrap`}>
                        {player.priority_label}
                      </span>

                      {/* Expand */}
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-600" /> : <ChevronDown className="w-4 h-4 text-gray-600" />}
                    </div>

                    {/* Expanded Detail */}
                    {isExpanded && (
                      <div className="px-4 pb-4 border-t border-white/5 pt-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {/* SHAP-like Factor Bars */}
                          <div>
                            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Fatores de Impacto (SHAP)</h4>
                            <div className="space-y-2.5">
                              {Object.entries(player.factors).map(([key, factor]) => (
                                <div key={key}>
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-xs text-gray-400">{factor.label}</span>
                                    <span className={`text-xs font-medium ${
                                      factor.direction === 'negative' ? 'text-red-400' :
                                      factor.direction === 'positive' ? 'text-pitch-400' : 'text-gray-500'
                                    }`}>
                                      {factor.impact > 0 ? `+${factor.impact}` : factor.impact}
                                    </span>
                                  </div>
                                  <div className="h-1.5 bg-dark-300 rounded-full overflow-hidden">
                                    <div
                                      className={`h-full rounded-full transition-all ${getFactorBarColor(factor.direction)}`}
                                      style={{ width: `${Math.min(100, (factor.impact / 25) * 100)}%` }}
                                    ></div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Key Metrics */}
                          <div>
                            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Métricas Chave</h4>
                            <div className="grid grid-cols-2 gap-3">
                              {[
                                { label: 'ACWR', value: player.metrics.acwr, warn: player.metrics.acwr > 1.5 || player.metrics.acwr < 0.8 },
                                { label: 'Monotonia', value: player.metrics.monotony, warn: player.metrics.monotony > 2.0 },
                                { label: 'Tensão', value: player.metrics.strain, warn: player.metrics.strain > 6000 },
                                { label: 'Bem-estar', value: `${player.metrics.wellness}/25`, warn: player.metrics.wellness < 12 },
                                { label: 'Carga Sem.', value: player.metrics.weekly_load, warn: false },
                                { label: 'Sprints', value: player.metrics.avg_sprints ?? '-', warn: false },
                              ].map((m, i) => (
                                <div key={i} className={`p-2.5 rounded-lg ${m.warn ? 'bg-red-500/5 border border-red-500/10' : 'bg-dark-300/50'}`}>
                                  <p className="text-[10px] text-gray-500 uppercase">{m.label}</p>
                                  <p className={`text-sm font-bold ${m.warn ? 'text-red-400' : 'text-white'}`}>{m.value ?? '-'}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="card-dark rounded-xl p-12 text-center">
              <Zap className="w-12 h-12 text-gray-700 mx-auto mb-3" />
              <p className="text-gray-500">Sem dados suficientes para recomendações de substituição</p>
              <p className="text-xs text-gray-600 mt-1">Adicione sessões de treino com dados GPS e PSE</p>
            </div>
          )}
        </div>
      )}

      {/* === CHARTS TAB === */}
      {activeTab === 'charts' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card-dark rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Top 5 — Carga</h3>
            <TopAthletesChart athletes={dashboard?.top_load_athletes || []} />
          </div>
          <div className="card-dark rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Distribuição por Posição</h3>
            <PositionDistributionChart athletes={dashboard?.athletes_overview || []} />
          </div>
          <div className="card-dark rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Top 10 — Distância Média</h3>
            <DistanceDistributionChart athletes={dashboard?.athletes_overview || []} />
          </div>
          <div className="card-dark rounded-xl p-5">
            <h3 className="text-sm font-semibold text-white mb-4">Top 10 — Velocidade Máxima</h3>
            <SpeedDistributionChart athletes={dashboard?.athletes_overview || []} />
          </div>
        </div>
      )}

      {/* === PERFORMANCE TAB === */}
      {activeTab === 'performance' && (
        <div className="card-dark rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-white/5">
            <h3 className="text-sm font-semibold text-white">Performance dos Atletas</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="px-4 py-3 text-left text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Atleta</th>
                  <th className="px-4 py-3 text-left text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Posição</th>
                  <th className="px-4 py-3 text-right text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Carga</th>
                  <th className="px-4 py-3 text-right text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Monotonia</th>
                  <th className="px-4 py-3 text-right text-[10px] font-semibold text-gray-500 uppercase tracking-wider">ACWR</th>
                  <th className="px-4 py-3 text-right text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Risco</th>
                </tr>
              </thead>
              <tbody>
                {dashboard?.athletes_overview?.map((athlete) => {
                  const risk = athlete.risk_overall
                  const riskColors = risk === 'red' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                    risk === 'yellow' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                    'bg-pitch-500/10 text-pitch-400 border-pitch-500/20'
                  return (
                    <tr key={athlete.atleta_id} className="border-b border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3">
                        <div className="text-sm font-medium text-gray-200">{athlete.nome_completo}</div>
                        <div className="text-[10px] text-gray-600">{athlete.training_days || 0} dias treino</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-1 rounded-full bg-dark-300/50 text-gray-400 border border-white/5">
                          {athlete.posicao}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm font-medium text-gray-200">{athlete.weekly_load ? Math.round(athlete.weekly_load) : '-'}</span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm font-medium text-gray-200">{athlete.monotony ? athlete.monotony.toFixed(2) : '-'}</span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-sm font-medium text-gray-200">{athlete.acwr ? athlete.acwr.toFixed(2) : '-'}</span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className={`text-xs px-2 py-1 rounded-full font-medium border ${riskColors}`}>
                          {risk === 'red' ? 'Alto' : risk === 'yellow' ? 'Médio' : 'Normal'}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
