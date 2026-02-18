#!/usr/bin/env python3
"""Add physical tests display to athlete detail frontend"""

import os

# Read the current AthleteDetail.jsx file
athlete_detail_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetail.jsx"

with open(athlete_detail_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Physical tests section to add
physical_tests_section = '''
        {/* Physical Evaluations */}
        {comprehensiveProfile?.physical_evaluations && comprehensiveProfile.physical_evaluations.length > 0 && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-5 border-b border-gray-200">
              <div className="flex items-center">
                <Zap className="w-5 h-5 text-blue-500 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Physical Evaluations</h2>
              </div>
            </div>
            <div className="px-6 py-5">
              {/* Latest Evaluation Summary */}
              {comprehensiveProfile.physical_evaluations[0] && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-4">
                    Latest Evaluation ({new Date(comprehensiveProfile.physical_evaluations[0].data_avaliacao).toLocaleDateString('pt-PT')})
                  </h3>
                  <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
                    {/* Speed Tests */}
                    <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">
                          {comprehensiveProfile.physical_evaluations[0].sprint_35m_seconds?.toFixed(2) || 'N/A'}s
                        </div>
                        <div className="text-sm text-gray-600">35m Sprint</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {comprehensiveProfile.physical_evaluations[0].percentile_speed}th percentile
                        </div>
                      </div>
                    </div>

                    <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">
                          {comprehensiveProfile.physical_evaluations[0].test_5_0_5_seconds?.toFixed(2) || 'N/A'}s
                        </div>
                        <div className="text-sm text-gray-600">5-0-5 Agility</div>
                        <div className="text-xs text-gray-500 mt-1">Change of direction</div>
                      </div>
                    </div>

                    {/* Power Tests */}
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {comprehensiveProfile.physical_evaluations[0].cmj_height_cm?.toFixed(1) || 'N/A'}cm
                        </div>
                        <div className="text-sm text-gray-600">CMJ Height</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {comprehensiveProfile.physical_evaluations[0].percentile_power}th percentile
                        </div>
                      </div>
                    </div>

                    {/* Endurance */}
                    <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {comprehensiveProfile.physical_evaluations[0].vo2_max_ml_kg_min?.toFixed(1) || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-600">VO₂ Max</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {comprehensiveProfile.physical_evaluations[0].percentile_endurance}th percentile
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Detailed Test Results */}
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Detailed Test Results</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">35m Sprint</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">5-0-5</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">CMJ</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Squat Jump</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Hop Test</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Bronco</th>
                        <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">VO₂ Max</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {comprehensiveProfile.physical_evaluations.map((evaluation, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-3 py-2 text-sm text-gray-900">
                            {new Date(evaluation.data_avaliacao).toLocaleDateString('pt-PT')}
                          </td>
                          <td className="px-3 py-2 text-sm">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              evaluation.tipo_avaliacao === 'pre_season' ? 'bg-blue-100 text-blue-800' :
                              evaluation.tipo_avaliacao === 'mid_season' ? 'bg-green-100 text-green-800' :
                              evaluation.tipo_avaliacao === 'post_season' ? 'bg-purple-100 text-purple-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {evaluation.tipo_avaliacao === 'pre_season' ? 'Pre-Season' :
                               evaluation.tipo_avaliacao === 'mid_season' ? 'Mid-Season' :
                               evaluation.tipo_avaliacao === 'post_season' ? 'Post-Season' :
                               evaluation.tipo_avaliacao}
                            </span>
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right font-mono">
                            {evaluation.sprint_35m_seconds?.toFixed(2) || '-'}s
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right font-mono">
                            {evaluation.test_5_0_5_seconds?.toFixed(2) || '-'}s
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right font-mono">
                            {evaluation.cmj_height_cm?.toFixed(1) || '-'}cm
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right font-mono">
                            {evaluation.squat_jump_height_cm?.toFixed(1) || '-'}cm
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right font-mono">
                            {evaluation.hop_test_distance_m?.toFixed(2) || '-'}m
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right font-mono">
                            {evaluation.bronco_test_time_seconds ? `${Math.floor(evaluation.bronco_test_time_seconds / 60)}:${String(Math.floor(evaluation.bronco_test_time_seconds % 60)).padStart(2, '0')}` : '-'}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 text-right font-mono">
                            {evaluation.vo2_max_ml_kg_min?.toFixed(1) || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Performance Comparison */}
              {comprehensiveProfile.physical_evaluations.length > 1 && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Performance Changes</h4>
                  <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                    {(() => {
                      const latest = comprehensiveProfile.physical_evaluations[0];
                      const previous = comprehensiveProfile.physical_evaluations[1];
                      
                      const sprintChange = latest.sprint_35m_seconds && previous.sprint_35m_seconds ? 
                        (previous.sprint_35m_seconds - latest.sprint_35m_seconds) : null;
                      const cmjChange = latest.cmj_height_cm && previous.cmj_height_cm ? 
                        (latest.cmj_height_cm - previous.cmj_height_cm) : null;
                      const vo2Change = latest.vo2_max_ml_kg_min && previous.vo2_max_ml_kg_min ? 
                        (latest.vo2_max_ml_kg_min - previous.vo2_max_ml_kg_min) : null;
                      
                      return (
                        <>
                          <div className="text-center">
                            <div className={`text-lg font-semibold ${sprintChange > 0 ? 'text-green-600' : sprintChange < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                              {sprintChange ? `${sprintChange > 0 ? '+' : ''}${sprintChange.toFixed(2)}s` : 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500">35m Sprint</div>
                          </div>
                          <div className="text-center">
                            <div className={`text-lg font-semibold ${cmjChange > 0 ? 'text-green-600' : cmjChange < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                              {cmjChange ? `${cmjChange > 0 ? '+' : ''}${cmjChange.toFixed(1)}cm` : 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500">CMJ Height</div>
                          </div>
                          <div className="text-center">
                            <div className={`text-lg font-semibold ${vo2Change > 0 ? 'text-green-600' : vo2Change < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                              {vo2Change ? `${vo2Change > 0 ? '+' : ''}${vo2Change.toFixed(1)}` : 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500">VO₂ Max</div>
                          </div>
                        </>
                      );
                    })()}
                  </div>
                </div>
              )}

              {/* Test Descriptions */}
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">Test Descriptions</h4>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 text-xs text-blue-700">
                  <div><strong>35m Sprint:</strong> Maximum speed over 35 meters</div>
                  <div><strong>5-0-5 Agility:</strong> Change of direction speed test</div>
                  <div><strong>CMJ:</strong> Countermovement jump for lower body power</div>
                  <div><strong>Squat Jump:</strong> Concentric-only jump test</div>
                  <div><strong>Hop Test:</strong> Single-leg horizontal jump distance</div>
                  <div><strong>Bronco Test:</strong> Multi-stage fitness test for endurance</div>
                  <div><strong>VO₂ Max:</strong> Maximum oxygen uptake capacity</div>
                  <div><strong>Percentiles:</strong> Ranking compared to position peers</div>
                </div>
              </div>
            </div>
          </div>
        )}
'''

# Find the position to insert physical tests section (after risk assessment section)
if 'Risk Assessment' in content:
    # Insert after risk assessment section
    insert_pos = content.find('          </div>\n        )}\n\n      </div>') + len('          </div>\n        )}\n\n      </div>')
    new_content = content[:insert_pos] + '\n\n' + physical_tests_section + '\n' + content[insert_pos:]
else:
    # Insert before the closing div of the main container
    insert_pos = content.rfind('      </div>\n    </div>\n  )\n}')
    new_content = content[:insert_pos] + physical_tests_section + '\n\n' + content[insert_pos:]

# Write the updated content
with open(athlete_detail_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Added physical tests display to AthleteDetail.jsx:")
print("   • Latest evaluation summary with key metrics")
print("   • Detailed test results table with all measurements")
print("   • Performance comparison between evaluations")
print("   • Color-coded improvements/declines")
print("   • Test descriptions and percentile rankings")
print("   • Pre-season vs Mid-season evaluation tracking")
print("   • Professional sports science test battery display")
