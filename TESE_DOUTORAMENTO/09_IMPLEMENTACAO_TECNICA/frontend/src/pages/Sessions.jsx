import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { sessionsApi, ingestionApi, computerVisionApi } from '../api/client'
import { PlusIcon, PencilIcon, TrashIcon, EyeIcon, ArrowUpTrayIcon, CalendarIcon } from '@heroicons/react/24/outline'
import ComputerVisionResults from '../components/ComputerVisionResults'
import ComputerVisionMonitor from '../components/ComputerVisionMonitor'
import VideoAnalysisDashboard from '../components/VideoAnalysisDashboard'

export default function Sessions() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedSession, setSelectedSession] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [selectedSessions, setSelectedSessions] = useState([])
  const [batchDeleteConfirm, setBatchDeleteConfirm] = useState(false)
  const [uploadHistory, setUploadHistory] = useState([])
  const [activeTab, setActiveTab] = useState('sessions')
  const [selectedSessionForCV, setSelectedSessionForCV] = useState(null)
  const [uploadProgress, setUploadProgress] = useState({ video: 0, gps: 0, pse: 0 })
  const [uploadStatus, setUploadStatus] = useState('')
  const [cvMonitor, setCvMonitor] = useState({ isOpen: false, analysisId: null })

  useEffect(() => {
    loadSessions()
    loadUploadHistory()
  }, [])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await sessionsApi.getAll()
      setSessions(response.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadUploadHistory = async () => {
    try {
      const response = await ingestionApi.getHistory()
      setUploadHistory(response.data)
    } catch (err) {
      console.error('Error loading upload history:', err)
    }
  }

  const handleCreateSession = async (sessionData, uploadFiles, uploadAfterCreate, videoAnalysisSettings) => {
    try {
      console.log('🔍 Creating session with data:', sessionData)
      console.log('🔍 Upload files:', uploadFiles)
      console.log('🔍 Upload after create:', uploadAfterCreate)
      console.log('🔍 Video analysis settings:', videoAnalysisSettings)
      
      const response = await sessionsApi.create(sessionData)
      console.log('✅ Session created:', response.data)
      const createdSession = response.data
      
      // If user wants to upload files after creating session
      if (uploadAfterCreate && (uploadFiles.gps || uploadFiles.pse || uploadFiles.video)) {
        const sessionDate = sessionData.data
        const jornada = sessionData.jornada || 1
        
        // Upload GPS file if provided
        if (uploadFiles.gps) {
          await ingestionApi.uploadCatapult(uploadFiles.gps, jornada, sessionDate)
        }
        
        // Upload PSE file if provided
        if (uploadFiles.pse) {
          await ingestionApi.uploadPSE(uploadFiles.pse, jornada, sessionDate)
        }
        
        // Upload video for computer vision analysis if provided
        if (uploadFiles.video) {
          console.log('🎬 Starting video upload...')
          console.log('   File:', uploadFiles.video.name, uploadFiles.video.size, 'bytes')
          console.log('   Session ID:', createdSession.id)
          console.log('   Settings:', videoAnalysisSettings)
          
          setUploadStatus('Uploading video...')
          
          const videoResponse = await computerVisionApi.uploadVideo(
            uploadFiles.video,
            createdSession.id,
            videoAnalysisSettings.analysisType,
            videoAnalysisSettings.confidenceThreshold,
            videoAnalysisSettings.sampleRate,
            (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              setUploadProgress(prev => ({ ...prev, video: percentCompleted }))
              setUploadStatus(`Uploading video: ${percentCompleted}%`)
            }
          )
          console.log('✅ Video upload response:', videoResponse.data)
          setUploadStatus('Video uploaded successfully!')
          
          // Open computer vision monitor when video upload completes
          if (videoResponse.data && videoResponse.data.analysis_id) {
            setCvMonitor({ 
              isOpen: true, 
              analysisId: videoResponse.data.analysis_id 
            })
          }
        }
        
        // Refresh upload history
        loadUploadHistory()
      }
      
      // Only close modal if no uploads are happening
      if (!uploadAfterCreate || (!uploadFiles.gps && !uploadFiles.pse && !uploadFiles.video)) {
        setShowCreateModal(false)
      }
      loadSessions()
    } catch (err) {
      console.error('❌ Session creation error:', err)
      console.error('   Error details:', err.response?.data || err.message)
      setError(err.message)
      setUploadStatus('Upload failed: ' + err.message)
    } finally {
      setLoading(false)
      // Close modal after uploads complete
      setTimeout(() => {
        setShowCreateModal(false)
        setUploadStatus('')
        setUploadProgress({ video: 0, gps: 0, pse: 0 })
      }, 2000)
    }
  }

  const handleEditSession = async (sessionData, uploadFiles, uploadAfterCreate, videoAnalysisSettings) => {
    try {
      await sessionsApi.update(selectedSession.id, sessionData)
      
      // If user wants to upload files after updating session
      if (uploadAfterCreate && (uploadFiles.gps || uploadFiles.pse || uploadFiles.video)) {
        const sessionDate = sessionData.data || selectedSession.data
        const jornada = sessionData.jornada || selectedSession.jornada || 1
        
        // Upload GPS file if provided
        if (uploadFiles.gps) {
          await ingestionApi.uploadCatapult(uploadFiles.gps, jornada, sessionDate)
        }
        
        // Upload PSE file if provided
        if (uploadFiles.pse) {
          await ingestionApi.uploadPSE(uploadFiles.pse, jornada, sessionDate)
        }
        
        // Upload video for computer vision analysis if provided
        if (uploadFiles.video) {
          await computerVisionApi.uploadVideo(
            uploadFiles.video,
            selectedSession.id,
            videoAnalysisSettings.analysisType,
            videoAnalysisSettings.confidenceThreshold,
            videoAnalysisSettings.sampleRate
          )
        }
        
        // Refresh upload history
        loadUploadHistory()
      }
      
      setShowEditModal(false)
      setSelectedSession(null)
      loadSessions()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDeleteSession = async (sessionId) => {
    try {
      await sessionsApi.delete(sessionId)
      setDeleteConfirm(null)
      loadSessions()
      loadUploadHistory()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleBatchDelete = async () => {
    try {
      setLoading(true)
      // Delete all selected sessions
      await Promise.all(selectedSessions.map(id => sessionsApi.delete(id)))
      setSelectedSessions([])
      setBatchDeleteConfirm(false)
      loadSessions()
      loadUploadHistory()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const toggleSessionSelection = (sessionId) => {
    setSelectedSessions(prev => 
      prev.includes(sessionId) 
        ? prev.filter(id => id !== sessionId)
        : [...prev, sessionId]
    )
  }

  const toggleSelectAll = () => {
    if (selectedSessions.length === sessions.length) {
      setSelectedSessions([])
    } else {
      setSelectedSessions(sessions.map(s => s.id))
    }
  }


  if (loading) {
    return <div className="text-center py-12 text-gray-400">Carregando sessões...</div>
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-white">Gestão de Sessões</h1>
          <p className="mt-2 text-sm text-gray-400">
            Gerir sessões, carregar dados e acompanhar histórico
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center rounded-md bg-pitch-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-pitch-700"
          >
            <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
            Nova Sessão
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mt-6">
        <div className="border-b border-white/10">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('sessions')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'sessions'
                  ? 'border-pitch-500 text-pitch-400'
                  : 'border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-600'
              }`}
            >
              <CalendarIcon className="w-5 h-5 inline mr-2" />
              Sessões ({sessions.length})
            </button>
            <button
              onClick={() => setActiveTab('uploads')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'uploads'
                  ? 'border-pitch-500 text-pitch-400'
                  : 'border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-600'
              }`}
            >
              <ArrowUpTrayIcon className="w-5 h-5 inline mr-2" />
              Histórico Uploads ({uploadHistory.length})
            </button>
            <button
              onClick={() => setActiveTab('computer-vision')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'computer-vision'
                  ? 'border-pitch-500 text-pitch-400'
                  : 'border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-600'
              }`}
            >
              <EyeIcon className="w-5 h-5 inline mr-2" />
              Análise de Vídeo
            </button>
          </nav>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-md">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {/* Sessions Tab */}
      {activeTab === 'sessions' && (
        <>
          {selectedSessions.length > 0 && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-sm font-medium text-red-400">
                  {selectedSessions.length} sessão(ões) selecionada(s)
                </span>
                <button
                  onClick={() => setSelectedSessions([])}
                  className="text-xs text-gray-400 hover:text-gray-200"
                >
                  Limpar seleção
                </button>
              </div>
              <button
                onClick={() => setBatchDeleteConfirm(true)}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 border border-red-500/30"
              >
                <TrashIcon className="w-4 h-4 mr-2" />
                Eliminar Selecionadas
              </button>
            </div>
          )}
          <SessionsTable 
            sessions={sessions}
            selectedSessions={selectedSessions}
            onToggleSelection={toggleSessionSelection}
            onToggleSelectAll={toggleSelectAll}
            onEdit={(session) => {
              setSelectedSession(session)
              setShowEditModal(true)
            }}
            onDelete={(session) => setDeleteConfirm(session)}
          />
        </>
      )}

      {/* Uploads Tab */}
      {activeTab === 'uploads' && (
        <UploadsTable 
          uploads={uploadHistory}
          onDeleteSession={handleDeleteSession}
        />
      )}

      {/* Computer Vision Tab */}
      {activeTab === 'computer-vision' && (
        <div className="mt-8 space-y-6">
          {/* Video Analysis Dashboard - Always visible at top */}
          <VideoAnalysisDashboard />
          
          {/* Session-specific results */}
          {selectedSessionForCV ? (
            <div>
              <div className="mb-4">
                <button
                  onClick={() => setSelectedSessionForCV(null)}
                  className="text-sm text-gray-400 hover:text-gray-200"
                >
                  ← Voltar à lista
                </button>
              </div>
              <h3 className="text-lg font-medium text-white mb-4">
                Session {selectedSessionForCV} - Detailed Analysis
              </h3>
              <ComputerVisionResults sessionId={selectedSessionForCV} />
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-medium text-white mb-4">Selecionar Sessão para Análise de Vídeo</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => setSelectedSessionForCV(session.id)}
                    className="card-dark border border-white/5 rounded-lg p-4 cursor-pointer hover:border-pitch-500/30 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        session.tipo === 'jogo' ? 'bg-red-500/10 text-red-400' :
                        session.tipo === 'recuperacao' ? 'bg-pitch-500/10 text-pitch-400' : 'bg-accent-cyan/10 text-accent-cyan'
                      }`}>
                        {session.tipo === 'jogo' ? '⚽ Jogo' :
                         session.tipo === 'recuperacao' ? '💆 Recuperação' : '🏃 Treino'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(session.data).toLocaleDateString('pt-PT')}
                      </span>
                    </div>
                    <div className="text-sm font-medium text-gray-200 mb-1">
                      {session.adversario || 'Treino'}
                    </div>
                    <div className="text-xs text-gray-500">
                      Duração: {session.duracao_min} min • {session.local}
                    </div>
                    {session.resultado && (
                      <div className="text-xs text-gray-400 mt-1">
                        Resultado: {session.resultado}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      {showCreateModal && (
        <SessionModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateSession}
          title="Criar Nova Sessão"
          uploadProgress={uploadProgress}
          uploadStatus={uploadStatus}
        />
      )}

      {showEditModal && selectedSession && (
        <SessionModal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false)
            setSelectedSession(null)
          }}
          onSubmit={handleEditSession}
          session={selectedSession}
          title="Editar Sessão"
          uploadProgress={uploadProgress}
          uploadStatus={uploadStatus}
        />
      )}


      {deleteConfirm && (
        <DeleteConfirmModal
          isOpen={!!deleteConfirm}
          onClose={() => setDeleteConfirm(null)}
          onConfirm={handleDeleteSession}
          session={deleteConfirm}
        />
      )}

      {batchDeleteConfirm && (
        <BatchDeleteConfirmModal
          isOpen={batchDeleteConfirm}
          onClose={() => setBatchDeleteConfirm(false)}
          onConfirm={handleBatchDelete}
          count={selectedSessions.length}
        />
      )}

      {/* Computer Vision Monitor */}
      <ComputerVisionMonitor
        isOpen={cvMonitor.isOpen}
        analysisId={cvMonitor.analysisId}
        onClose={() => setCvMonitor({ isOpen: false, analysisId: null })}
      />
    </div>
  )
}

// Sessions Table Component
function SessionsTable({ sessions, selectedSessions, onToggleSelection, onToggleSelectAll, onEdit, onDelete }) {
  const allSelected = sessions.length > 0 && selectedSessions.length === sessions.length
  const someSelected = selectedSessions.length > 0 && selectedSessions.length < sessions.length

  return (
    <div className="mt-8 flow-root">
      <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
          <div className="overflow-hidden shadow ring-1 ring-white/5 sm:rounded-lg">
            <table className="min-w-full divide-y divide-white/5">
              <thead className="bg-dark-300">
                <tr>
                  <th className="py-3.5 pl-4 pr-3 sm:pl-6 w-12">
                    <input
                      type="checkbox"
                      checked={allSelected}
                      ref={input => {
                        if (input) {
                          input.indeterminate = someSelected
                        }
                      }}
                      onChange={onToggleSelectAll}
                      className="h-4 w-4 rounded border-white/10 bg-dark-400 text-pitch-600 focus:ring-pitch-500 cursor-pointer"
                    />
                  </th>
                  <th className="py-3.5 px-3 text-left text-sm font-semibold text-gray-400">Data</th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">Tipo</th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">Adversário</th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">Jornada</th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-400">Resultado</th>
                  <th className="relative py-3.5 pl-3 pr-4 sm:pr-6"><span className="sr-only">Ações</span></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 bg-dark-200">
                {sessions.map((session) => (
                  <tr key={session.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 sm:pl-6 w-12">
                      <input
                        type="checkbox"
                        checked={selectedSessions.includes(session.id)}
                        onChange={() => onToggleSelection(session.id)}
                        className="h-4 w-4 rounded border-white/10 bg-dark-400 text-pitch-600 focus:ring-pitch-500 cursor-pointer"
                      />
                    </td>
                    <td className="whitespace-nowrap py-4 px-3 text-sm font-medium text-gray-200">
                      {new Date(session.data).toLocaleDateString('pt-PT')}
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm">
                      <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        session.tipo === 'jogo' ? 'bg-red-500/10 text-red-400' :
                        session.tipo === 'recuperacao' ? 'bg-pitch-500/10 text-pitch-400' :
                        'bg-accent-cyan/10 text-accent-cyan'
                      }`}>
                        {session.tipo === 'jogo' ? '⚽ Jogo' :
                         session.tipo === 'recuperacao' ? '💆 Recuperação' : '🏃 Treino'}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">{session.adversario || '-'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">{session.jornada || '-'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-400">{session.resultado || '-'}</td>
                    <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                      <div className="flex items-center justify-end space-x-2">
                        <Link to={`/sessions/${session.id}`} className="text-accent-cyan hover:text-accent-cyan/80" title="Ver detalhes">
                          <EyeIcon className="h-4 w-4" />
                        </Link>
                        <button onClick={() => onEdit(session)} className="text-accent-gold hover:text-accent-gold/80" title="Editar">
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button onClick={() => onDelete(session)} className="text-red-400 hover:text-red-300" title="Eliminar">
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
  )
}

// Uploads Table Component  
function UploadsTable({ uploads, onDeleteSession }) {
  return (
    <div className="mt-8 space-y-4">
      {uploads.map((item, idx) => (
        <div key={idx} className="card-dark rounded-lg p-4 border border-white/5">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium text-gray-200">{item.fonte}</p>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  item.tipo_dados === 'GPS' ? 'bg-accent-cyan/10 text-accent-cyan' : 'bg-pitch-500/10 text-pitch-400'
                }`}>
                  {item.tipo_dados}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Sessão #{item.sessao_id} • {item.data} • {item.num_records} registos
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {new Date(item.ingested_at).toLocaleString('pt-PT')}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Link to={`/sessions/${item.sessao_id}`} className="p-1 text-accent-cyan hover:bg-white/5 rounded" title="Ver sessão">
                <EyeIcon className="h-4 w-4" />
              </Link>
              <button onClick={() => onDeleteSession(item.sessao_id)} className="p-1 text-red-400 hover:bg-red-500/10 rounded" title="Eliminar sessão">
                <TrashIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

// Session Modal Component
function SessionModal({ isOpen, onClose, onSubmit, session = null, title, uploadProgress, uploadStatus }) {
  const [formData, setFormData] = useState({
    data: session?.data || '',
    tipo: session?.tipo || 'treino',
    adversario: session?.adversario || '',
    jornada: session?.jornada || '',
    resultado: session?.resultado || '',
    duracao_min: session?.duracao_min || 90,
    local: session?.local || 'casa',
    competicao: session?.competicao || ''
  })
  const [loading, setLoading] = useState(false)
  const [uploadFiles, setUploadFiles] = useState({ gps: null, pse: null, video: null })
  const [uploadAfterCreate, setUploadAfterCreate] = useState(false)
  const [videoAnalysisSettings, setVideoAnalysisSettings] = useState({
    analysisType: 'full',
    confidenceThreshold: 0.5,
    sampleRate: 1
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      // Ensure proper data types for API
      const processedFormData = {
        ...formData,
        duracao_min: parseInt(formData.duracao_min) || 90,
        jornada: formData.jornada ? parseInt(formData.jornada) : null
      }
      const createdSession = await onSubmit(processedFormData, uploadFiles, uploadAfterCreate, videoAnalysisSettings)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border border-white/10 w-11/12 md:w-2/3 shadow-lg rounded-xl bg-dark-200">
        <h3 className="text-lg font-medium text-white mb-4">{title}</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400">Data *</label>
              <input type="date" required value={formData.data} onChange={(e) => setFormData({...formData, data: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Tipo *</label>
              <select required value={formData.tipo} onChange={(e) => setFormData({...formData, tipo: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500">
                <option value="treino">Treino</option>
                <option value="jogo">Jogo</option>
                <option value="recuperacao">Recuperação</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Adversário</label>
              <input type="text" value={formData.adversario} onChange={(e) => setFormData({...formData, adversario: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500" placeholder="Nome do adversário (se jogo)" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Jornada</label>
              <input type="number" value={formData.jornada} onChange={(e) => setFormData({...formData, jornada: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Resultado</label>
              <input type="text" value={formData.resultado} onChange={(e) => setFormData({...formData, resultado: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500" placeholder="2-1, 0-0, etc." />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Duração (min)</label>
              <input type="number" value={formData.duracao_min} onChange={(e) => setFormData({...formData, duracao_min: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Local</label>
              <select value={formData.local} onChange={(e) => setFormData({...formData, local: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500">
                <option value="casa">Casa</option>
                <option value="fora">Fora</option>
                <option value="neutro">Neutro</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400">Competição/Descrição</label>
              <input type="text" value={formData.competicao} onChange={(e) => setFormData({...formData, competicao: e.target.value})} className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500" placeholder="Liga, Taça, etc." />
            </div>
          </div>
          
          {/* File Upload Section */}
          <div className="mt-6 border-t border-white/10 pt-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-medium text-white">Carregar Dados da Sessão</h4>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={uploadAfterCreate}
                  onChange={(e) => setUploadAfterCreate(e.target.checked)}
                  className="h-4 w-4 text-pitch-600 focus:ring-pitch-500 border-white/10 rounded bg-dark-400"
                />
                <span className="ml-2 text-sm text-gray-400">Carregar ficheiros após criar sessão</span>
              </label>
            </div>
            
            {uploadAfterCreate && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400">Dados GPS (Catapult)</label>
                    <input
                      type="file"
                      accept=".csv,.pdf,.png,.jpg,.jpeg,.gif,.bmp,.webp"
                      onChange={(e) => setUploadFiles({...uploadFiles, gps: e.target.files[0]})}
                      className="mt-1 block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-accent-cyan/10 file:text-accent-cyan hover:file:bg-accent-cyan/20"
                    />
                    {uploadFiles.gps && (
                      <p className="mt-1 text-xs text-green-600">✓ {uploadFiles.gps.name}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-400">Dados PSE (Wellness)</label>
                    <input
                      type="file"
                      accept=".csv,.pdf,.png,.jpg,.jpeg,.gif,.bmp,.webp"
                      onChange={(e) => setUploadFiles({...uploadFiles, pse: e.target.files[0]})}
                      className="mt-1 block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-pitch-500/10 file:text-pitch-400 hover:file:bg-pitch-500/20"
                    />
                    {uploadFiles.pse && (
                      <p className="mt-1 text-xs text-green-600">✓ {uploadFiles.pse.name}</p>
                    )}
                  </div>
                </div>
                
                {/* Video Upload Section */}
                <div className="border-t border-white/10 pt-4">
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-400 mb-2">Vídeo para Análise de Visão Computacional</label>
                    <input
                      type="file"
                      accept=".mp4,.avi,.mov,.mkv,.wmv"
                      onChange={(e) => setUploadFiles({...uploadFiles, video: e.target.files[0]})}
                      className="mt-1 block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-500/10 file:text-purple-400 hover:file:bg-purple-500/20"
                    />
                    {uploadFiles.video && (
                      <p className="mt-1 text-xs text-green-600">✓ {uploadFiles.video.name}</p>
                    )}
                  </div>
                  
                  {uploadFiles.video && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 p-4 bg-dark-300/50 rounded-lg border border-white/5">
                      <div>
                        <label className="block text-sm font-medium text-gray-400">Tipo de Análise</label>
                        <select
                          value={videoAnalysisSettings.analysisType}
                          onChange={(e) => setVideoAnalysisSettings({...videoAnalysisSettings, analysisType: e.target.value})}
                          className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-purple-500 focus:ring-purple-500 text-sm"
                        >
                          <option value="full">Completa (mais lenta)</option>
                          <option value="quick">Rápida (amostragem)</option>
                          <option value="ball_only">Apenas Bola</option>
                          <option value="players_only">Apenas Jogadores</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-400">Confiança</label>
                        <select
                          value={videoAnalysisSettings.confidenceThreshold}
                          onChange={(e) => setVideoAnalysisSettings({...videoAnalysisSettings, confidenceThreshold: parseFloat(e.target.value)})}
                          className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-purple-500 focus:ring-purple-500 text-sm"
                        >
                          <option value={0.3}>Baixa (30%)</option>
                          <option value={0.5}>Média (50%)</option>
                          <option value={0.7}>Alta (70%)</option>
                          <option value={0.9}>Muito Alta (90%)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-400">Taxa de Amostragem</label>
                        <select
                          value={videoAnalysisSettings.sampleRate}
                          onChange={(e) => setVideoAnalysisSettings({...videoAnalysisSettings, sampleRate: parseInt(e.target.value)})}
                          className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-purple-500 focus:ring-purple-500 text-sm"
                        >
                          <option value={1}>Todos os frames</option>
                          <option value={2}>Cada 2º frame</option>
                          <option value={5}>Cada 5º frame</option>
                          <option value={10}>Cada 10º frame</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Upload Progress Indicator */}
          {loading && uploadAfterCreate && (uploadFiles.gps || uploadFiles.pse || uploadFiles.video) && (
            <div className="mt-4 p-4 bg-accent-cyan/5 rounded-lg border border-accent-cyan/20">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-accent-cyan">Upload Progress</span>
                <span className="text-sm text-gray-400">{uploadStatus}</span>
              </div>
              
              {uploadFiles.video && (
                <div className="mb-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Video ({uploadFiles.video.name})</span>
                    <span>{uploadProgress.video}%</span>
                  </div>
                  <div className="w-full bg-dark-400 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${uploadProgress.video}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {uploadFiles.gps && (
                <div className="mb-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>GPS ({uploadFiles.gps.name})</span>
                    <span>{uploadProgress.gps}%</span>
                  </div>
                  <div className="w-full bg-dark-400 rounded-full h-2">
                    <div 
                      className="bg-accent-cyan h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${uploadProgress.gps}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              {uploadFiles.pse && (
                <div className="mb-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>PSE ({uploadFiles.pse.name})</span>
                    <span>{uploadProgress.pse}%</span>
                  </div>
                  <div className="w-full bg-dark-400 rounded-full h-2">
                    <div 
                      className="bg-pitch-500 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${uploadProgress.pse}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onClose} disabled={loading} className="px-4 py-2 text-sm font-medium text-gray-300 bg-dark-300 rounded-md hover:bg-dark-50 border border-white/10 disabled:opacity-50">Cancelar</button>
            <button type="submit" disabled={loading} className="px-4 py-2 text-sm font-medium text-white bg-pitch-600 rounded-md hover:bg-pitch-700 disabled:opacity-50">
              {loading ? (uploadAfterCreate && (uploadFiles.gps || uploadFiles.pse || uploadFiles.video) ? 'Criando e Carregando...' : 'Guardando...') : (session ? 'Atualizar' : 'Criar')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


// Delete Confirmation Modal
function DeleteConfirmModal({ isOpen, onClose, onConfirm, session }) {
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm(session.id)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border border-white/10 w-96 shadow-lg rounded-xl bg-dark-200">
        <div className="mt-3 text-center">
          <h3 className="text-lg font-medium text-white mb-4">Eliminar Sessão</h3>
          <p className="text-sm text-gray-400 mb-4">Tem a certeza que pretende eliminar esta sessão? Todos os dados GPS e PSE associados serão também eliminados.</p>
          <div className="flex justify-center space-x-3">
            <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-300 bg-dark-300 rounded-md hover:bg-dark-50 border border-white/10">Cancelar</button>
            <button onClick={handleConfirm} disabled={loading} className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 border border-red-500/30">
              {loading ? 'Eliminando...' : 'Eliminar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Batch Delete Confirmation Modal
function BatchDeleteConfirmModal({ isOpen, onClose, onConfirm, count }) {
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm()
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border border-red-500/20 w-96 shadow-lg rounded-xl bg-dark-200">
        <div className="mt-3 text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-500/10 mb-4">
            <TrashIcon className="h-6 w-6 text-red-500" />
          </div>
          <h3 className="text-lg font-medium text-white mb-4">Eliminar {count} Sessões</h3>
          <p className="text-sm text-gray-400 mb-4">
            Tem a certeza que pretende eliminar <span className="font-semibold text-red-400">{count} sessões</span>? 
            Todos os dados GPS, PSE e de vídeo associados a estas sessões serão também eliminados.
          </p>
          <p className="text-xs text-red-400/80 mb-4">
            ⚠️ Esta ação não pode ser revertida
          </p>
          <div className="flex justify-center space-x-3">
            <button 
              onClick={onClose} 
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-300 bg-dark-300 rounded-md hover:bg-dark-50 border border-white/10 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button 
              onClick={handleConfirm} 
              disabled={loading} 
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 border border-red-500/30"
            >
              {loading ? 'Eliminando...' : `Eliminar ${count} Sessões`}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
