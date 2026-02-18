import { useState, useEffect } from 'react'

export default function WellnessTest() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching comprehensive profile...')
        const response = await fetch('http://localhost:8000/api/metrics/athletes/251/comprehensive-profile')
        console.log('Response status:', response.status)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const result = await response.json()
        console.log('API Response:', result)
        setData(result)
      } catch (err) {
        console.error('API Error:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) return <div className="p-8 text-gray-400">Loading...</div>
  if (error) return <div className="p-8 text-red-400">Error: {error}</div>

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-white">API Data Verification Test</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Wellness Data */}
        <div className="card-dark rounded-xl p-6 border border-white/5">
          <h2 className="text-xl font-semibold mb-4 text-white">Wellness Data ({data?.wellness_data?.length || 0} records)</h2>
          {data?.wellness_data && data.wellness_data.length > 0 ? (
            <div className="space-y-2 text-gray-300">
              <p><strong>Latest wellness score:</strong> {data.wellness_data[0]?.wellness_score}</p>
              <p><strong>Status:</strong> {data.wellness_data[0]?.wellness_status}</p>
              <p><strong>Recommendation:</strong> {data.wellness_data[0]?.training_recommendation}</p>
              <p><strong>Sleep Quality:</strong> {data.wellness_data[0]?.sleep_quality}/7</p>
              <p><strong>Fatigue Level:</strong> {data.wellness_data[0]?.fatigue_level}/7</p>
              <p><strong>Readiness Score:</strong> {data.wellness_data[0]?.readiness_score}</p>
            </div>
          ) : (
            <p className="text-red-500">❌ No wellness data found</p>
          )}
        </div>

        {/* Physical Evaluations */}
        <div className="card-dark rounded-xl p-6 border border-white/5">
          <h2 className="text-xl font-semibold mb-4 text-white">Physical Evaluations ({data?.physical_evaluations?.length || 0} records)</h2>
          {data?.physical_evaluations && data.physical_evaluations.length > 0 ? (
            <div className="space-y-2 text-gray-300">
              <p><strong>35m Sprint:</strong> {data.physical_evaluations[0]?.sprint_35m_seconds}s</p>
              <p><strong>5-0-5 Agility:</strong> {data.physical_evaluations[0]?.test_5_0_5_seconds}s</p>
              <p><strong>CMJ Height:</strong> {data.physical_evaluations[0]?.cmj_height_cm}cm</p>
              <p><strong>Squat Jump:</strong> {data.physical_evaluations[0]?.squat_jump_height_cm}cm</p>
              <p><strong>Hop Test:</strong> {data.physical_evaluations[0]?.hop_test_distance_m}m</p>
              <p><strong>VO₂ Max:</strong> {data.physical_evaluations[0]?.vo2_max_ml_kg_min}</p>
              <p><strong>Speed Percentile:</strong> {data.physical_evaluations[0]?.percentile_speed}th</p>
            </div>
          ) : (
            <p className="text-red-500">❌ No physical evaluations found</p>
          )}
        </div>

        {/* Risk Assessment */}
        <div className="card-dark rounded-xl p-6 border border-white/5">
          <h2 className="text-xl font-semibold mb-4 text-white">Risk Assessment</h2>
          {data?.risk_assessment ? (
            <div className="space-y-2 text-gray-300">
              <p><strong>Injury Risk:</strong> {data.risk_assessment.injury_risk_category} ({data.risk_assessment.injury_risk_score}/10)</p>
              <p><strong>Performance Risk:</strong> {data.risk_assessment.performance_risk_category}</p>
              <p><strong>Substitution Risk:</strong> {data.risk_assessment.substitution_risk_category}</p>
              <p><strong>Training Recommendation:</strong> {data.risk_assessment.training_recommendation}</p>
              <p><strong>Match Recommendation:</strong> {data.risk_assessment.match_recommendation}</p>
            </div>
          ) : (
            <p className="text-red-500">❌ No risk assessment found</p>
          )}
        </div>

        {/* Recent Sessions */}
        <div className="card-dark rounded-xl p-6 border border-white/5">
          <h2 className="text-xl font-semibold mb-4 text-white">Recent Sessions ({data?.recent_sessions?.length || 0} records)</h2>
          {data?.recent_sessions && data.recent_sessions.length > 0 ? (
            <div className="space-y-2 text-gray-300">
              <p><strong>Latest Session:</strong> {data.recent_sessions[0]?.data} - {data.recent_sessions[0]?.tipo}</p>
              <p><strong>Opponent:</strong> {data.recent_sessions[0]?.adversario || 'N/A'}</p>
              <p><strong>Difficulty:</strong> {data.recent_sessions[0]?.dificuldade_adversario || 'N/A'}</p>
              <p><strong>Avg Distance:</strong> {data.recent_sessions[0]?.avg_distance ? Math.round(data.recent_sessions[0].avg_distance) + 'm' : 'N/A'}</p>
              <p><strong>Avg Speed:</strong> {data.recent_sessions[0]?.avg_max_speed ? data.recent_sessions[0].avg_max_speed.toFixed(1) + ' km/h' : 'N/A'}</p>
            </div>
          ) : (
            <p className="text-red-500">❌ No recent sessions found</p>
          )}
        </div>
      </div>

      {/* Raw Data Preview */}
      <div className="mt-8 card-dark rounded-xl p-6 border border-white/5">
        <h2 className="text-xl font-semibold mb-4 text-white">Raw API Response (First 1000 chars)</h2>
        <pre className="text-xs bg-dark-400 text-gray-300 p-4 rounded border border-white/5 overflow-auto max-h-64">
          {JSON.stringify(data, null, 2).substring(0, 1000)}...
        </pre>
      </div>

      {/* Status Summary */}
      <div className="mt-6 p-4 card-dark rounded-xl border border-accent-cyan/20">
        <h3 className="font-semibold text-accent-cyan">API Status Summary:</h3>
        <ul className="mt-2 space-y-1 text-gray-300">
          <li>✅ API Connection: Working</li>
          <li>{data?.wellness_data?.length > 0 ? '✅' : '❌'} Wellness Data: {data?.wellness_data?.length || 0} records</li>
          <li>{data?.physical_evaluations?.length > 0 ? '✅' : '❌'} Physical Evaluations: {data?.physical_evaluations?.length || 0} records</li>
          <li>{data?.risk_assessment ? '✅' : '❌'} Risk Assessment: {data?.risk_assessment ? 'Available' : 'Missing'}</li>
          <li>{data?.recent_sessions?.length > 0 ? '✅' : '❌'} Recent Sessions: {data?.recent_sessions?.length || 0} records</li>
        </ul>
      </div>
    </div>
  )
}
