import { useState, useEffect } from 'react'
import { computerVisionApi } from '../api/client'
import { PlayIcon, EyeIcon, ArrowDownTrayIcon, ChartBarIcon } from '@heroicons/react/24/outline'

export default function ComputerVisionResults({ sessionId }) {
  const [analyses, setAnalyses] = useState([])
  const [selectedAnalysis, setSelectedAnalysis] = useState(null)
  const [detailedResults, setDetailedResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generatingVideo, setGeneratingVideo] = useState(null)
  const [showNotification, setShowNotification] = useState(false)

  useEffect(() => {
    loadAnalyses()
  }, [sessionId])

  const loadAnalyses = async () => {
    try {
      console.log('🔍 Loading analyses for session:', sessionId)
      const response = await computerVisionApi.getSessionAnalyses(sessionId)
      console.log('📊 Analyses response:', response.data)
      setAnalyses(response.data)
      
      // Auto-select the first completed analysis and show notification
      const completedAnalysis = response.data.find(a => a.status === 'completed')
      if (completedAnalysis) {
        setSelectedAnalysis(completedAnalysis.analysis_id)
        loadDetailedResults(completedAnalysis.analysis_id)
        setShowNotification(true)
        setTimeout(() => setShowNotification(false), 5000) // Hide after 5 seconds
      }
    } catch (err) {
      console.error('❌ Error loading analyses:', err)
      console.error('   Session ID:', sessionId)
      console.error('   Error details:', err.response?.data || err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadDetailedResults = async (analysisId) => {
    try {
      const response = await computerVisionApi.getDetailedAnalysis(analysisId)
      setDetailedResults(response.data)
    } catch (err) {
      console.error('Error loading detailed results:', err)
    }
  }

  const handleGenerateVideo = async (analysisId) => {
    setGeneratingVideo(analysisId)
    try {
      const response = await computerVisionApi.generateAnnotatedVideo(analysisId)
      if (response.data.status === 'exists') {
        // Video already exists, can download immediately
        window.open(computerVisionApi.getAnnotatedVideo(analysisId), '_blank')
      } else {
        // Video is being generated
        setTimeout(() => {
          setGeneratingVideo(null)
          // Could add polling here to check when video is ready
        }, 5000)
      }
    } catch (err) {
      console.error('Error generating video:', err)
      setGeneratingVideo(null)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'processing': return 'text-blue-600 bg-blue-100'
      case 'queued': return 'text-yellow-600 bg-yellow-100'
      case 'failed': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getQualityColor = (quality) => {
    switch (quality?.toLowerCase()) {
      case 'excellent': return 'text-green-600'
      case 'good': return 'text-blue-600'
      case 'fair': return 'text-yellow-600'
      case 'poor': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  if (loading) {
    return <div className="text-center py-8">Carregando análises de vídeo...</div>
  }

  if (analyses.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma análise de vídeo</h3>
        <p className="mt-1 text-sm text-gray-500">
          Carregue um vídeo para esta sessão para ver a análise de visão computacional.
        </p>
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            💡 <strong>Dica:</strong> Vá para a aba "Sessões" → "Nova Sessão" → marque "Carregar ficheiros após criar sessão" → selecione um vídeo
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Analysis Selection */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Análises de Vídeo</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analyses.map((analysis) => (
            <div
              key={analysis.analysis_id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors relative ${
                selectedAnalysis === analysis.analysis_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => {
                setSelectedAnalysis(analysis.analysis_id)
                if (analysis.status === 'completed') {
                  loadDetailedResults(analysis.analysis_id)
                }
              }}
            >
              {/* Video Content Indicator */}
              <div className="absolute top-2 right-2">
                {analysis.status === 'completed' && analysis.ball_visibility_percentage > 0 && (
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full" title="Contém análise de vídeo"></div>
                    <span className="text-xs text-green-600 font-medium">📹</span>
                  </div>
                )}
                {analysis.status === 'processing' && (
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" title="Processando vídeo"></div>
                    <span className="text-xs text-blue-600 font-medium">⏳</span>
                  </div>
                )}
                {analysis.status === 'failed' && (
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-red-500 rounded-full" title="Falha no processamento"></div>
                    <span className="text-xs text-red-600 font-medium">❌</span>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-between mb-2 pr-8">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(analysis.status)}`}>
                  {analysis.status.toUpperCase()}
                </span>
                <span className="text-xs text-gray-500">
                  {analysis.analysis_type}
                </span>
              </div>
              
              <div className="text-sm text-gray-600 mb-2">
                Criado: {new Date(analysis.created_at).toLocaleDateString('pt-PT')}
              </div>
              
              {analysis.processing_time_seconds && (
                <div className="text-sm text-gray-600 mb-2">
                  Tempo: {(analysis.processing_time_seconds / 60).toFixed(1)} min
                </div>
              )}
              
              {analysis.status === 'completed' && analysis.interpretation && (
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>Qualidade:</span>
                    <span className={getQualityColor(analysis.interpretation.quality_assessment)}>
                      {analysis.interpretation.quality_assessment}
                    </span>
                  </div>
                  {analysis.ball_visibility_percentage && (
                    <div className="flex justify-between text-xs">
                      <span>Bola visível:</span>
                      <span>{analysis.ball_visibility_percentage.toFixed(1)}%</span>
                    </div>
                  )}
                  {analysis.avg_players_detected && (
                    <div className="flex justify-between text-xs">
                      <span>Jogadores:</span>
                      <span>{analysis.avg_players_detected.toFixed(1)}</span>
                    </div>
                  )}
                </div>
              )}
              
              {analysis.status === 'completed' && (
                <div className="mt-3 flex space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleGenerateVideo(analysis.analysis_id)
                    }}
                    disabled={generatingVideo === analysis.analysis_id}
                    className="flex-1 inline-flex items-center justify-center px-2 py-1 text-xs font-medium text-white bg-purple-600 rounded hover:bg-purple-700 disabled:opacity-50"
                  >
                    {generatingVideo === analysis.analysis_id ? (
                      'Gerando...'
                    ) : (
                      <>
                        <PlayIcon className="w-3 h-3 mr-1" />
                        Vídeo
                      </>
                    )}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      loadDetailedResults(analysis.analysis_id)
                    }}
                    className="flex-1 inline-flex items-center justify-center px-2 py-1 text-xs font-medium text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
                  >
                    <EyeIcon className="w-3 h-3 mr-1" />
                    Detalhes
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Results */}
      {detailedResults && detailedResults.status === 'completed' && (
        <div className="border rounded-lg p-6 bg-white">
          <h4 className="text-lg font-medium text-gray-900 mb-4">
            Resultados Detalhados - {detailedResults.analysis.opponent || 'Sessão'}
          </h4>
          
          {/* Overall Assessment */}
          {detailedResults.interpretation?.overall_assessment && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h5 className="font-medium text-gray-900 mb-2">Avaliação Geral</h5>
              <div className="flex items-center space-x-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  detailedResults.interpretation.overall_assessment.rating === 'Excellent' ? 'bg-green-100 text-green-800' :
                  detailedResults.interpretation.overall_assessment.rating === 'Good' ? 'bg-blue-100 text-blue-800' :
                  detailedResults.interpretation.overall_assessment.rating === 'Fair' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {detailedResults.interpretation.overall_assessment.rating}
                </span>
                <span className="text-sm text-gray-600">
                  {detailedResults.interpretation.overall_assessment.description}
                </span>
              </div>
            </div>
          )}

          {/* Key Metrics */}
          {detailedResults.metrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {detailedResults.metrics.ball_visibility_percentage?.toFixed(1) || 0}%
                </div>
                <div className="text-sm text-blue-600">Visibilidade da Bola</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {detailedResults.metrics.avg_players_detected?.toFixed(1) || 0}
                </div>
                <div className="text-sm text-green-600">Jogadores Médios</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {detailedResults.metrics.ball_activity_level || 'N/A'}
                </div>
                <div className="text-sm text-purple-600">Atividade da Bola</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {detailedResults.metrics.overall_quality_score || 'N/A'}
                </div>
                <div className="text-sm text-yellow-600">Qualidade Geral</div>
              </div>
            </div>
          )}

          {/* Possession Analysis */}
          {detailedResults.interpretation?.tactical_insights?.field_usage && (
            <div className="mb-6">
              <h5 className="font-medium text-gray-900 mb-3">Análise de Posse por Zonas</h5>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-xl font-bold text-gray-700">
                    {detailedResults.interpretation.tactical_insights.field_usage.left_third}
                  </div>
                  <div className="text-sm text-gray-600">Terço Esquerdo</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-xl font-bold text-blue-700">
                    {detailedResults.interpretation.tactical_insights.field_usage.center_third}
                  </div>
                  <div className="text-sm text-blue-600">Terço Central</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-xl font-bold text-gray-700">
                    {detailedResults.interpretation.tactical_insights.field_usage.right_third}
                  </div>
                  <div className="text-sm text-gray-600">Terço Direito</div>
                </div>
              </div>
              <div className="mt-2 text-center text-sm text-gray-600">
                Estilo: {detailedResults.interpretation.tactical_insights.possession_style}
              </div>
            </div>
          )}

          {/* Detection Counts */}
          {detailedResults.detections && detailedResults.detections.length > 0 && (
            <div className="mb-6">
              <h5 className="font-medium text-gray-900 mb-3">Contagens de Detecção</h5>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {detailedResults.detections.map((detection) => (
                  <div key={detection.object_class} className="text-center p-3 border rounded-lg">
                    <div className="text-lg font-bold text-gray-700">
                      {detection.total_detections}
                    </div>
                    <div className="text-sm text-gray-600 capitalize">
                      {detection.object_class === 'ball' ? 'Bola' :
                       detection.object_class === 'player' ? 'Jogadores' :
                       detection.object_class === 'goalkeeper' ? 'Guarda-Redes' :
                       detection.object_class === 'referee' ? 'Árbitro' :
                       detection.object_class}
                    </div>
                    <div className="text-xs text-gray-500">
                      Conf: {detection.avg_confidence}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Insights and Recommendations */}
          {detailedResults.interpretation?.recommendations && detailedResults.interpretation.recommendations.length > 0 && (
            <div className="mb-6">
              <h5 className="font-medium text-gray-900 mb-3">Recomendações</h5>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                {detailedResults.interpretation.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Processing Info */}
          <div className="border-t pt-4 text-sm text-gray-500">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="font-medium">Tipo:</span> {detailedResults.analysis.analysis_type}
              </div>
              <div>
                <span className="font-medium">Confiança:</span> {detailedResults.analysis.confidence_threshold}
              </div>
              <div>
                <span className="font-medium">Amostragem:</span> 1/{detailedResults.analysis.sample_rate}
              </div>
              <div>
                <span className="font-medium">Tempo:</span> {
                  detailedResults.analysis.processing_time_seconds 
                    ? `${(detailedResults.analysis.processing_time_seconds / 60).toFixed(1)} min`
                    : 'N/A'
                }
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
