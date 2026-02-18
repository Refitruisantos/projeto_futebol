import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { athletesApi } from '../api/client'
import { PlusIcon, PencilIcon, TrashIcon, EyeIcon, UserPlusIcon } from '@heroicons/react/24/outline'

export default function Athletes() {
  const [athletes, setAthletes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedAthlete, setSelectedAthlete] = useState(null)
  const [showInactive, setShowInactive] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  useEffect(() => {
    loadAthletes()
  }, [showInactive])

  const loadAthletes = async () => {
    try {
      setLoading(true)
      const response = await athletesApi.getAll({ ativo: !showInactive })
      setAthletes(response.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAthlete = async (athleteData) => {
    try {
      await athletesApi.create(athleteData)
      setShowCreateModal(false)
      loadAthletes()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEditAthlete = async (athleteData) => {
    try {
      await athletesApi.update(selectedAthlete.id, athleteData)
      setShowEditModal(false)
      setSelectedAthlete(null)
      loadAthletes()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteAthlete = async (athleteId, permanent = false) => {
    try {
      await athletesApi.delete(athleteId, { permanent })
      setDeleteConfirm(null)
      loadAthletes()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleReactivateAthlete = async (athleteId) => {
    try {
      await athletesApi.reactivate(athleteId)
      loadAthletes()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return <div className="text-center py-12 text-gray-400">Carregando atletas...</div>
  }

  if (error) {
    return <div className="text-red-400 py-12">Erro: {error}</div>
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-white">Gestão de Atletas</h1>
          <p className="mt-2 text-sm text-gray-400">
            Gerir atletas, criar novos perfis e acompanhar jornadas
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none space-x-3">
          <button
            type="button"
            onClick={() => setShowInactive(!showInactive)}
            className="inline-flex items-center rounded-md bg-dark-50 px-3 py-2 text-sm font-semibold text-gray-300 shadow-sm hover:bg-dark-300 border border-white/10"
          >
            {showInactive ? 'Ver Ativos' : 'Ver Inativos'}
          </button>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center rounded-md bg-pitch-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-pitch-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-pitch-600"
          >
            <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
            Novo Atleta
          </button>
        </div>
      </div>
      
      <div className="mt-8 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <div className="overflow-hidden shadow ring-1 ring-white/5 sm:rounded-lg">
              <table className="min-w-full divide-y divide-white/5">
                <thead className="bg-dark-300">
                  <tr>
                    <th className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-400 sm:pl-6">
                      Nome
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      ID
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Posição
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Nº
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Altura/Peso
                    </th>
                    <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">
                      Estado
                    </th>
                    <th className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                      <span className="sr-only">Ações</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 bg-dark-200">
                  {athletes.map((athlete) => (
                    <tr key={athlete.id} className={`hover:bg-white/[0.02] transition-colors ${!athlete.ativo ? 'opacity-60' : ''}`}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-200 sm:pl-6">
                        {athlete.nome_completo}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        {athlete.jogador_id}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        {athlete.posicao || '-'}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        {athlete.numero_camisola || '-'}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">
                        {athlete.altura_cm ? `${athlete.altura_cm}cm` : '-'}
                        {athlete.massa_kg ? ` / ${athlete.massa_kg}kg` : ''}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm">
                        {athlete.ativo ? (
                          <span className="inline-flex items-center rounded-full bg-pitch-500/10 px-2.5 py-0.5 text-xs font-medium text-pitch-400 border border-pitch-500/20">
                            Ativo
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-medium text-red-400 border border-red-500/20">
                            Inativo
                          </span>
                        )}
                      </td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <div className="flex items-center justify-end space-x-2">
                          <Link
                            to={`/athletes/${athlete.id}`}
                            className="text-accent-cyan hover:text-accent-cyan/80"
                            title="Ver detalhes"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </Link>
                          <button
                            onClick={() => {
                              setSelectedAthlete(athlete)
                              setShowEditModal(true)
                            }}
                            className="text-accent-gold hover:text-accent-gold/80"
                            title="Editar"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          {athlete.ativo ? (
                            <button
                              onClick={() => setDeleteConfirm(athlete)}
                              className="text-red-400 hover:text-red-300"
                              title="Desativar/Eliminar"
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleReactivateAthlete(athlete.id)}
                              className="text-pitch-400 hover:text-pitch-300"
                              title="Reativar"
                            >
                              <UserPlusIcon className="h-4 w-4" />
                            </button>
                          )}
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

      {/* Create Athlete Modal */}
      {showCreateModal && (
        <AthleteModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateAthlete}
          title="Criar Novo Atleta"
        />
      )}

      {/* Edit Athlete Modal */}
      {showEditModal && selectedAthlete && (
        <AthleteModal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false)
            setSelectedAthlete(null)
          }}
          onSubmit={handleEditAthlete}
          athlete={selectedAthlete}
          title="Editar Atleta"
        />
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <DeleteConfirmModal
          isOpen={!!deleteConfirm}
          onClose={() => setDeleteConfirm(null)}
          onConfirm={handleDeleteAthlete}
          athlete={deleteConfirm}
        />
      )}
    </div>
  )
}

// Athlete Form Modal Component
function AthleteModal({ isOpen, onClose, onSubmit, athlete = null, title }) {
  const [formData, setFormData] = useState({
    jogador_id: athlete?.jogador_id || '',
    nome_completo: athlete?.nome_completo || '',
    data_nascimento: athlete?.data_nascimento || '',
    posicao: athlete?.posicao || '',
    numero_camisola: athlete?.numero_camisola || '',
    pe_dominante: athlete?.pe_dominante || '',
    altura_cm: athlete?.altura_cm || '',
    massa_kg: athlete?.massa_kg || ''
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    // Clean up empty values
    const cleanData = Object.fromEntries(
      Object.entries(formData).filter(([_, value]) => value !== '')
    )
    
    try {
      await onSubmit(cleanData)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border border-white/10 w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-xl bg-dark-200">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-white mb-4">{title}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-400">ID do Jogador *</label>
                <input
                  type="text"
                  required
                  value={formData.jogador_id}
                  onChange={(e) => setFormData({...formData, jogador_id: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                  placeholder="ATL001"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Nome Completo *</label>
                <input
                  type="text"
                  required
                  value={formData.nome_completo}
                  onChange={(e) => setFormData({...formData, nome_completo: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                  placeholder="João Silva"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Data de Nascimento</label>
                <input
                  type="date"
                  value={formData.data_nascimento}
                  onChange={(e) => setFormData({...formData, data_nascimento: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Posição</label>
                <select
                  value={formData.posicao}
                  onChange={(e) => setFormData({...formData, posicao: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                >
                  <option value="">Selecionar...</option>
                  <option value="GR">Guarda-Redes</option>
                  <option value="DC">Defesa Central</option>
                  <option value="DL">Defesa Lateral</option>
                  <option value="MC">Médio Centro</option>
                  <option value="EX">Extremo</option>
                  <option value="AV">Avançado</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Número da Camisola</label>
                <input
                  type="number"
                  min="1"
                  max="99"
                  value={formData.numero_camisola}
                  onChange={(e) => setFormData({...formData, numero_camisola: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Pé Dominante</label>
                <select
                  value={formData.pe_dominante}
                  onChange={(e) => setFormData({...formData, pe_dominante: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                >
                  <option value="">Selecionar...</option>
                  <option value="Direito">Direito</option>
                  <option value="Esquerdo">Esquerdo</option>
                  <option value="Ambidestro">Ambidestro</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Altura (cm)</label>
                <input
                  type="number"
                  min="150"
                  max="220"
                  value={formData.altura_cm}
                  onChange={(e) => setFormData({...formData, altura_cm: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Peso (kg)</label>
                <input
                  type="number"
                  min="40"
                  max="120"
                  step="0.1"
                  value={formData.massa_kg}
                  onChange={(e) => setFormData({...formData, massa_kg: e.target.value})}
                  className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500"
                />
              </div>
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
                {loading ? 'Guardando...' : (athlete ? 'Atualizar' : 'Criar')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

// Delete Confirmation Modal
function DeleteConfirmModal({ isOpen, onClose, onConfirm, athlete }) {
  const [permanent, setPermanent] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm(athlete.id, permanent)
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
            Eliminar Atleta
          </h3>
          <p className="text-sm text-gray-400 mb-4">
            Tem a certeza que pretende eliminar <strong>{athlete.nome_completo}</strong>?
          </p>
          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={permanent}
                onChange={(e) => setPermanent(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-gray-400">
                Eliminação permanente (apenas se não tiver dados associados)
              </span>
            </label>
          </div>
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
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 border border-red-500/30"
            >
              {loading ? 'Eliminando...' : (permanent ? 'Eliminar Permanentemente' : 'Desativar')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
