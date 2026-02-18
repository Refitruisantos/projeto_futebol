#!/usr/bin/env python3
"""Add wellness display to athlete detail page"""

import os

# Read the current AthleteDetail.jsx file
athlete_detail_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetail.jsx"

with open(athlete_detail_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where to insert wellness section - after the existing wellness chart
wellness_section = '''
        {/* Wellness Status */}
        {comprehensiveProfile?.wellness_data && comprehensiveProfile.wellness_data.length > 0 && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-5 border-b border-gray-200">
              <div className="flex items-center">
                <Heart className="w-5 h-5 text-green-500 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Wellness Status</h2>
              </div>
            </div>
            <div className="px-6 py-5">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {/* Current Wellness */}
                <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <Heart className="w-8 h-8 text-green-600" />
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-500">Current Score</p>
                      <p className="text-2xl font-semibold text-gray-900">
                        {comprehensiveProfile.wellness_data[0]?.wellness_score?.toFixed(1) || 'N/A'}
                      </p>
                      <p className="text-sm text-gray-600 capitalize">
                        {comprehensiveProfile.wellness_data[0]?.wellness_status || 'Unknown'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Wellness Trend */}
                {comprehensiveProfile.wellness_trends && (
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <TrendingUp className={`w-8 h-8 ${
                          comprehensiveProfile.wellness_trends.trend_direction === 'improving' ? 'text-green-600' :
                          comprehensiveProfile.wellness_trends.trend_direction === 'declining' ? 'text-red-600' :
                          'text-yellow-600'
                        }`} />
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-500">7-Day Trend</p>
                        <p className="text-2xl font-semibold text-gray-900">
                          {comprehensiveProfile.wellness_trends.avg_score_7d || 'N/A'}
                        </p>
                        <p className={`text-sm capitalize ${
                          comprehensiveProfile.wellness_trends.trend_direction === 'improving' ? 'text-green-600' :
                          comprehensiveProfile.wellness_trends.trend_direction === 'declining' ? 'text-red-600' :
                          'text-yellow-600'
                        }`}>
                          {comprehensiveProfile.wellness_trends.trend_direction}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Training Recommendation */}
                {comprehensiveProfile.wellness_data[0]?.training_recommendation && (
                  <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-4">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <Zap className="w-8 h-8 text-orange-600" />
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-500">Recommendation</p>
                        <p className="text-sm text-gray-900 font-medium">
                          {comprehensiveProfile.wellness_data[0].training_recommendation}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Readiness Score */}
                {comprehensiveProfile.wellness_data[0]?.readiness_score && (
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <Activity className="w-8 h-8 text-purple-600" />
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-500">Readiness</p>
                        <p className="text-2xl font-semibold text-gray-900">
                          {comprehensiveProfile.wellness_data[0].readiness_score.toFixed(1)}
                        </p>
                        <p className="text-sm text-gray-600">Training Ready</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Recent Wellness History */}
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Recent Wellness History</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Sleep</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Fatigue</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {comprehensiveProfile.wellness_data.slice(0, 7).map((wellness, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {new Date(wellness.data).toLocaleDateString('pt-PT')}
                          </td>
                          <td className="px-3 py-2 text-sm font-medium text-gray-900">
                            {wellness.wellness_score?.toFixed(1) || '-'}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-500">
                            {wellness.sleep_quality || '-'}/7
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-500">
                            {wellness.fatigue_level || '-'}/7
                          </td>
                          <td className="px-3 py-2 text-sm">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              wellness.wellness_status === 'excellent' ? 'bg-green-100 text-green-800' :
                              wellness.wellness_status === 'good' ? 'bg-blue-100 text-blue-800' :
                              wellness.wellness_status === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                              wellness.wellness_status === 'poor' ? 'bg-orange-100 text-orange-800' :
                              wellness.wellness_status === 'very_poor' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {wellness.wellness_status || 'Unknown'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Risk Assessment */}
        {comprehensiveProfile?.risk_assessment && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-5 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Risk Assessment</h2>
            </div>
            <div className="px-6 py-5">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                {/* Injury Risk */}
                <div className="text-center">
                  <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold ${
                    comprehensiveProfile.risk_assessment.injury_risk_category === 'low' ? 'bg-green-100 text-green-800' :
                    comprehensiveProfile.risk_assessment.injury_risk_category === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                    comprehensiveProfile.risk_assessment.injury_risk_category === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {comprehensiveProfile.risk_assessment.injury_risk_score?.toFixed(1)}
                  </div>
                  <p className="mt-2 text-sm font-medium text-gray-900">Injury Risk</p>
                  <p className="text-xs text-gray-500 capitalize">{comprehensiveProfile.risk_assessment.injury_risk_category}</p>
                </div>

                {/* Performance Risk */}
                <div className="text-center">
                  <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold ${
                    comprehensiveProfile.risk_assessment.performance_risk_category === 'low' ? 'bg-green-100 text-green-800' :
                    comprehensiveProfile.risk_assessment.performance_risk_category === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                    comprehensiveProfile.risk_assessment.performance_risk_category === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {comprehensiveProfile.risk_assessment.performance_risk_score?.toFixed(1)}
                  </div>
                  <p className="mt-2 text-sm font-medium text-gray-900">Performance Risk</p>
                  <p className="text-xs text-gray-500 capitalize">{comprehensiveProfile.risk_assessment.performance_risk_category}</p>
                </div>

                {/* Substitution Risk */}
                <div className="text-center">
                  <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold ${
                    comprehensiveProfile.risk_assessment.substitution_risk_category === 'low' ? 'bg-green-100 text-green-800' :
                    comprehensiveProfile.risk_assessment.substitution_risk_category === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                    comprehensiveProfile.risk_assessment.substitution_risk_category === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {comprehensiveProfile.risk_assessment.substitution_risk_score?.toFixed(1)}
                  </div>
                  <p className="mt-2 text-sm font-medium text-gray-900">Substitution Risk</p>
                  <p className="text-xs text-gray-500 capitalize">{comprehensiveProfile.risk_assessment.substitution_risk_category}</p>
                </div>
              </div>

              {/* Recommendations */}
              <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-900">Training Recommendation</h4>
                  <p className="mt-1 text-sm text-blue-700">{comprehensiveProfile.risk_assessment.training_recommendation}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-green-900">Match Recommendation</h4>
                  <p className="mt-1 text-sm text-green-700">{comprehensiveProfile.risk_assessment.match_recommendation}</p>
                </div>
              </div>
            </div>
          </div>
        )}
'''

# Find the position to insert wellness section (after existing wellness chart)
if '{/* Wellness */}' in content:
    # Insert after existing wellness section
    insert_pos = content.find('        </div>\n      )}') + len('        </div>\n      )}')
    new_content = content[:insert_pos] + '\n\n' + wellness_section + '\n' + content[insert_pos:]
else:
    # Insert before the closing div of the main container
    insert_pos = content.rfind('    </div>\n  )\n}')
    new_content = content[:insert_pos] + wellness_section + '\n\n' + content[insert_pos:]

# Write the updated content
with open(athlete_detail_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Added wellness display to AthleteDetail.jsx:")
print("   • Current wellness status with score and trend")
print("   • Risk assessment visualization")
print("   • Recent wellness history table")
print("   • Training and match recommendations")
print("   • Uses comprehensive profile API data")
