import { useState, useEffect } from 'react'
import { opponentsApi } from '../api/client'
import { PlusIcon, PencilIcon, TrashIcon, EyeIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

export default function Opponents() {
  const [opponents, setOpponents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedOpponent, setSelectedOpponent] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadOpponents()
  }, [])

  const loadOpponents = async () => {
    try {
      setLoading(true)
      const response = await opponentsApi.getAll()
      setOpponents(response.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOpponent = async (opponentData) => {
    try {
      await opponentsApi.create(opponentData)
      setShowCreateModal(false)
      loadOpponents()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEditOpponent = async (opponentData) => {
    try {
      await opponentsApi.update(selectedOpponent.id, opponentData)
      setShowEditModal(false)
      setSelectedOpponent(null)
      loadOpponents()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteOpponent = async (opponentId) => {
    try {
      await opponentsApi.delete(opponentId)
      setDeleteConfirm(null)
      loadOpponents()
    } catch (err) {
      setError(err.message)
    }
  }

  const getDifficultyColor = (rating) => {
    if (rating >= 4.5) return 'bg-red-500/10 text-red-400'
    if (rating >= 4.0) return 'bg-orange-500/10 text-orange-400'
    if (rating >= 3.0) return 'bg-yellow-500/10 text-yellow-400'
    if (rating >= 2.0) return 'bg-accent-cyan/10 text-accent-cyan'
    return 'bg-pitch-500/10 text-pitch-400'
  }

  const getDifficultyLabel = (rating) => {
    if (rating >= 4.5) return 'Muito Difícil'
    if (rating >= 4.0) return 'Difícil'
    if (rating >= 3.0) return 'Médio'
    if (rating >= 2.0) return 'Fácil'
    return 'Muito Fácil'
  }

  const filteredOpponents = opponents.filter(opponent =>
    opponent.opponent_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return <div className="text-center py-12 text-gray-400">Carregando adversários...</div>
  }

  if (error) {
    return <div className="text-red-400 py-12">Erro: {error}</div>
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-white">Gestão de Adversários</h1>
          <p className="mt-2 text-sm text-gray-400">
            Gerir características e dificuldade dos adversários
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center rounded-md bg-pitch-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-pitch-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-pitch-600"
          >
            <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
            Novo Adversário
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-white/10 rounded-md leading-5 bg-dark-400 text-gray-200 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-pitch-500 focus:border-pitch-500"
            placeholder="Pesquisar adversários..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>
      
      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-white/10 sm:rounded-xl">
              <table className="min-w-full divide-y divide-white/5">
                <thead className="bg-dark-300">
                  <tr>
                    <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-400 sm:pl-6">
                      Adversário
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Posição Liga
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Dificuldade
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Forma Recente
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Histórico H2H
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Complexidade
                    </th>
                    <th className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span className="sr-only">Ações</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 bg-dark-200">
                  {filteredOpponents.map((opponent) => (
                    <tr key={opponent.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-200 sm:pl-6">
                        <div className="flex items-center">
                          <div>
                            <div className="font-medium text-gray-200">{opponent.opponent_name}</div>
                            {opponent.home_advantage && (
                              <div className="text-xs text-accent-cyan">Vantagem Casa</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        {opponent.league_position}º
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getDifficultyColor(opponent.overall_rating)}`}>
                          {getDifficultyLabel(opponent.overall_rating)} ({opponent.overall_rating})
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        {opponent.recent_form_points} pts
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        {opponent.head_to_head_record}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        <div className="flex space-x-1">
                          <span className="text-xs bg-dark-300 px-2 py-1 rounded border border-white/10">
                            T: {opponent.tactical_difficulty}
                          </span>
                          <span className="text-xs bg-dark-300 px-2 py-1 rounded border border-white/10">
                            F: {opponent.physical_intensity}
                          </span>
                        </div>
                      </td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => {
                              setSelectedOpponent(opponent)
                              setShowEditModal(true)
                            }}
                            className="text-accent-cyan hover:text-accent-cyan/80"
                            title="Editar"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(opponent)}
                            className="text-red-400 hover:text-red-300"
                            title="Eliminar"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Create Opponent Modal */}
      {showCreateModal && (
        <OpponentModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateOpponent}
          title="Criar Novo Adversário"
        />
      )}

      {/* Edit Opponent Modal */}
      {showEditModal && selectedOpponent && (
        <OpponentModal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false)
            setSelectedOpponent(null)
          }}
          onSubmit={handleEditOpponent}
          opponent={selectedOpponent}
          title="Editar Adversário"
        />
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <DeleteConfirmModal
          isOpen={!!deleteConfirm}
          onClose={() => setDeleteConfirm(null)}
          onConfirm={handleDeleteOpponent}
          opponent={deleteConfirm}
        />
      )}
    </div>
  )
}

// Opponent Form Modal Component
function OpponentModal({ isOpen, onClose, onSubmit, opponent = null, title }) {
  const [formData, setFormData] = useState({
    opponent_name: opponent?.opponent_name || '',
    league_position: opponent?.league_position || '',
    recent_form_points: opponent?.recent_form_points || '',
    home_advantage: opponent?.home_advantage || false,
    head_to_head_record: opponent?.head_to_head_record || '',
    key_players_available: opponent?.key_players_available || '',
    tactical_difficulty: opponent?.tactical_difficulty || '',
    physical_intensity: opponent?.physical_intensity || '',
    overall_rating: opponent?.overall_rating || '',
    explanation: opponent?.explanation || ''
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    // Convert string numbers to integers/floats
    const cleanData = {
      ...formData,
      league_position: parseInt(formData.league_position),
      recent_form_points: parseInt(formData.recent_form_points),
      key_players_available: parseInt(formData.key_players_available),
      tactical_difficulty: parseInt(formData.tactical_difficulty),
      physical_intensity: parseInt(formData.physical_intensity),
      overall_rating: parseFloat(formData.overall_rating)
    }
    
    try {
      await onSubmit(cleanData)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border border-white/10 w-11/12 md:w-3/4 lg:w-2/3 shadow-lg rounded-xl bg-dark-200">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-white mb-4">{title}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400">Nome do Adversário *</label>
                <input
                  type="text"
                  required
                  value={formData.opponent_name}
                  onChange={(e) => setFormData({...formData, opponent_name: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                  placeholder="FC Porto"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Posição na Liga *</label>
                <input
                  type="number"
                  required
                  min="1"
                  max="20"
                  value={formData.league_position}
                  onChange={(e) => setFormData({...formData, league_position: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Pontos Forma Recente *</label>
                <input
                  type="number"
                  required
                  min="0"
                  max="15"
                  value={formData.recent_form_points}
                  onChange={(e) => setFormData({...formData, recent_form_points: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                  placeholder="Pontos nos últimos 5 jogos"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Histórico H2H *</label>
                <input
                  type="text"
                  required
                  value={formData.head_to_head_record}
                  onChange={(e) => setFormData({...formData, head_to_head_record: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                  placeholder="2W-1D-2L"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Jogadores-Chave Disponíveis *</label>
                <input
                  type="number"
                  required
                  min="0"
                  max="11"
                  value={formData.key_players_available}
                  onChange={(e) => setFormData({...formData, key_players_available: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Complexidade Tática *</label>
                <select
                  required
                  value={formData.tactical_difficulty}
                  onChange={(e) => setFormData({...formData, tactical_difficulty: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                >
                  <option value="">Selecionar...</option>
                  <option value="1">1 - Muito Baixa</option>
                  <option value="2">2 - Baixa</option>
                  <option value="3">3 - Média</option>
                  <option value="4">4 - Alta</option>
                  <option value="5">5 - Muito Alta</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Intensidade Física *</label>
                <select
                  required
                  value={formData.physical_intensity}
                  onChange={(e) => setFormData({...formData, physical_intensity: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                >
                  <option value="">Selecionar...</option>
                  <option value="1">1 - Muito Baixa</option>
                  <option value="2">2 - Baixa</option>
                  <option value="3">3 - Média</option>
                  <option value="4">4 - Alta</option>
                  <option value="5">5 - Muito Alta</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Classificação Geral *</label>
                <input
                  type="number"
                  required
                  min="1.0"
                  max="5.0"
                  step="0.1"
                  value={formData.overall_rating}
                  onChange={(e) => setFormData({...formData, overall_rating: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                  placeholder="1.0 - 5.0"
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.home_advantage}
                  onChange={(e) => setFormData({...formData, home_advantage: e.target.checked})}
                  className="h-4 w-4 text-pitch-600 focus:ring-pitch-500 border-white/10 rounded bg-dark-400"
                />
                <label className="ml-2 block text-sm text-gray-300">
                  Vantagem de jogar em casa
                </label>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Explicação</label>
              <textarea
                rows={3}
                value={formData.explanation}
                onChange={(e) => setFormData({...formData, explanation: e.target.value})}
                className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                placeholder="Análise detalhada do adversário..."
              />
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-300 bg-dark-300 rounded-md hover:bg-dark-50 border border-white/10"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-pitch-600 rounded-md hover:bg-pitch-700 disabled:opacity-50"
              >
                {loading ? 'Guardando...' : (opponent ? 'Atualizar' : 'Criar')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

// Delete Confirmation Modal
function DeleteConfirmModal({ isOpen, onClose, onConfirm, opponent }) {
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm(opponent.id)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border border-white/10 w-96 shadow-lg rounded-xl bg-dark-200">
        <div className="mt-3 text-center">
          <h3 className="text-lg font-medium text-white mb-4">
            Eliminar Adversário
          </h3>
          <p className="text-sm text-gray-400 mb-4">
            Tem a certeza que pretende eliminar <strong className="text-white">{opponent.opponent_name}</strong>?
          </p>
          <p className="text-xs text-yellow-400 mb-4">
            Nota: Se este adversário estiver associado a sessões, não será eliminado.
          </p>
          <div className="flex justify-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-300 bg-dark-300 rounded-md hover:bg-dark-50 border border-white/10"
            >
              Cancelar
            </button>
            <button
              onClick={handleConfirm}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {loading ? 'Eliminando...' : 'Eliminar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
