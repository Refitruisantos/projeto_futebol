import { useState, useEffect } from 'react'
import { computerVisionApi } from '../api/client'
import { VideoCameraIcon, ChartBarIcon, ClockIcon, CheckCircleIcon, ExclamationTriangleIcon, TrashIcon, ArrowPathIcon } from '@heroicons/react/24/outline'
import VideoAnalysisDetails from './VideoAnalysisDetails'

export default function VideoAnalysisDashboard() {
  const [summary, setSummary] = useState({
    total: 0,
    completed: 0,
    processing: 0,
    queued: 0,
    failed: 0
  })
  const [recentAnalyses, setRecentAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedAnalysisId, setSelectedAnalysisId] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [actionLoading, setActionLoading] = useState(null)

  useEffect(() => {
    loadDashboardData()
    // Refresh faster when analyses are in progress
    const hasActive = recentAnalyses.some(a => a.status === 'processing' || a.status === 'queued')
    const interval = setInterval(loadDashboardData, hasActive ? 5000 : 30000)
    return () => clearInterval(interval)
  }, [recentAnalyses.some(a => a.status === 'processing' || a.status === 'queued')])

  const loadDashboardData = async () => {
    try {
      // Load ALL analyses from the backend (no hardcoded session IDs)
      const response = await computerVisionApi.getAllAnalyses(50)
      const allAnalyses = response.data || []

      // Calculate summary
      const summaryData = {
        total: allAnalyses.length,
        completed: allAnalyses.filter(a => a.status === 'completed').length,
        processing: allAnalyses.filter(a => a.status === 'processing').length,
        queued: allAnalyses.filter(a => a.status === 'queued').length,
        failed: allAnalyses.filter(a => a.status === 'failed').length
      }

      setSummary(summaryData)
      setRecentAnalyses(allAnalyses.slice(0, 10)) // Show 10 most recent
      
    } catch (err) {
      console.error('Error loading dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'processing':
        return <ClockIcon className="h-5 w-5 text-blue-500 animate-spin" />
      case 'queued':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const handleDelete = async (e, analysisId) => {
    e.stopPropagation()
    if (deleteConfirm !== analysisId) {
      setDeleteConfirm(analysisId)
      return
    }
    setActionLoading(analysisId)
    try {
      await computerVisionApi.deleteAnalysis(analysisId)
      setDeleteConfirm(null)
      loadDashboardData()
    } catch (err) {
      console.error('Error deleting analysis:', err)
      alert('Failed to delete: ' + (err.response?.data?.detail || err.message))
    } finally {
      setActionLoading(null)
    }
  }

  const handleReset = async (e, analysisId) => {
    e.stopPropagation()
    setActionLoading(analysisId)
    try {
      await fetch(`/api/computer-vision/analysis/${analysisId}/reset`, { method: 'PATCH' })
      loadDashboardData()
    } catch (err) {
      console.error('Error resetting analysis:', err)
    } finally {
      setActionLoading(null)
    }
  }

  const getStatusBadge = (status) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium"
    switch (status) {
      case 'completed':
        return `${baseClasses} bg-green-100 text-green-800`
      case 'processing':
        return `${baseClasses} bg-blue-100 text-blue-800`
      case 'queued':
        return `${baseClasses} bg-yellow-100 text-yellow-800`
      case 'failed':
        return `${baseClasses} bg-red-100 text-red-800`
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Prominent Alert for Completed Analyses */}
      {summary.completed > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-400 p-4 rounded-lg shadow-lg">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <VideoCameraIcon className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-green-800">
                🎉 {summary.completed} Video Analysis{summary.completed > 1 ? 'es' : ''} Complete!
              </h3>
              <p className="text-green-700">
                Your football video analyses are ready to view. Click on any session below to see detailed results.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Analyses</p>
              <p className="text-2xl font-bold text-gray-900">{summary.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-green-600">{summary.completed}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-400">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-blue-400 animate-spin" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Processing</p>
              <p className="text-2xl font-bold text-blue-600">{summary.processing}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Queued</p>
              <p className="text-2xl font-bold text-yellow-600">{summary.queued}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Analyses */}
      {recentAnalyses.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <VideoCameraIcon className="h-5 w-5 mr-2" />
              Recent Video Analyses
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {recentAnalyses.map((analysis) => (
              <div 
                key={analysis.analysis_id} 
                className="px-6 py-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => analysis.status === 'completed' && setSelectedAnalysisId(analysis.analysis_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(analysis.status)}
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {analysis.session_id ? `Sessão ${analysis.session_id}` : 'Sem sessão'} - Análise {analysis.analysis_id.substring(0, 8)}...
                      </p>
                      <p className="text-sm text-gray-500">
                        {analysis.analysis_type} | Criado: {new Date(analysis.created_at).toLocaleString()}
                        {analysis.status === 'completed' && analysis.processing_time_seconds && (
                          <span> | Tempo: {Math.floor(analysis.processing_time_seconds / 60)}:{String(Math.floor(analysis.processing_time_seconds % 60)).padStart(2, '0')}</span>
                        )}
                      </p>
                      {analysis.status === 'processing' && (
                        <div className="mt-1 flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                            <div 
                              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${analysis.progress_percentage || 0}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-blue-600">
                            {(analysis.progress_percentage || 0).toFixed(1)}%
                          </span>
                          {analysis.started_at && (
                            <span className="text-xs text-gray-400">
                              {Math.floor((Date.now() - new Date(analysis.started_at).getTime()) / 60000)}min decorridos
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={getStatusBadge(analysis.status)}>
                      {analysis.status.toUpperCase()}
                    </span>
                    {analysis.status === 'completed' && (
                      <span className="text-xs text-blue-600 font-medium">Click to view</span>
                    )}
                    {(analysis.status === 'processing' || analysis.status === 'queued') && (
                      <button
                        onClick={(e) => handleReset(e, analysis.analysis_id)}
                        disabled={actionLoading === analysis.analysis_id}
                        className="p-1 text-yellow-600 hover:text-yellow-800 hover:bg-yellow-50 rounded" title="Reset stuck analysis">
                        <ArrowPathIcon className={`h-4 w-4 ${actionLoading === analysis.analysis_id ? 'animate-spin' : ''}`} />
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDelete(e, analysis.analysis_id)}
                      disabled={actionLoading === analysis.analysis_id}
                      className={`p-1 rounded text-sm ${
                        deleteConfirm === analysis.analysis_id
                          ? 'bg-red-600 text-white px-2 hover:bg-red-700'
                          : 'text-red-400 hover:text-red-600 hover:bg-red-50'
                      }`}
                      title={deleteConfirm === analysis.analysis_id ? 'Click again to confirm' : 'Delete analysis'}>
                      {deleteConfirm === analysis.analysis_id
                        ? <span className="text-xs font-medium">Confirm?</span>
                        : <TrashIcon className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Analyses Message */}
      {summary.total === 0 && (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <VideoCameraIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No video analyses yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Upload a video in a session to start computer vision analysis.
          </p>
        </div>
      )}

      {/* Video Analysis Details Modal */}
      {selectedAnalysisId && (
        <VideoAnalysisDetails
          analysisId={selectedAnalysisId}
          onClose={() => setSelectedAnalysisId(null)}
        />
      )}
    </div>
  )
}
