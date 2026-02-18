import { useState, useEffect } from 'react'
import { computerVisionApi } from '../api/client'
import { 
  ChartBarIcon, 
  VideoCameraIcon, 
  ClockIcon, 
  EyeIcon,
  UserGroupIcon,
  PlayIcon
} from '@heroicons/react/24/outline'
import VideoAnalysisPlayer from './VideoAnalysisPlayer'
import TacticalMetricsDisplay from './TacticalMetricsDisplay'
import XGBoostPredictionPanel from './XGBoostPredictionPanel'

export default function VideoAnalysisDetails({ analysisId, onClose }) {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showVideoPlayer, setShowVideoPlayer] = useState(false)

  const exportAnalysisData = (analysis, results) => {
    try {
      // Create comprehensive export data
      const exportData = {
        analysis_id: analysis.analysis_id,
        session_id: analysis.session_id,
        analysis_type: analysis.analysis_type,
        status: analysis.status,
        created_at: analysis.created_at,
        completed_at: analysis.completed_at,
        processing_time: analysis.processing_time,
        results: results,
        export_timestamp: new Date().toISOString(),
        export_version: "1.0"
      }

      // Convert to JSON string
      const jsonString = JSON.stringify(exportData, null, 2)
      
      // Create blob and download
      const blob = new Blob([jsonString], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      
      // Create download link
      const link = document.createElement('a')
      link.href = url
      link.download = `tactical_analysis_${analysis.analysis_id.substring(0, 8)}.json`
      document.body.appendChild(link)
      link.click()
      
      // Cleanup
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Error exporting data:', error)
      alert('Error exporting data. Please try again.')
    }
  }

  useEffect(() => {
    if (analysisId) {
      loadAnalysisDetails()
    }
  }, [analysisId])

  const loadAnalysisDetails = async () => {
    try {
      console.log('🔍 Loading analysis details for:', analysisId)
      const response = await computerVisionApi.getAnalysisStatus(analysisId)
      console.log('📊 Analysis details:', response.data)
      setAnalysis(response.data)
    } catch (err) {
      console.error('❌ Error loading analysis details:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  const getVisibilityColor = (percentage) => {
    if (percentage >= 70) return 'text-green-600'
    if (percentage >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getVisibilityBg = (percentage) => {
    if (percentage >= 70) return 'bg-green-100'
    if (percentage >= 50) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
          <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
          <div className="text-center">
            <h3 className="text-lg font-medium text-red-600 mb-2">Error Loading Analysis</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={onClose}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!analysis) return null

  const results = analysis.results || {}
  const ballVisibility = results.ball_visibility_percentage || 
    (results.ball_detections && results.total_frames ? 
      Math.round((results.ball_detections / results.total_frames) * 100) : 0)

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-11/12 max-w-6xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <VideoCameraIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h3 className="text-xl font-medium text-gray-900">
                Video Analysis Results
              </h3>
              <p className="text-sm text-gray-500">
                Analysis ID: {analysis.analysis_id?.substring(0, 8)}...
                {analysis.session_id && ` | Session ${analysis.session_id}`}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Status Banner */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">
                Analysis Completed Successfully
              </p>
              <p className="text-sm text-green-600">
                Processed on {new Date(analysis.completed_at).toLocaleString('pt-PT')}
                {analysis.processing_time_seconds && 
                  ` | Processing time: ${formatDuration(analysis.processing_time_seconds)}`}
              </p>
            </div>
          </div>
        </div>

        {/* Main Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Frames */}
          <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
            <div className="flex items-center">
              <PlayIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-blue-600">Total Frames</p>
                <p className="text-2xl font-bold text-blue-900">
                  {results.total_frames?.toLocaleString() || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Ball Detections */}
          <div className="bg-green-50 rounded-lg p-6 border border-green-200">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">⚽</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-green-600">Ball Detections</p>
                <p className="text-2xl font-bold text-green-900">
                  {results.ball_detections?.toLocaleString() || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Player Detections */}
          <div className="bg-purple-50 rounded-lg p-6 border border-purple-200">
            <div className="flex items-center">
              <UserGroupIcon className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-purple-600">Player Detections</p>
                <p className="text-2xl font-bold text-purple-900">
                  {results.player_detections?.toLocaleString() || 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Ball Visibility */}
          <div className={`${getVisibilityBg(ballVisibility)} rounded-lg p-6 border`}>
            <div className="flex items-center">
              <EyeIcon className={`h-8 w-8 ${getVisibilityColor(ballVisibility)}`} />
              <div className="ml-4">
                <p className={`text-sm font-medium ${getVisibilityColor(ballVisibility)}`}>
                  Ball Visibility
                </p>
                <p className={`text-2xl font-bold ${getVisibilityColor(ballVisibility)}`}>
                  {ballVisibility}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Tactical Metrics Display */}
        <div className="mb-6">
          <TacticalMetricsDisplay results={results} />
        </div>

        {/* XGBoost ML Prediction Panel */}
        <div className="mb-6">
          <XGBoostPredictionPanel analysisId={analysis.analysis_id} />
        </div>

        {/* Ball Visibility Chart */}
        <div className="mb-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Ball Visibility Analysis</h4>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Ball Visible</span>
                  <span>{ballVisibility}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      ballVisibility >= 70 ? 'bg-green-500' :
                      ballVisibility >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${ballVisibility}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Ball Hidden</span>
                  <span>{100 - ballVisibility}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gray-400 h-2 rounded-full"
                    style={{ width: `${100 - ballVisibility}%` }}
                  ></div>
                </div>
              </div>
            </div>
            
            {/* Interpretation */}
            <div className="mt-4 p-3 bg-gray-50 rounded">
              <p className="text-sm text-gray-700">
                {ballVisibility >= 70 ? 
                  '🟢 Excellent ball visibility - Great for tactical analysis' :
                  ballVisibility >= 50 ?
                  '🟡 Good ball visibility - Suitable for most analysis' :
                  '🔴 Limited ball visibility - May affect some metrics'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Close
          </button>
          <button
            onClick={() => setShowVideoPlayer(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-2"
          >
            <PlayIcon className="h-4 w-4" />
            <span>Watch Video with Analysis</span>
          </button>
          <button
            onClick={() => exportAnalysisData(analysis, results)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Export Data
          </button>
        </div>

        {/* Video Analysis Player Modal */}
        {showVideoPlayer && (
          <VideoAnalysisPlayer
            analysisId={analysis.analysis_id}
            onClose={() => setShowVideoPlayer(false)}
          />
        )}
      </div>
    </div>
  )
}
