import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { athletesApi } from '../api/client'
import { ArrowLeft, TrendingUp, Activity, Heart, Zap } from 'lucide-react'
import { LoadTrendChart, WellnessChart } from '../components/LoadChart'

export default function AthleteDetail() {
  const { id } = useParams()
  const [athlete, setAthlete] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [comprehensiveProfile, setComprehensiveProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sessionFilter, setSessionFilter] = useState('all') // 'all', 'training', 'games'
  const [showRPEDetails, setShowRPEDetails] = useState(false)

  useEffect(() => {
    loadData()
  }, [id])

  // Debug logging
  useEffect(() => {
    if (comprehensiveProfile) {
      console.log('Dados do Perfil Abrangente:', comprehensiveProfile)
      console.log('Dados de Wellness:', comprehensiveProfile.wellness_data)
      console.log('Avaliações Físicas:', comprehensiveProfile.physical_evaluations)
    }
  }, [comprehensiveProfile])

  const loadData = async () => {
    try {
      setLoading(true)
      const [athleteRes, metricsRes, profileRes] = await Promise.all([
        athletesApi.getById(id),
        athletesApi.getMetrics(id, 7),
        fetch(`http://localhost:8000/api/metrics/athletes/${id}/comprehensive-profile`)
          .then(res => res.json())
          .catch(() => null)
      ])
      setAthlete(athleteRes.data)
      setMetrics(metricsRes.data)
      setComprehensiveProfile(profileRes)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-400">A carregar...</div>
  }

  if (error) {
    return <div className="text-red-400 py-12">Erro: {error}</div>
  }

  const filteredSessions = comprehensiveProfile?.recent_sessions?.filter(session => {
    if (sessionFilter === 'training') return session.tipo === 'treino'
    if (sessionFilter === 'games') return session.tipo === 'jogo'
    return true
  }) || []

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-6">
        <Link
          to="/athletes"
          className="inline-flex items-center text-sm text-gray-400 hover:text-gray-200"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Voltar aos atletas
        </Link>
      </div>

      {/* Cabeçalho do Atleta */}
      <div className="card-dark rounded-xl mb-6 border border-white/5">
        <div className="px-6 py-5">
          <div className="flex items-center space-x-5">
            <div className="flex-shrink-0">
              <div className="w-20 h-20 bg-dark-300 rounded-full flex items-center justify-center border border-white/10">
                <span className="text-2xl font-bold text-gray-400">
                  {athlete?.nome_completo?.split(' ').map(n => n[0]).join('').slice(0, 2)}
                </span>
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-white">{athlete?.nome_completo}</h1>
              <div className="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:space-x-6">
                <div className="mt-2 flex items-center text-sm text-gray-400">
                  <span className="font-medium">Posição:</span>
                  <span className="ml-1">{athlete?.posicao}</span>
                </div>
                <div className="mt-2 flex items-center text-sm text-gray-400">
                  <span className="font-medium">Número:</span>
                  <span className="ml-1">{athlete?.numero_camisola}</span>
                </div>
                <div className="mt-2 flex items-center text-sm text-gray-400">
                  <span className="font-medium">Idade:</span>
                  <span className="ml-1">{comprehensiveProfile?.athlete_info?.idade || 'N/A'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Estado de Wellness */}
      {comprehensiveProfile?.wellness_data && comprehensiveProfile.wellness_data.length > 0 ? (
        <div className="card-dark rounded-xl mb-6 border border-white/5">
          <div className="px-6 py-5 border-b border-white/5">
            <div className="flex items-center">
              <Heart className="w-5 h-5 text-pitch-400 mr-2" />
              <h2 className="text-lg font-medium text-white">Estado de Wellness</h2>
            </div>
          </div>
          <div className="px-6 py-5">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {/* Wellness Atual */}
              <div className="bg-dark-300/50 rounded-lg p-4 border border-pitch-500/20">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Heart className="w-8 h-8 text-pitch-400" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Pontuação Atual</p>
                    <div 
                      className="text-2xl font-semibold text-white cursor-help"
                      title={`Pontuação baseada em sono (${comprehensiveProfile.wellness_data[0]?.sleep_quality || 'N/A'}/7), fadiga (${comprehensiveProfile.wellness_data[0]?.fatigue_level || 'N/A'}/7), stress e humor. Ranking: ${comprehensiveProfile.wellness_data[0]?.ranking_wellness || 'N/A'}º de 20 atletas`}
                    >
                      {comprehensiveProfile.wellness_data[0]?.wellness_score?.toFixed(1) || 'N/A'}
                    </div>
                    <p className="text-sm text-gray-400 capitalize">
                      {comprehensiveProfile.wellness_data[0]?.wellness_status || 'Desconhecido'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Tendência de Wellness */}
              {comprehensiveProfile.wellness_trends && (
                <div className="bg-dark-300/50 rounded-lg p-4 border border-accent-cyan/20">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <TrendingUp className={`w-8 h-8 ${
                        comprehensiveProfile.wellness_trends.trend_direction === 'improving' ? 'text-green-600' :
                        comprehensiveProfile.wellness_trends.trend_direction === 'declining' ? 'text-red-600' :
                        'text-yellow-600'
                      }`} />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-500">Tendência 7 Dias</p>
                      <p className="text-2xl font-semibold text-white">
                        {comprehensiveProfile.wellness_trends.avg_score_7d || 'N/A'}
                      </p>
                      <p className={`text-sm capitalize ${
                        comprehensiveProfile.wellness_trends.trend_direction === 'improving' ? 'text-green-600' :
                        comprehensiveProfile.wellness_trends.trend_direction === 'declining' ? 'text-red-600' :
                        'text-yellow-600'
                      }`}>
                        {comprehensiveProfile.wellness_trends.trend_direction === 'improving' ? 'Melhorando' :
                         comprehensiveProfile.wellness_trends.trend_direction === 'declining' ? 'Declinando' : 'Estável'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Recomendação de Treino */}
              {comprehensiveProfile.wellness_data[0]?.training_recommendation && (
                <div className="bg-dark-300/50 rounded-lg p-4 border border-accent-gold/20">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Zap className="w-8 h-8 text-orange-600" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-500">Recomendação</p>
                      <p 
                        className="text-sm text-white font-medium cursor-help"
                        title="Baseado na pontuação de wellness: >6.0=Normal, 4.0-6.0=Modificado, 2.0-4.0=Leve, <2.0=Descanso"
                      >
                        {comprehensiveProfile.wellness_data[0].training_recommendation === 'modified_training' ? 'Treino Modificado' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'normal_training' ? 'Treino Normal' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'light_training' ? 'Treino Leve' :
                         comprehensiveProfile.wellness_data[0].training_recommendation === 'rest' ? 'Descanso' :
                         comprehensiveProfile.wellness_data[0].training_recommendation}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Pontuação de Prontidão */}
              {comprehensiveProfile.wellness_data[0]?.readiness_score && (
                <div className="bg-dark-300/50 rounded-lg p-4 border border-purple-500/20">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Activity className="w-8 h-8 text-purple-600" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-500">Prontidão</p>
                      <p 
                        className="text-2xl font-semibold text-white cursor-help"
                        title="Prontidão calculada: (Wellness × 0.4) + (Sono × 0.3) + (HRV × 0.3). >8.0=Excelente, 6.0-8.0=Bom, 4.0-6.0=Moderado, <4.0=Baixo"
                      >
                        {comprehensiveProfile.wellness_data[0].readiness_score.toFixed(1)}
                      </p>
                      <p className="text-sm text-gray-400">Pronto para Treinar</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Dados Detalhados do Sono */}
            {comprehensiveProfile.wellness_data[0]?.tempo_cama && (
              <div className="mt-6 bg-dark-300/50 rounded-lg p-4 border border-white/5">
                <h3 className="text-sm font-medium text-white mb-3">Análise Detalhada do Sono</h3>
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-white">
                      {comprehensiveProfile.wellness_data[0].tempo_cama}
                    </div>
                    <div className="text-xs text-gray-500">Hora de Deitar</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-white">
                      {comprehensiveProfile.wellness_data[0].eficiencia_sono?.toFixed(1) || 'N/A'}%
                    </div>
                    <div className="text-xs text-gray-500">Eficiência do Sono</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-white">
                      {comprehensiveProfile.wellness_data[0].sono_profundo_min || 'N/A'}min
                    </div>
                    <div className="text-xs text-gray-500">Sono Profundo</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-white">
                      {comprehensiveProfile.wellness_data[0].num_despertares || 0}
                    </div>
                    <div className="text-xs text-gray-500">Despertares</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="card-dark rounded-xl mb-6 border border-white/5">
          <div className="px-6 py-5">
            <p className="text-gray-500">A carregar dados de wellness...</p>
          </div>
        </div>
      )}

      {/* Avaliações Físicas */}
      {comprehensiveProfile?.physical_evaluations && comprehensiveProfile.physical_evaluations.length > 0 ? (
        <div className="card-dark rounded-xl mb-6 border border-white/5">
          <div className="px-6 py-5 border-b border-white/5">
            <div className="flex items-center">
              <Zap className="w-5 h-5 text-accent-cyan mr-2" />
              <h2 className="text-lg font-medium text-white">Avaliações Físicas</h2>
            </div>
          </div>
          <div className="px-6 py-5">
            {/* Resumo da Última Avaliação */}
            {comprehensiveProfile.physical_evaluations[0] && (
              <div className="mb-6">
                <h3 className="text-sm font-medium text-white mb-4">
                  Última Avaliação ({new Date(comprehensiveProfile.physical_evaluations[0].data_avaliacao).toLocaleDateString('pt-PT')})
                </h3>
                <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
                  {/* Testes de Velocidade */}
                  <div className="bg-dark-300/50 rounded-lg p-4 border border-red-500/20">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-400">
                        {comprehensiveProfile.physical_evaluations[0].sprint_35m_seconds?.toFixed(2) || 'N/A'}s
                      </div>
                      <div className="text-sm text-gray-400">Sprint 35m</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {comprehensiveProfile.physical_evaluations[0].percentile_speed}º percentil
                      </div>
                    </div>
                  </div>

                  <div className="bg-dark-300/50 rounded-lg p-4 border border-accent-gold/20">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-accent-gold">
                        {comprehensiveProfile.physical_evaluations[0].test_5_0_5_seconds?.toFixed(2) || 'N/A'}s
                      </div>
                      <div className="text-sm text-gray-400">Agilidade 5-0-5</div>
                      <div className="text-xs text-gray-500 mt-1">Mudança de direção</div>
                    </div>
                  </div>

                  {/* Testes de Potência */}
                  <div className="bg-dark-300/50 rounded-lg p-4 border border-accent-cyan/20">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-accent-cyan">
                        {comprehensiveProfile.physical_evaluations[0].cmj_height_cm?.toFixed(1) || 'N/A'}cm
                      </div>
                      <div className="text-sm text-gray-400">Altura CMJ</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {comprehensiveProfile.physical_evaluations[0].percentile_power}º percentil
                      </div>
                    </div>
                  </div>

                  {/* Resistência */}
                  <div className="bg-dark-300/50 rounded-lg p-4 border border-pitch-500/20">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-pitch-400">
                        {comprehensiveProfile.physical_evaluations[0].vo2_max_ml_kg_min?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-400">VO₂ Máx</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {comprehensiveProfile.physical_evaluations[0].percentile_endurance}º percentil
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="card-dark rounded-xl mb-6 border border-white/5">
          <div className="px-6 py-5">
            <p className="text-gray-500">A carregar dados de avaliação física...</p>
          </div>
        </div>
      )}

      {/* Métricas de Carga de Treino */}
      {metrics && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card-dark rounded-xl border border-white/5">
            <div className="px-6 py-5 border-b border-white/5">
              <div className="flex items-center">
                <TrendingUp className="w-5 h-5 text-accent-cyan mr-2" />
                <h2 className="text-lg font-medium text-white">Tendências de Carga</h2>
              </div>
            </div>
            <div className="px-6 py-5">
              {comprehensiveProfile?.load_chart_data && comprehensiveProfile.load_chart_data.length > 0 ? (
                <LoadTrendChart data={comprehensiveProfile.load_chart_data} />
              ) : (
                <p className="text-gray-500">Sem dados de carga disponíveis</p>
              )}
            </div>
          </div>

          <div className="card-dark rounded-xl border border-white/5">
            <div className="px-6 py-5 border-b border-white/5">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-pitch-400 mr-2" />
                <h2 className="text-lg font-medium text-white">Wellness</h2>
              </div>
            </div>
            <div className="px-6 py-5">
              {comprehensiveProfile?.wellness_data && comprehensiveProfile.wellness_data.length > 0 ? (
                <WellnessChart data={comprehensiveProfile.wellness_data.slice(0, 14)} />
              ) : (
                <p className="text-gray-500">Sem dados de wellness disponíveis</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Sessões */}
      <div className="mt-6 card-dark rounded-xl border border-white/5">
        <div className="px-6 py-5 border-b border-white/5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-white">Sessões</h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setSessionFilter('all')}
                className={`px-3 py-1 text-sm rounded ${
                  sessionFilter === 'all' ? 'bg-pitch-500/10 text-pitch-400' : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                Todas ({filteredSessions.length})
              </button>
              <button
                onClick={() => setSessionFilter('training')}
                className={`px-3 py-1 text-sm rounded ${
                  sessionFilter === 'training' ? 'bg-pitch-500/10 text-pitch-400' : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                Treino ({comprehensiveProfile?.recent_sessions?.filter(s => s.tipo === 'treino').length || 0})
              </button>
              <button
                onClick={() => setSessionFilter('games')}
                className={`px-3 py-1 text-sm rounded ${
                  sessionFilter === 'games' ? 'bg-pitch-500/10 text-pitch-400' : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                Jogos ({comprehensiveProfile?.recent_sessions?.filter(s => s.tipo === 'jogo').length || 0})
              </button>
            </div>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-white/5">
            <thead className="bg-dark-300">
              <tr>
                <th className="py-3 pl-6 pr-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Data
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Tipo
                </th>
                <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Adversário
                </th>
                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Dificuldade
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Distância
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Vel. Máx
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Carga PSE
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Player Load
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Acelerações
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Desacelerações
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 bg-dark-200">
              {filteredSessions.map((session, index) => (
                <tr key={index} className="hover:bg-white/[0.02] transition-colors">
                  <td className="whitespace-nowrap py-3 pl-6 pr-3 text-sm font-medium text-gray-200">
                    {new Date(session.data).toLocaleDateString('pt-PT')}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-400">
                    <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                      session.tipo === 'jogo' 
                        ? 'bg-red-500/10 text-red-400'
                        : 'bg-accent-cyan/10 text-accent-cyan'
                    }`}>
                      {session.tipo === 'jogo' ? 'Jogo' : 'Treino'}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300">
                    {session.adversario || '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-center">
                    {session.dificuldade_adversario ? (
                      <span 
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium cursor-help ${
                          session.dificuldade_adversario >= 4 ? 'bg-red-500/10 text-red-400' :
                          session.dificuldade_adversario >= 3 ? 'bg-yellow-500/10 text-yellow-400' :
                          'bg-pitch-500/10 text-pitch-400'
                        }`}
                        title={session.difficulty_explanation || session.difficulty_breakdown || `Dificuldade ${session.dificuldade_adversario}/5 - ${session.adversario}: Avaliação baseada em múltiplos fatores de análise do adversário`}
                      >
                        {session.dificuldade_adversario}/5
                      </span>
                    ) : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                    {session.avg_distance ? `${Math.round(session.avg_distance)}m` : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                    {session.avg_max_speed ? `${session.avg_max_speed.toFixed(1)} km/h` : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                    {session.avg_pse_load ? session.avg_pse_load.toFixed(0) : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                    {session.avg_player_load ? session.avg_player_load.toFixed(1) : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                    {session.avg_accelerations ? Math.round(session.avg_accelerations) : '-'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                    {session.avg_decelerations ? Math.round(session.avg_decelerations) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
