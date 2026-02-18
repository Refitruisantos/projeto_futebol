import React from 'react'
import { 
  ChartBarIcon, 
  UserGroupIcon, 
  EyeIcon,
  ArrowsPointingOutIcon,
  ScaleIcon
} from '@heroicons/react/24/outline'

export default function TacticalMetricsDisplay({ results }) {
  if (!results) return null

  const formatNumber = (value, decimals = 2) => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A'
    return Number(value).toFixed(decimals)
  }

  const formatInteger = (value) => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A'
    return Math.round(Number(value))
  }

  // Extract tactical analysis data
  const tacticalAnalysis = results.tactical_analysis || {}
  const playerTracking = results.player_tracking || {}
  const detectionQuality = results.detection_quality || {}

  // Mock detailed pressure and formation data (in production, this would come from the backend)
  const pressureMetrics = {
    ball_pressure_intensity: 4,
    avg_distance_to_ball: 8.5,
    min_distance_to_ball: 3.2,
    max_distance_to_ball: 15.8,
    avg_all_distances_to_ball: 12.3,
    home_team_pressure: 2,
    away_team_pressure: 2,
    pressure_ratio: 1.0,
    home_avg_pressure_distance: 7.8,
    away_avg_pressure_distance: 9.2,
    pressure_density: 0.04,
    total_players_analyzed: 22
  }

  const formationMetrics = {
    defensive_line_depth_avg: 18.5,
    defensive_line_depth_std: 2.1,
    defensive_line_compactness: 8.3,
    defensive_line_min_depth: 15.2,
    defensive_line_max_depth: 23.5,
    defensive_width: 45.8,
    defensive_width_avg: 34.0,
    defensive_width_std: 12.4,
    defensive_left_position: 12.5,
    defensive_right_position: 58.3,
    avg_gap_between_defenders: 11.5,
    min_gap_between_defenders: 6.2,
    max_gap_between_defenders: 18.9,
    total_defensive_gaps: 4,
    gap_consistency: 4.2
  }

  return (
    <div className="space-y-6">
      {/* Pressure Analysis Metrics */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <ScaleIcon className="h-5 w-5 mr-2 text-red-600" />
          Pressure Distance Analysis
        </h4>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-red-50 p-3 rounded">
            <p className="text-xs text-red-600 font-medium">Ball Pressure Intensity</p>
            <p className="text-xl font-bold text-red-800">{formatInteger(pressureMetrics.ball_pressure_intensity)}</p>
            <p className="text-xs text-red-500">players within 10m</p>
          </div>
          
          <div className="bg-red-50 p-3 rounded">
            <p className="text-xs text-red-600 font-medium">Avg Distance to Ball</p>
            <p className="text-xl font-bold text-red-800">{formatNumber(pressureMetrics.avg_distance_to_ball)}m</p>
            <p className="text-xs text-red-500">pressure zone average</p>
          </div>
          
          <div className="bg-red-50 p-3 rounded">
            <p className="text-xs text-red-600 font-medium">Min Distance to Ball</p>
            <p className="text-xl font-bold text-red-800">{formatNumber(pressureMetrics.min_distance_to_ball)}m</p>
            <p className="text-xs text-red-500">closest player</p>
          </div>
          
          <div className="bg-green-50 p-3 rounded">
            <p className="text-xs text-green-600 font-medium">Home Pressure Distance</p>
            <p className="text-xl font-bold text-green-800">{formatNumber(pressureMetrics.home_avg_pressure_distance)}m</p>
            <p className="text-xs text-green-500">average distance</p>
          </div>
          
          <div className="bg-blue-50 p-3 rounded">
            <p className="text-xs text-blue-600 font-medium">Away Pressure Distance</p>
            <p className="text-xl font-bold text-blue-800">{formatNumber(pressureMetrics.away_avg_pressure_distance)}m</p>
            <p className="text-xs text-blue-500">average distance</p>
          </div>
          
          <div className="bg-purple-50 p-3 rounded">
            <p className="text-xs text-purple-600 font-medium">Pressure Ratio</p>
            <p className="text-xl font-bold text-purple-800">{formatNumber(pressureMetrics.pressure_ratio)}</p>
            <p className="text-xs text-purple-500">home vs away</p>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-600 font-medium">Overall Avg Distance</p>
            <p className="text-lg font-bold text-gray-800">{formatNumber(pressureMetrics.avg_all_distances_to_ball)}m</p>
          </div>
          
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-600 font-medium">Pressure Density</p>
            <p className="text-lg font-bold text-gray-800">{formatNumber(pressureMetrics.pressure_density, 4)}</p>
          </div>
        </div>
      </div>

      {/* Formation Analysis Metrics */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <ArrowsPointingOutIcon className="h-5 w-5 mr-2 text-blue-600" />
          Defensive Formation Analysis
        </h4>
        
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-3 rounded">
            <p className="text-xs text-blue-600 font-medium">Defensive Line Depth</p>
            <p className="text-xl font-bold text-blue-800">{formatNumber(formationMetrics.defensive_line_depth_avg)}m</p>
            <p className="text-xs text-blue-500">average position</p>
          </div>
          
          <div className="bg-blue-50 p-3 rounded">
            <p className="text-xs text-blue-600 font-medium">Line Compactness</p>
            <p className="text-xl font-bold text-blue-800">{formatNumber(formationMetrics.defensive_line_compactness)}m</p>
            <p className="text-xs text-blue-500">depth variation</p>
          </div>
          
          <div className="bg-blue-50 p-3 rounded">
            <p className="text-xs text-blue-600 font-medium">Defensive Width</p>
            <p className="text-xl font-bold text-blue-800">{formatNumber(formationMetrics.defensive_width)}m</p>
            <p className="text-xs text-blue-500">total width</p>
          </div>
          
          <div className="bg-yellow-50 p-3 rounded">
            <p className="text-xs text-yellow-600 font-medium">Avg Gap Between Defenders</p>
            <p className="text-xl font-bold text-yellow-800">{formatNumber(formationMetrics.avg_gap_between_defenders)}m</p>
            <p className="text-xs text-yellow-500">spacing average</p>
          </div>
          
          <div className="bg-yellow-50 p-3 rounded">
            <p className="text-xs text-yellow-600 font-medium">Max Gap</p>
            <p className="text-xl font-bold text-yellow-800">{formatNumber(formationMetrics.max_gap_between_defenders)}m</p>
            <p className="text-xs text-yellow-500">largest gap</p>
          </div>
          
          <div className="bg-yellow-50 p-3 rounded">
            <p className="text-xs text-yellow-600 font-medium">Min Gap</p>
            <p className="text-xl font-bold text-yellow-800">{formatNumber(formationMetrics.min_gap_between_defenders)}m</p>
            <p className="text-xs text-yellow-500">smallest gap</p>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-600 font-medium">Line Consistency</p>
            <p className="text-lg font-bold text-gray-800">{formatNumber(formationMetrics.defensive_line_depth_std)}</p>
          </div>
          
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-600 font-medium">Width Consistency</p>
            <p className="text-lg font-bold text-gray-800">{formatNumber(formationMetrics.defensive_width_std)}</p>
          </div>
          
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-600 font-medium">Gap Consistency</p>
            <p className="text-lg font-bold text-gray-800">{formatNumber(formationMetrics.gap_consistency)}</p>
          </div>
          
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-600 font-medium">Total Gaps</p>
            <p className="text-lg font-bold text-gray-800">{formatInteger(formationMetrics.total_defensive_gaps)}</p>
          </div>
        </div>
      </div>

      {/* Player Tracking Summary */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <UserGroupIcon className="h-5 w-5 mr-2 text-green-600" />
          Player Tracking Summary
        </h4>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-green-50 p-3 rounded">
            <p className="text-xs text-green-600 font-medium">Home Team Players</p>
            <p className="text-xl font-bold text-green-800">{formatInteger(playerTracking.home_team_players)}</p>
            <p className="text-xs text-green-500">detected players</p>
          </div>
          
          <div className="bg-red-50 p-3 rounded">
            <p className="text-xs text-red-600 font-medium">Away Team Players</p>
            <p className="text-xl font-bold text-red-800">{formatInteger(playerTracking.away_team_players)}</p>
            <p className="text-xs text-red-500">detected players</p>
          </div>
          
          <div className="bg-blue-50 p-3 rounded">
            <p className="text-xs text-blue-600 font-medium">Referees</p>
            <p className="text-xl font-bold text-blue-800">{formatInteger(playerTracking.referees)}</p>
            <p className="text-xs text-blue-500">detected officials</p>
          </div>
          
          <div className="bg-purple-50 p-3 rounded">
            <p className="text-xs text-purple-600 font-medium">Avg Positions/Frame</p>
            <p className="text-xl font-bold text-purple-800">{formatNumber(playerTracking.avg_player_positions_per_frame)}</p>
            <p className="text-xs text-purple-500">total detections</p>
          </div>
        </div>
      </div>

      {/* Detection Quality Metrics */}
      {detectionQuality && Object.keys(detectionQuality).length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <EyeIcon className="h-5 w-5 mr-2 text-indigo-600" />
            Detection Quality Metrics
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-indigo-50 p-3 rounded">
              <p className="text-xs text-indigo-600 font-medium">Player ID Accuracy</p>
              <p className="text-xl font-bold text-indigo-800">{formatNumber(detectionQuality.player_id_accuracy * 100, 1)}%</p>
              <p className="text-xs text-indigo-500">identification rate</p>
            </div>
            
            <div className="bg-indigo-50 p-3 rounded">
              <p className="text-xs text-indigo-600 font-medium">Jersey Number Detection</p>
              <p className="text-xl font-bold text-indigo-800">{formatNumber(detectionQuality.jersey_number_detection * 100, 1)}%</p>
              <p className="text-xs text-indigo-500">number recognition</p>
            </div>
            
            <div className="bg-indigo-50 p-3 rounded">
              <p className="text-xs text-indigo-600 font-medium">Ball Tracking Continuity</p>
              <p className="text-xl font-bold text-indigo-800">{formatNumber(detectionQuality.ball_tracking_continuity * 100, 1)}%</p>
              <p className="text-xs text-indigo-500">tracking consistency</p>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Summary */}
      <div className="bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200 rounded-lg p-6">
        <h4 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
          <ChartBarIcon className="h-5 w-5 mr-2 text-gray-600" />
          Analysis Summary
        </h4>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <p className="text-gray-600">Total Frames</p>
            <p className="text-2xl font-bold text-gray-900">{formatInteger(results.total_frames)}</p>
          </div>
          
          <div className="text-center">
            <p className="text-gray-600">Ball Detections</p>
            <p className="text-2xl font-bold text-green-600">{formatInteger(results.ball_detections)}</p>
          </div>
          
          <div className="text-center">
            <p className="text-gray-600">Player Detections</p>
            <p className="text-2xl font-bold text-blue-600">{formatInteger(results.player_detections)}</p>
          </div>
          
          <div className="text-center">
            <p className="text-gray-600">Ball Visibility</p>
            <p className="text-2xl font-bold text-purple-600">{formatNumber(results.ball_visibility_percentage, 1)}%</p>
          </div>
        </div>
      </div>
    </div>
  )
}
