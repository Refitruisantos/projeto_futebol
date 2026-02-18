#!/usr/bin/env python3
"""Fix exception handling in comprehensive profile endpoint to properly handle 404s"""

import os

# Read the metrics.py file
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("🔧 Fixing exception handling in comprehensive profile endpoint...")

# Replace the problematic exception handling
old_exception_handling = """    except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")"""

new_exception_handling = """    except HTTPException:
        # Re-raise HTTPExceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")"""

if old_exception_handling in content:
    content = content.replace(old_exception_handling, new_exception_handling)
    print("   ✅ Fixed exception handling to preserve HTTPExceptions")
else:
    print("   ⚠️  Could not find exact exception handling pattern")
    
    # Try alternative pattern
    alt_pattern = """except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")"""
    
    if alt_pattern in content:
        alt_replacement = """except HTTPException:
        # Re-raise HTTPExceptions (like 404) as-is
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")"""
        
        content = content.replace(alt_pattern, alt_replacement)
        print("   ✅ Fixed exception handling with alternative pattern")
    else:
        print("   ❌ Could not find exception handling pattern to fix")

# Write the fixed content back
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed comprehensive profile exception handling:")
print("   • HTTPExceptions (404) will now pass through correctly")
print("   • Only genuine errors will return 500")
print("   • Frontend will get proper 404 for non-existent athletes")
print("\n🔄 Restart backend server to apply fix")
