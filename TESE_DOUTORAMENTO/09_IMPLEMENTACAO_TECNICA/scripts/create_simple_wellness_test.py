#!/usr/bin/env python3
"""Create a simple test to verify wellness data is being fetched and displayed"""

import os

# Create a simple test page to verify the API is working
test_page_content = '''<!DOCTYPE html>
<html>
<head>
    <title>API Test</title>
</head>
<body>
    <h1>Comprehensive Profile API Test</h1>
    <div id="result"></div>
    
    <script>
        async function testAPI() {
            try {
                const response = await fetch('http://localhost:8000/api/metrics/athletes/251/comprehensive-profile');
                const data = await response.json();
                
                document.getElementById('result').innerHTML = `
                    <h2>API Response Status: ${response.status}</h2>
                    <h3>Wellness Data Count: ${data.wellness_data ? data.wellness_data.length : 0}</h3>
                    <h3>Physical Evaluations Count: ${data.physical_evaluations ? data.physical_evaluations.length : 0}</h3>
                    <h3>Recent Sessions Count: ${data.recent_sessions ? data.recent_sessions.length : 0}</h3>
                    
                    <h4>Sample Wellness Record:</h4>
                    <pre>${data.wellness_data && data.wellness_data[0] ? JSON.stringify(data.wellness_data[0], null, 2) : 'No wellness data'}</pre>
                    
                    <h4>Sample Physical Evaluation:</h4>
                    <pre>${data.physical_evaluations && data.physical_evaluations[0] ? JSON.stringify(data.physical_evaluations[0], null, 2) : 'No physical evaluations'}</pre>
                `;
            } catch (error) {
                document.getElementById('result').innerHTML = `<h2>Error: ${error.message}</h2>`;
            }
        }
        
        testAPI();
    </script>
</body>
</html>'''

# Write the test page
test_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\public\api-test.html"
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_page_content)

print("✅ Created API test page at:")
print("   http://localhost:5173/api-test.html")
print("\n🔧 Also creating a minimal React component to test data loading...")

# Create a minimal test component
test_component = '''import { useState, useEffect } from 'react'

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

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div style={{ padding: '20px' }}>
      <h1>Wellness Data Test</h1>
      
      <h2>Wellness Data ({data?.wellness_data?.length || 0} records)</h2>
      {data?.wellness_data && data.wellness_data.length > 0 ? (
        <div>
          <p>Latest wellness score: {data.wellness_data[0]?.wellness_score}</p>
          <p>Status: {data.wellness_data[0]?.wellness_status}</p>
          <p>Recommendation: {data.wellness_data[0]?.training_recommendation}</p>
        </div>
      ) : (
        <p>No wellness data found</p>
      )}
      
      <h2>Physical Evaluations ({data?.physical_evaluations?.length || 0} records)</h2>
      {data?.physical_evaluations && data.physical_evaluations.length > 0 ? (
        <div>
          <p>35m Sprint: {data.physical_evaluations[0]?.sprint_35m_seconds}s</p>
          <p>CMJ Height: {data.physical_evaluations[0]?.cmj_height_cm}cm</p>
          <p>VO2 Max: {data.physical_evaluations[0]?.vo2_max_ml_kg_min}</p>
        </div>
      ) : (
        <p>No physical evaluations found</p>
      )}
      
      <h2>Risk Assessment</h2>
      {data?.risk_assessment ? (
        <div>
          <p>Injury Risk: {data.risk_assessment.injury_risk_category}</p>
          <p>Substitution Risk: {data.risk_assessment.substitution_risk_category}</p>
        </div>
      ) : (
        <p>No risk assessment found</p>
      )}
      
      <h2>Raw Data (check console for full details)</h2>
      <pre style={{ fontSize: '12px', maxHeight: '300px', overflow: 'auto' }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}'''

test_component_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\WellnessTest.jsx"
with open(test_component_file, 'w', encoding='utf-8') as f:
    f.write(test_component)

print("✅ Created test component at:")
print("   /src/pages/WellnessTest.jsx")
print("\n📋 To test:")
print("   1. Navigate to http://localhost:5173/api-test.html")
print("   2. Or add WellnessTest route to see React component")
print("   3. Check browser console for detailed logs")
print("   4. Verify API is returning wellness and physical data")
