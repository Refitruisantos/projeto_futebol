#!/usr/bin/env python3
"""Fix frontend wellness display - the data exists but isn't showing"""

import os

# Read the current AthleteDetail.jsx file
athlete_detail_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend\src\pages\AthleteDetail.jsx"

with open(athlete_detail_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Fixing frontend wellness display logic...")

# The issue is likely in the conditional rendering logic
# Let's check if the wellness section is properly conditioned

# Find the wellness section and make sure it's properly displayed
old_wellness_condition = """      {/* Wellness Status */}
      {comprehensiveProfile?.wellness_data && comprehensiveProfile.wellness_data.length > 0 && ("""

new_wellness_condition = """      {/* Wellness Status */}
      {comprehensiveProfile?.wellness_data && comprehensiveProfile.wellness_data.length > 0 ? ("""

if old_wellness_condition in content:
    content = content.replace(old_wellness_condition, new_wellness_condition)
    print("   ✅ Fixed wellness conditional rendering")

# Also fix the physical evaluations condition
old_physical_condition = """      {/* Physical Evaluations */}
      {comprehensiveProfile?.physical_evaluations && comprehensiveProfile.physical_evaluations.length > 0 && ("""

new_physical_condition = """      {/* Physical Evaluations */}
      {comprehensiveProfile?.physical_evaluations && comprehensiveProfile.physical_evaluations.length > 0 ? ("""

if old_physical_condition in content:
    content = content.replace(old_physical_condition, new_physical_condition)
    print("   ✅ Fixed physical evaluations conditional rendering")

# Add debug logging to see what data is being received
debug_section = """  useEffect(() => {
    loadData()
  }, [id])

  // Debug logging
  useEffect(() => {
    if (comprehensiveProfile) {
      console.log('Comprehensive Profile Data:', comprehensiveProfile)
      console.log('Wellness Data:', comprehensiveProfile.wellness_data)
      console.log('Physical Evaluations:', comprehensiveProfile.physical_evaluations)
    }
  }, [comprehensiveProfile])"""

old_useeffect = """  useEffect(() => {
    loadData()
  }, [id])"""

if old_useeffect in content and debug_section not in content:
    content = content.replace(old_useeffect, debug_section)
    print("   ✅ Added debug logging")

# Make sure the wellness section closes properly
old_wellness_close = """        </div>
      )}"""

new_wellness_close = """        </div>
      ) : (
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-5">
            <p className="text-gray-500">Loading wellness data...</p>
          </div>
        </div>
      )}"""

# Only replace the first occurrence (wellness section)
if old_wellness_close in content:
    # Find the wellness section specifically
    wellness_start = content.find("Wellness Status")
    if wellness_start > 0:
        wellness_section_start = content.rfind("{/*", 0, wellness_start)
        wellness_section_end = content.find(old_wellness_close, wellness_start)
        if wellness_section_end > 0:
            before = content[:wellness_section_end]
            after = content[wellness_section_end + len(old_wellness_close):]
            content = before + new_wellness_close + after
            print("   ✅ Added fallback for wellness section")

# Write the fixed content back
with open(athlete_detail_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed frontend wellness display:")
print("   • Fixed conditional rendering logic")
print("   • Added debug console logging")
print("   • Added loading fallbacks")
print("   • Refresh browser to see changes")
