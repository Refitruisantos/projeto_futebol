import { useState, useEffect } from 'react'
import { ingestionApi } from '../api/client'
import { Upload as UploadIcon, CheckCircle, XCircle, Eye, Trash2 } from 'lucide-react'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [jornada, setJornada] = useState(1)
  const [sessionDate, setSessionDate] = useState('')
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [viewingSession, setViewingSession] = useState(null)
  const [sessionData, setSessionData] = useState(null)
  const [deletingSession, setDeletingSession] = useState(null)
  const [uploadType, setUploadType] = useState('gps')
  const [pseFile, setPseFile] = useState(null)
  const [pseUploading, setPseUploading] = useState(false)
  const [pseResult, setPseResult] = useState(null)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response = await ingestionApi.getHistory(10)
      setHistory(response.data)
    } catch (err) {
      console.error('Error loading history:', err)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const fileName = selectedFile.name.toLowerCase()
      const validExtensions = ['.csv', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
      const isValidFile = validExtensions.some(ext => fileName.endsWith(ext))
      
      if (isValidFile) {
        if (uploadType === 'gps') {
          setFile(selectedFile)
        } else {
          setPseFile(selectedFile)
        }
        setError(null)
      } else {
        setError('Por favor selecione um ficheiro CSV, PDF ou imagem (PNG, JPG, JPEG, GIF, BMP, WEBP)')
        if (uploadType === 'gps') {
          setFile(null)
        } else {
          setPseFile(null)
        }
      }
    }
  }

  const handlePseFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const fileName = selectedFile.name.toLowerCase()
      const validExtensions = ['.csv', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
      const isValidFile = validExtensions.some(ext => fileName.endsWith(ext))
      
      if (isValidFile) {
        setPseFile(selectedFile)
        setError(null)
      } else {
        setError('Por favor selecione um ficheiro CSV, PDF ou imagem (PNG, JPG, JPEG, GIF, BMP, WEBP)')
        setPseFile(null)
      }
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    
    const currentFile = uploadType === 'gps' ? file : pseFile
    if (!currentFile) {
      setError('Selecione um ficheiro')
      return
    }

    try {
      if (uploadType === 'gps') {
        setUploading(true)
      } else {
        setPseUploading(true)
      }
      setError(null)
      setResult(null)
      setPseResult(null)

      let response
      if (uploadType === 'gps') {
        response = await ingestionApi.uploadCatapult(file, jornada, sessionDate)
        setResult(response.data)
        setFile(null)
        document.getElementById('file-upload').value = ''
      } else {
        response = await ingestionApi.uploadPSE(pseFile, jornada, sessionDate)
        setPseResult(response.data)
        setPseFile(null)
        document.getElementById('pse-file-upload').value = ''
      }
      
      loadHistory()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      if (uploadType === 'gps') {
        setUploading(false)
      } else {
        setPseUploading(false)
      }
    }
  }

  const handleViewSession = async (sessionId) => {
    try {
      setViewingSession(sessionId)
      const response = await ingestionApi.getSessionData(sessionId)
      setSessionData(response.data)
    } catch (err) {
      setError(`Erro ao carregar dados da sessão: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Tem certeza que deseja eliminar esta sessão? Esta ação não pode ser desfeita.')) {
      return
    }

    try {
      setDeletingSession(sessionId)
      await ingestionApi.deleteSession(sessionId)
      setDeletingSession(null)
      loadHistory() // Refresh the history
      setError(null)
    } catch (err) {
      setDeletingSession(null)
      setError(`Erro ao eliminar sessão: ${err.response?.data?.detail || err.message}`)
    }
  }

  const closeModal = () => {
    setViewingSession(null)
    setSessionData(null)
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold text-white mb-6">Carregar Dados GPS</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-dark rounded-xl p-6 border border-white/5">
          <h2 className="text-lg font-medium text-white mb-4">
            Upload de Dados
          </h2>

          {/* Upload Type Selector */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Tipo de Dados
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center text-gray-300">
                <input
                  type="radio"
                  value="gps"
                  checked={uploadType === 'gps'}
                  onChange={(e) => setUploadType(e.target.value)}
                  className="mr-2 text-pitch-600 focus:ring-pitch-500"
                />
                GPS (Catapult)
              </label>
              <label className="flex items-center text-gray-300">
                <input
                  type="radio"
                  value="pse"
                  checked={uploadType === 'pse'}
                  onChange={(e) => setUploadType(e.target.value)}
                  className="mr-2 text-pitch-600 focus:ring-pitch-500"
                />
                PSE (Wellness)
              </label>
            </div>
          </div>

          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Ficheiro (CSV, PDF ou Imagem)
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-white/10 border-dashed rounded-md hover:border-pitch-500/30 transition-colors">
                <div className="space-y-1 text-center">
                  <UploadIcon className="mx-auto h-12 w-12 text-gray-500" />
                  <div className="flex text-sm text-gray-400">
                    <label
                      htmlFor={uploadType === 'gps' ? 'file-upload' : 'pse-file-upload'}
                      className="relative cursor-pointer rounded-md font-medium text-pitch-400 hover:text-pitch-300 focus-within:outline-none"
                    >
                      <span>Escolher ficheiro {uploadType === 'gps' ? 'GPS' : 'PSE'}</span>
                      <input
                        id={uploadType === 'gps' ? 'file-upload' : 'pse-file-upload'}
                        type="file"
                        className="sr-only"
                        accept=".csv,.pdf,.png,.jpg,.jpeg,.gif,.bmp,.webp"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>
                  {(uploadType === 'gps' ? file : pseFile) && (
                    <p className="text-xs text-gray-500">{(uploadType === 'gps' ? file : pseFile).name}</p>
                  )}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Jornada
              </label>
              <input
                type="number"
                min="1"
                value={jornada}
                onChange={(e) => setJornada(parseInt(e.target.value) || 1)}
                className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Data da Sessão (opcional)
              </label>
              <input
                type="date"
                value={sessionDate}
                onChange={(e) => setSessionDate(e.target.value)}
                className="mt-1 block w-full rounded-md bg-dark-400 border-white/10 text-gray-200 shadow-sm focus:border-pitch-500 focus:ring-pitch-500 sm:text-sm"
              />
            </div>

            <button
              type="submit"
              disabled={!(uploadType === 'gps' ? file : pseFile) || (uploadType === 'gps' ? uploading : pseUploading)}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-pitch-600 hover:bg-pitch-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pitch-500 disabled:bg-dark-300 disabled:cursor-not-allowed disabled:text-gray-500"
            >
              {(uploadType === 'gps' ? uploading : pseUploading) ? 'A carregar...' : `Carregar ${uploadType === 'gps' ? 'GPS' : 'PSE'}`}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-md flex items-start">
              <XCircle className="h-5 w-5 text-red-400 mr-2 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          {(result || pseResult) && (
            <div className="mt-4 p-4 bg-pitch-500/10 border border-pitch-500/20 rounded-md">
              <div className="flex items-start">
                <CheckCircle className="h-5 w-5 text-pitch-400 mr-2 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-pitch-300">
                  {(result || pseResult).status === 'uploaded' ? (
                    // Handle PDF/Image upload response
                    <>
                      <p className="font-medium">Ficheiro {uploadType === 'gps' ? 'GPS' : 'PSE'} carregado com sucesso!</p>
                      <p className="mt-1">{(result || pseResult).message}</p>
                      <ul className="mt-2 space-y-1">
                        <li>Jornada: {(result || pseResult).jornada}</li>
                        <li>Sessão ID: {(result || pseResult).session_id}</li>
                        <li>Ficheiro: {(result || pseResult).file}</li>
                        <li>Tipo: {(result || pseResult).file_info?.file_type}</li>
                        {(result || pseResult).file_info?.image_width && (
                          <li>Dimensões: {(result || pseResult).file_info.image_width} x {(result || pseResult).file_info.image_height}</li>
                        )}
                      </ul>
                      {(result || pseResult).instructions && (
                        <div className="mt-3 p-3 bg-accent-cyan/10 border border-accent-cyan/20 rounded">
                          <p className="font-medium text-accent-cyan mb-2">Próximos Passos:</p>
                          <ul className="list-disc list-inside text-xs text-gray-400 space-y-1">
                            {(result || pseResult).instructions.map((instruction, idx) => (
                              <li key={idx}>{instruction}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  ) : (
                    // Handle CSV upload response
                    <>
                      <p className="font-medium">Upload {uploadType === 'gps' ? 'GPS' : 'PSE'} concluído com sucesso!</p>
                      <ul className="mt-2 space-y-1">
                        <li>Jornada: {(result || pseResult).jornada}</li>
                        <li>Sessão ID: {(result || pseResult).session_id}</li>
                        <li>Registos inseridos: {(result || pseResult).inserted} / {(result || pseResult).total_rows}</li>
                      </ul>
                      {(result || pseResult).errors && (result || pseResult).errors.length > 0 && (
                        <div className="mt-2">
                          <p className="font-medium text-accent-gold">Avisos:</p>
                          <ul className="list-disc list-inside">
                            {(result || pseResult).errors.slice(0, 5).map((err, idx) => (
                              <li key={idx} className="text-xs">{err}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="card-dark rounded-xl p-6 border border-white/5">
          <h2 className="text-lg font-medium text-white mb-4">
            Histórico de Uploads
          </h2>
          <div className="space-y-3">
            {history.length > 0 ? (
              history.map((item, idx) => (
                <div key={idx} className="border-b border-white/5 pb-3">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-200">
                        {item.fonte}
                        {item.tipo_dados && (
                          <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                            item.tipo_dados === 'GPS' 
                              ? 'bg-accent-cyan/10 text-accent-cyan' 
                              : 'bg-pitch-500/10 text-pitch-400'
                          }`}>
                            {item.tipo_dados}
                          </span>
                        )}
                      </p>
                      <p className="text-xs text-gray-500">
                        Sessão #{item.sessao_id} • {item.data}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(item.ingested_at).toLocaleString('pt-PT')}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">
                        {item.num_records} registos
                      </span>
                      <button
                        onClick={() => handleViewSession(item.sessao_id)}
                        className="p-1 text-accent-cyan hover:text-accent-cyan/80 hover:bg-white/5 rounded"
                        title="Ver dados da sessão"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteSession(item.sessao_id)}
                        disabled={deletingSession === item.sessao_id}
                        className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded disabled:opacity-50"
                        title="Eliminar sessão"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">Sem uploads recentes</p>
            )}
          </div>
        </div>
      </div>

      {/* Session Data Modal */}
      {viewingSession && sessionData && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border border-white/10 w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-xl bg-dark-200">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-white">
                  Dados da Sessão #{sessionData.session.id}
                </h3>
                <button
                  onClick={closeModal}
                  className="text-gray-500 hover:text-gray-300"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Session Info */}
                <div className="bg-dark-300/50 p-4 rounded-lg border border-white/5">
                  <h4 className="font-medium text-white mb-2">Informações da Sessão</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-300">
                    <div>
                      <span className="font-medium">Jornada:</span> {sessionData.session.jornada}
                    </div>
                    <div>
                      <span className="font-medium">Data:</span> {new Date(sessionData.session.data).toLocaleDateString('pt-PT')}
                    </div>
                    <div>
                      <span className="font-medium">Tipo:</span> {sessionData.session.tipo}
                    </div>
                    <div>
                      <span className="font-medium">Duração:</span> {sessionData.session.duracao_min || 'N/A'} min
                    </div>
                  </div>
                </div>

                {/* Data Counts */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-accent-cyan/5 p-4 rounded-lg border border-accent-cyan/20">
                    <h4 className="font-medium text-accent-cyan mb-2">Dados GPS</h4>
                    <p className="text-2xl font-bold text-white">{sessionData.gps_count}</p>
                    <p className="text-sm text-gray-400">registos</p>
                  </div>
                  <div className="bg-pitch-500/5 p-4 rounded-lg border border-pitch-500/20">
                    <h4 className="font-medium text-pitch-400 mb-2">Dados PSE</h4>
                    <p className="text-2xl font-bold text-white">{sessionData.pse_count}</p>
                    <p className="text-sm text-gray-400">registos</p>
                  </div>
                </div>

                {/* Sample Data */}
                {sessionData.gps_sample && sessionData.gps_sample.length > 0 && (
                  <div className="bg-dark-300/50 p-4 rounded-lg border border-white/5">
                    <h4 className="font-medium text-white mb-2">Amostra GPS (primeiros 5)</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-xs text-gray-300">
                        <thead>
                          <tr className="border-b border-white/10">
                            <th className="text-left py-1">Jogador</th>
                            <th className="text-left py-1">Distância (m)</th>
                            <th className="text-left py-1">Vel. Máx (km/h)</th>
                            <th className="text-left py-1">Acelerações</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sessionData.gps_sample.map((record, idx) => (
                            <tr key={idx} className="border-b border-white/5">
                              <td className="py-1">{record.nome_completo}</td>
                              <td className="py-1">{record.distancia_total?.toFixed(1) || 'N/A'}</td>
                              <td className="py-1">{record.velocidade_max?.toFixed(1) || 'N/A'}</td>
                              <td className="py-1">{record.aceleracoes || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {sessionData.pse_sample && sessionData.pse_sample.length > 0 && (
                  <div className="bg-dark-300/50 p-4 rounded-lg border border-white/5">
                    <h4 className="font-medium text-white mb-2">Amostra PSE (primeiros 5)</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full text-xs text-gray-300">
                        <thead>
                          <tr className="border-b border-white/10">
                            <th className="text-left py-1">Jogador</th>
                            <th className="text-left py-1">Sono</th>
                            <th className="text-left py-1">Stress</th>
                            <th className="text-left py-1">Fadiga</th>
                            <th className="text-left py-1">RPE</th>
                            <th className="text-left py-1">Carga</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sessionData.pse_sample.map((record, idx) => (
                            <tr key={idx} className="border-b border-white/5">
                              <td className="py-1">{record.nome_completo}</td>
                              <td className="py-1">{record.qualidade_sono || 'N/A'}</td>
                              <td className="py-1">{record.stress || 'N/A'}</td>
                              <td className="py-1">{record.fadiga || 'N/A'}</td>
                              <td className="py-1">{record.pse || 'N/A'}</td>
                              <td className="py-1">{record.carga_total || 'N/A'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={closeModal}
                  className="px-4 py-2 bg-dark-300 text-gray-300 rounded-md hover:bg-dark-50 border border-white/10"
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
