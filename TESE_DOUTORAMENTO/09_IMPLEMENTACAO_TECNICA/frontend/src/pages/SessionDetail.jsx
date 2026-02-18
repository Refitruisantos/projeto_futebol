import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { sessionsApi } from '../api/client'
import { ArrowLeft } from 'lucide-react'

export default function SessionDetail() {
  const { id } = useParams()
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadSession()
  }, [id])

  const loadSession = async () => {
    try {
      setLoading(true)
      const response = await sessionsApi.getById(id)
      setSession(response.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-400">Carregando...</div>
  }

  if (error) {
    return <div className="text-red-400 py-12">Erro: {error}</div>
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="mb-6">
        <Link
          to="/sessions"
          className="inline-flex items-center text-sm text-gray-400 hover:text-gray-200"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Voltar às sessões
        </Link>
      </div>

      <div className="card-dark rounded-xl border border-white/5">
        <div className="px-6 py-5 border-b border-white/5">
          <h1 className="text-2xl font-bold text-white">
            {session?.tipo === 'jogo' ? 'Jogo' : 'Treino'} - {' '}
            {session?.data ? new Date(session.data).toLocaleDateString('pt-PT') : ''}
          </h1>
          {session?.adversario && (
            <p className="mt-1 text-sm text-gray-400">vs {session.adversario}</p>
          )}
        </div>

        <div className="px-6 py-5">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Data</dt>
              <dd className="mt-1 text-sm text-gray-300">
                {session?.data ? new Date(session.data).toLocaleDateString('pt-PT') : '-'}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Tipo</dt>
              <dd className="mt-1 text-sm text-gray-300">{session?.tipo}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Duração</dt>
              <dd className="mt-1 text-sm text-gray-300">
                {session?.duracao_min ? `${session.duracao_min} min` : '-'}
              </dd>
            </div>
            {session?.training_type && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Tipo de Treino</dt>
                <dd className="mt-1">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    session.training_type === 'speed' ? 'bg-red-500/10 text-red-400' :
                    session.training_type === 'strength' ? 'bg-orange-500/10 text-orange-400' :
                    session.training_type === 'tactical' ? 'bg-accent-cyan/10 text-accent-cyan' :
                    session.training_type === 'conditioning' ? 'bg-pitch-500/10 text-pitch-400' :
                    session.training_type === 'recovery' ? 'bg-teal-500/10 text-teal-400' :
                    'bg-dark-300 text-gray-400'
                  }`}>
                    {session.training_type === 'speed' ? '⚡ Speed (-3)' :
                     session.training_type === 'strength' ? '💪 Strength (-2)' :
                     session.training_type === 'tactical' ? '🧠 Tactical (0)' :
                     session.training_type === 'conditioning' ? '🏃 Conditioning (+1)' :
                     session.training_type === 'recovery' ? '💆 Recovery (+2)' :
                     session.training_type}
                  </span>
                </dd>
              </div>
            )}
            {session?.jornada && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Jornada</dt>
                <dd className="mt-1 text-sm text-gray-300">{session.jornada}</dd>
              </div>
            )}
            {session?.resultado && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Resultado</dt>
                <dd className="mt-1 text-sm text-gray-300">{session.resultado}</dd>
              </div>
            )}
            {session?.local && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Local</dt>
                <dd className="mt-1 text-sm text-gray-300">{session.local}</dd>
              </div>
            )}
          </dl>
          
          {session?.observacoes && session.tipo === 'treino' && (
            <div className="mt-6 pt-6 border-t border-white/5">
              <dt className="text-sm font-medium text-gray-500 mb-2">Descrição</dt>
              <dd className="text-sm text-gray-400">{session.observacoes}</dd>
            </div>
          )}
        </div>
      </div>

      {session?.gps_data && session.gps_data.length > 0 && (
        <div className="mt-6 card-dark rounded-xl border border-white/5">
          <div className="px-6 py-5 border-b border-white/5">
            <h2 className="text-lg font-medium text-white">Dados GPS</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-white/5">
              <thead className="bg-dark-300">
                <tr>
                  <th className="py-3 pl-6 pr-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Atleta
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Pos
                  </th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Dist. Total (m)
                  </th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Vel. Max (km/h)
                  </th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Sprints
                  </th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Acel
                  </th>
                  <th className="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Desacel
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 bg-dark-200">
                {session.gps_data.map((data) => (
                  <tr key={data.atleta_id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="whitespace-nowrap py-3 pl-6 pr-3 text-sm font-medium text-gray-200">
                      {data.nome_completo}
                    </td>
                    <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-400">
                      {data.posicao}
                    </td>
                    <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                      {data.distancia_total ? Math.round(data.distancia_total) : '-'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                      {data.velocidade_max ? data.velocidade_max.toFixed(1) : '-'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                      {data.sprints || '-'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                      {data.aceleracoes || '-'}
                    </td>
                    <td className="whitespace-nowrap px-3 py-3 text-sm text-gray-300 text-right">
                      {data.desaceleracoes || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
