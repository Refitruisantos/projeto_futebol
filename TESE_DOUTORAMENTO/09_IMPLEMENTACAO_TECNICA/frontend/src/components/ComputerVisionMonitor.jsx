import React, { useState, useEffect } from 'react'
import { computerVisionApi } from '../api/client'
import { XMarkIcon, PlayIcon, PauseIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

const ComputerVisionMonitor = ({ analysisId, isOpen, onClose }) => {
  const [status, setStatus] = useState(null)
  const [progress, setProgress] = useState(0)
  const [logs, setLogs] = useState([])
  const [error, setError] = useState(null)
  const [isPolling, setIsPolling] = useState(false)

  useEffect(() => {
    if (isOpen && analysisId) {
      startMonitoring()
    } else {
      stopMonitoring()
    }

    return () => stopMonitoring()
  }, [isOpen, analysisId])

  const startMonitoring = () => {
    setIsPolling(true)
    pollStatus()
  }

  const stopMonitoring = () => {
    setIsPolling(false)
  }

  const formatDuration = (seconds) => {
    if (!seconds || seconds < 0) return '--:--'
    const m = Math.floor(seconds / 60)
    const s = Math.floor(seconds % 60)
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const pollStatus = async () => {
    if (!isPolling || !analysisId) return

    try {
      const response = await computerVisionApi.getAnalysisStatus(analysisId)
      const data = response.data

      setStatus(data.status)
      setError(data.error_message)

      // Use real progress from backend
      let newProgress = 0
      let elapsedSec = 0
      let estimatedRemaining = null

      if (data.started_at) {
        elapsedSec = (Date.now() - new Date(data.started_at).getTime()) / 1000
      }

      switch (data.status) {
        case 'queued':
          newProgress = 0
          break
        case 'processing':
          newProgress = data.progress_percentage || 0
          if (newProgress > 0 && elapsedSec > 0) {
            estimatedRemaining = (elapsedSec / newProgress) * (100 - newProgress)
          }
          break
        case 'completed':
          newProgress = 100
          elapsedSec = data.processing_time_seconds || elapsedSec
          setIsPolling(false)
          break
        case 'failed':
          newProgress = 0
          setIsPolling(false)
          break
        default:
          newProgress = 0
      }
      setProgress(newProgress)

      // Add log entry
      const timestamp = new Date().toLocaleTimeString()
      const logEntry = {
        timestamp,
        status: data.status,
        message: getStatusMessage(data.status, data.error_message, newProgress, elapsedSec, estimatedRemaining)
      }

      setLogs(prev => {
        const newLogs = [logEntry, ...prev.slice(0, 29)]
        return newLogs
      })

      // Continue polling if still processing
      if (isPolling && (data.status === 'processing' || data.status === 'queued')) {
        setTimeout(pollStatus, 3000)
      }

    } catch (err) {
      console.error('Error polling CV status:', err)
      setError(err.message)
      setIsPolling(false)
    }
  }

  const getStatusMessage = (status, errorMessage, pct, elapsed, remaining) => {
    switch (status) {
      case 'queued':
        return 'Análise adicionada à fila de processamento...'
      case 'processing':
        const parts = [`Processando: ${pct.toFixed(1)}%`]
        if (elapsed > 0) parts.push(`Tempo decorrido: ${formatDuration(elapsed)}`)
        if (remaining && remaining > 0) parts.push(`Tempo restante estimado: ${formatDuration(remaining)}`)
        return parts.join(' | ')
      case 'completed':
        return `Análise concluída com sucesso! (${formatDuration(elapsed)})`
      case 'failed':
        return `Falha na análise: ${errorMessage || 'Erro desconhecido'}`
      default:
        return 'Status desconhecido'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'queued':
        return <PauseIcon className="h-5 w-5 text-yellow-500" />
      case 'processing':
        return <PlayIcon className="h-5 w-5 text-blue-500 animate-pulse" />
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      default:
        return <PauseIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'queued':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-2/3 shadow-lg rounded-md bg-white max-h-[80vh] overflow-hidden">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Monitor de Visão Computacional
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Analysis Info */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              ID da Análise: {analysisId}
            </span>
            <div className="flex items-center space-x-2">
              {getStatusIcon(status)}
              <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(status)}`}>
                {status?.toUpperCase() || 'DESCONHECIDO'}
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-3">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progresso da Análise</span>
              <span>{progress.toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all duration-500 ${
                  status === 'completed' ? 'bg-green-500' : 
                  status === 'failed' ? 'bg-red-500' : 'bg-blue-500'
                }`}
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">
                <strong>Erro:</strong> {error}
              </p>
            </div>
          )}
        </div>

        {/* Process Logs */}
        <div className="mb-4">
          <h4 className="text-md font-medium text-gray-900 mb-3">
            Log do Processo
          </h4>
          <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm max-h-64 overflow-y-auto">
            {logs.length === 0 ? (
              <div className="text-gray-500">Aguardando logs do processo...</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="mb-1">
                  <span className="text-gray-400">[{log.timestamp}]</span>{' '}
                  <span className={
                    log.status === 'completed' ? 'text-green-400' :
                    log.status === 'failed' ? 'text-red-400' :
                    log.status === 'processing' ? 'text-blue-400' :
                    'text-yellow-400'
                  }>
                    {log.message}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          {status === 'completed' && (
            <button
              onClick={() => {
                // Navigate to analysis results
                onClose()
                // Could trigger a callback to show results
              }}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
            >
              Ver Resultados
            </button>
          )}
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}

export default ComputerVisionMonitor
