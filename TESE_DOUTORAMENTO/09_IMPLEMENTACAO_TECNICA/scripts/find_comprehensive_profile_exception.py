#!/usr/bin/env python3
"""Find the exception handling in comprehensive profile endpoint"""

import os

# Read the metrics.py file to find the exception handling
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔍 Looking for exception handling in comprehensive profile endpoint...")

# Find the comprehensive profile function
start_marker = "def get_comprehensive_athlete_profile"
end_marker = "def "

start_pos = content.find(start_marker)
if start_pos == -1:
    print("❌ Could not find comprehensive profile function")
    exit()

# Find the end of the function (next function definition or end of file)
next_func_pos = content.find(end_marker, start_pos + len(start_marker))
if next_func_pos == -1:
    function_content = content[start_pos:]
else:
    function_content = content[start_pos:next_func_pos]

print(f"📄 Function found, length: {len(function_content)} characters")

# Look for exception handling
if "except Exception as e:" in function_content:
    print("✅ Found exception handling")
    
    # Extract the exception block
    except_pos = function_content.find("except Exception as e:")
    except_block = function_content[except_pos:except_pos+500]
    print(f"Exception block:\n{except_block}")
    
else:
    print("❌ No exception handling found")
    
# Look for HTTPException raises
if "raise HTTPException" in function_content:
    print("✅ Found HTTPException usage")
    
    # Find all HTTPException raises
    lines = function_content.split('\n')
    for i, line in enumerate(lines):
        if "raise HTTPException" in line:
            print(f"Line {i}: {line.strip()}")
else:
    print("❌ No HTTPException found")

print("\n🎯 The issue is likely that the exception handler is catching HTTPException")
print("   and re-raising it as a 500 error instead of letting it pass through")
