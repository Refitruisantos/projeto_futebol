import React, { useState } from 'react'
import { 
  CpuChipIcon,
  ChartBarIcon,
  BeakerIcon,
  DocumentTextIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

export default function AIAnalysisPanel({ analysisId }) {
  const [aiResults, setAiResults] = useState(null)
  const [numericalResults, setNumericalResults] = useState(null)
  const [loading, setLoading] = useState(false)

  const runAIAnalysis = async () => {
    try {
      setLoading(true)
      
      const response = await fetch(`/api/ai-analysis/analyze/${analysisId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        setAiResults(result.ai_analysis)
      } else {
        throw new Error('Failed to run AI analysis')
      }
    } catch (error) {
      console.error('Error running AI analysis:', error)
    } finally {
      setLoading(false)
    }
  }

  const getNumericalInsights = async () => {
    try {
      setLoading(true)
      
      const response = await fetch(`/api/ai-analysis/insights/${analysisId}`)
      
      if (response.ok) {
        const result = await response.json()
        setNumericalResults(result.numerical_results)
      } else {
        throw new Error('Failed to get numerical insights')
      }
    } catch (error) {
      console.error('Error getting numerical insights:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
        <CpuChipIcon className="h-5 w-5 mr-2 text-purple-600" />
        AI/ML Tactical Analysis Engine
      </h4>
      
      <div className="space-y-4">
        {/* Control Buttons */}
        <div className="flex space-x-3">
          <button
            onClick={runAIAnalysis}
            disabled={loading}
            className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? (
              <>
                <ArrowPathIcon className="h-4 w-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <BeakerIcon className="h-4 w-4" />
                <span>Run AI Analysis</span>
              </>
            )}
          </button>
          
          <button
            onClick={getNumericalInsights}
            disabled={loading}
            className="flex items-center space-x-2 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            <ChartBarIcon className="h-4 w-4" />
            <span>Get Numerical Results</span>
          </button>
        </div>

        {/* AI Analysis Results */}
        {aiResults && (
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h5 className="font-medium text-purple-800 mb-3">AI Cross-Reference Analysis</h5>
            
            {/* Primary Findings */}
            {aiResults.primary_findings && aiResults.primary_findings.length > 0 && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-purple-700 mb-2">Primary Findings</h6>
                <div className="grid grid-cols-2 gap-2">
                  {aiResults.primary_findings.map((finding, index) => (
                    <div key={index} className="bg-white p-2 rounded border text-xs">
                      <div className="font-medium text-purple-800">{finding.metric.replace(/_/g, ' ')}</div>
                      <div className="text-purple-600">Value: {finding.value}</div>
                      <div className="text-purple-600">Confidence: {finding.confidence}%</div>
                      <div className="text-purple-600">Correlation: {finding.correlation}%</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Pattern Analysis */}
            {aiResults.pattern_analysis && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-purple-700 mb-2">Pattern Analysis</h6>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">Detected Patterns:</span> {aiResults.pattern_analysis.detected_patterns}
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">High Confidence:</span> {aiResults.pattern_analysis.high_confidence_patterns}
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">Strongest Pattern:</span> {aiResults.pattern_analysis.strongest_pattern?.replace(/_/g, ' ')}
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">Reliability:</span> {(aiResults.pattern_analysis.pattern_reliability * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            )}

            {/* Performance Metrics */}
            {aiResults.performance_metrics && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-purple-700 mb-2">AI Performance Scores</h6>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">Pressure Effectiveness:</span> {(aiResults.performance_metrics.pressure_effectiveness * 100).toFixed(1)}%
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">Formation Stability:</span> {(aiResults.performance_metrics.formation_stability * 100).toFixed(1)}%
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">Tactical Efficiency:</span> {(aiResults.performance_metrics.tactical_efficiency * 100).toFixed(1)}%
                  </div>
                  <div className="bg-white p-2 rounded border">
                    <span className="font-medium">Overall Performance:</span> {(aiResults.performance_metrics.overall_performance * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            )}

            {/* AI Confidence */}
            <div className="bg-white p-2 rounded border text-center">
              <span className="font-medium text-purple-800">AI Confidence Score: {aiResults.ai_confidence}%</span>
            </div>
          </div>
        )}

        {/* Numerical Results */}
        {numericalResults && (
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <h5 className="font-medium text-indigo-800 mb-3">Exact Numerical Results</h5>
            
            {/* Pressure Metrics */}
            {numericalResults.pressure_metrics && Object.keys(numericalResults.pressure_metrics).length > 0 && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-indigo-700 mb-2">Pressure Metrics</h6>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  {Object.entries(numericalResults.pressure_metrics).map(([key, value]) => (
                    <div key={key} className="bg-white p-2 rounded border">
                      <div className="font-medium text-indigo-800">{key.replace(/_/g, ' ')}</div>
                      <div className="text-indigo-600">{typeof value === 'number' ? value.toFixed(2) : value}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Formation Metrics */}
            {numericalResults.formation_metrics && Object.keys(numericalResults.formation_metrics).length > 0 && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-indigo-700 mb-2">Formation Metrics</h6>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  {Object.entries(numericalResults.formation_metrics).map(([key, value]) => (
                    <div key={key} className="bg-white p-2 rounded border">
                      <div className="font-medium text-indigo-800">{key.replace(/_/g, ' ')}</div>
                      <div className="text-indigo-600">{typeof value === 'number' ? value.toFixed(2) : value}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Scores */}
            {numericalResults.ai_scores && Object.keys(numericalResults.ai_scores).length > 0 && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-indigo-700 mb-2">AI Calculated Scores</h6>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  {Object.entries(numericalResults.ai_scores).map(([key, value]) => (
                    <div key={key} className="bg-white p-2 rounded border">
                      <div className="font-medium text-indigo-800">{key.replace(/_/g, ' ')}</div>
                      <div className="text-indigo-600">{typeof value === 'number' ? value.toFixed(2) : value}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Correlations */}
            {numericalResults.correlations && Object.keys(numericalResults.correlations).length > 0 && (
              <div className="mb-4">
                <h6 className="text-sm font-medium text-indigo-700 mb-2">Data Correlations</h6>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(numericalResults.correlations).map(([key, value]) => (
                    <div key={key} className="bg-white p-2 rounded border">
                      <div className="font-medium text-indigo-800">{key.replace(/_/g, ' ')}</div>
                      <div className="text-indigo-600">{typeof value === 'number' ? value.toFixed(3) : value}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detected Patterns */}
            {numericalResults.patterns && numericalResults.patterns.length > 0 && (
              <div>
                <h6 className="text-sm font-medium text-indigo-700 mb-2">Detected Patterns</h6>
                <div className="space-y-2">
                  {numericalResults.patterns.map((pattern, index) => (
                    <div key={index} className="bg-white p-2 rounded border text-xs">
                      <div className="font-medium text-indigo-800">{pattern.metric.replace(/_/g, ' ')}</div>
                      <div className="grid grid-cols-3 gap-2 mt-1">
                        <span className="text-indigo-600">Value: {pattern.value}</span>
                        <span className="text-indigo-600">Confidence: {pattern.confidence}%</span>
                        <span className="text-indigo-600">Correlation: {pattern.correlation}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h5 className="font-medium text-gray-800 mb-2 flex items-center">
            <DocumentTextIcon className="h-4 w-4 mr-2" />
            AI Analysis Features
          </h5>
          <div className="text-sm text-gray-600 space-y-1">
            <p><strong>AI Analysis:</strong> Cross-references all tactical data using ML algorithms to detect patterns and correlations</p>
            <p><strong>Numerical Results:</strong> Exact values without explanatory text - pure data output</p>
            <p><strong>Pattern Detection:</strong> Identifies tactical patterns with confidence scores and correlation strengths</p>
            <p><strong>Performance Scoring:</strong> AI-calculated effectiveness metrics for pressure, formation, and overall performance</p>
          </div>
        </div>
      </div>
    </div>
  )
}
