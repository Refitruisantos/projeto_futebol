import React from 'react'
import { DocumentTextIcon } from '@heroicons/react/24/outline'

export default function TacticalReport({ analysis, results }) {
  if (!results) return null

  // Extract actual metrics from results
  const tactical = results.tactical_analysis || {}
  const pressure = tactical.pressure_analysis || {}
  const formation = tactical.formation_analysis || {}

  // Generate tactical interpretations based on actual data
  const generateTacticalInsights = () => {
    const insights = []

    // Defensive Line Alignment Analysis
    const lineCompactness = formation.line_compactness || 0
    const defensiveWidth = formation.defensive_width || 0
    const avgGap = formation.avg_gap_between_defenders || 0
    const maxGap = formation.max_gap || 0
    const minGap = formation.min_gap || 0

    if (lineCompactness > 0) {
      if (lineCompactness < 10) {
        insights.push("Players maintain excellent defensive line alignment with tight compactness")
      } else if (lineCompactness < 15) {
        insights.push("Defensive line shows moderate alignment with acceptable depth variation")
      } else {
        insights.push("Defensive line lacks proper alignment with excessive depth variation")
      }
    }

    // Gap Analysis
    if (maxGap > 0 && minGap > 0) {
      const gapVariation = maxGap - minGap
      if (gapVariation < 10) {
        insights.push("Consistent spacing between defenders maintains structural integrity")
      } else if (gapVariation < 15) {
        insights.push("Moderate spacing inconsistencies present defensive vulnerabilities")
      } else {
        insights.push("Significant spacing gaps create exploitable defensive weaknesses")
      }
    }

    // Pressure Effectiveness Analysis
    const ballPressure = pressure.ball_pressure_intensity || 0
    const avgDistance = pressure.avg_distance_to_ball || 0
    const pressureRatio = pressure.pressure_ratio || 0

    if (ballPressure > 0) {
      if (ballPressure >= 3) {
        insights.push("Effective ball pressure with multiple players engaging")
      } else if (ballPressure >= 2) {
        insights.push("Moderate ball pressure with limited player involvement")
      } else {
        insights.push("Insufficient ball pressure allowing opponent freedom")
      }
    }

    // Distance-based Pressure Analysis
    if (avgDistance > 0) {
      if (avgDistance < 8) {
        insights.push("High-intensity pressing disrupts opponent ball control")
      } else if (avgDistance < 12) {
        insights.push("Moderate pressing maintains defensive shape while applying pressure")
      } else {
        insights.push("Low pressing intensity allows opponent time and space")
      }
    }

    // Team Balance Analysis
    if (pressureRatio > 0) {
      if (Math.abs(pressureRatio - 1.0) < 0.2) {
        insights.push("Balanced team engagement with equal pressure contribution")
      } else if (pressureRatio > 1.2) {
        insights.push("Home team dominates pressure application")
      } else if (pressureRatio < 0.8) {
        insights.push("Away team shows superior pressing intensity")
      }
    }

    // Formation Width Analysis
    if (defensiveWidth > 0) {
      if (defensiveWidth > 40) {
        insights.push("Wide defensive formation provides good field coverage")
      } else if (defensiveWidth > 30) {
        insights.push("Compact defensive formation prioritizes central protection")
      } else {
        insights.push("Narrow defensive formation vulnerable to wide attacks")
      }
    }

    return insights.length > 0 ? insights : ["Analysis data insufficient for tactical interpretation"]
  }

  const tacticalInsights = generateTacticalInsights()

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
        <DocumentTextIcon className="h-5 w-5 mr-2 text-blue-600" />
        Tactical Analysis Interpretation
      </h4>
      
      <div className="space-y-3">
        {tacticalInsights.map((insight, index) => (
          <div key={index} className="bg-gray-50 border-l-4 border-blue-500 p-4">
            <p className="text-gray-800 font-medium">{insight}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
