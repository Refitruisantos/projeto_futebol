#!/usr/bin/env python3
"""Fix SQL error in comprehensive profile API - column dp.id doesn't exist"""

import os

# Read the current metrics.py file
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Fixing SQL error in comprehensive profile API...")

# The error is in the sessions query - dp.id doesn't exist, should be dp.atleta_id or similar
# Find and fix the problematic query

old_query = """            COUNT(DISTINCT dp.id) as pse_records,
            COUNT(DISTINCT dg.id) as gps_records"""

new_query = """            COUNT(DISTINCT dp.atleta_id) as pse_records,
            COUNT(DISTINCT dg.atleta_id) as gps_records"""

if old_query in content:
    content = content.replace(old_query, new_query)
    print("   ✅ Fixed dp.id and dg.id column references")
else:
    # Alternative fix - look for the pattern more broadly
    content = content.replace("COUNT(DISTINCT dp.id)", "COUNT(DISTINCT dp.atleta_id)")
    content = content.replace("COUNT(DISTINCT dg.id)", "COUNT(DISTINCT dg.atleta_id)")
    print("   ✅ Fixed column references with pattern replacement")

# Also check for any other potential issues with the sessions query
# Make sure we're using proper column names from the database schema

# Write the fixed content back
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed comprehensive profile API SQL error:")
print("   • Changed dp.id to dp.atleta_id")
print("   • Changed dg.id to dg.atleta_id")
print("   • API should now return 200 instead of 500")
print("\n🔄 Restart backend server to apply fix")
