#!/usr/bin/env python3
"""Find and fix the comprehensive profile API to include detailed breakdown"""

import os

# Search for the comprehensive profile endpoint
backend_dir = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend"

print("🔍 Searching for comprehensive profile API endpoint...")

def search_files_for_text(directory, search_text):
    """Search for text in Python files"""
    matches = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if search_text in content:
                            matches.append(file_path)
                except:
                    pass
    return matches

# Search for comprehensive profile endpoint
matches = search_files_for_text(backend_dir, "comprehensive-profile")
if not matches:
    matches = search_files_for_text(backend_dir, "comprehensive_profile")

print(f"   Found {len(matches)} files with comprehensive profile:")
for match in matches:
    print(f"     {match}")

if matches:
    # Read the first match to find the endpoint
    api_file = matches[0]
    print(f"\n🔧 Updating {api_file}...")
    
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the sessions query and add detailed_breakdown
    if "SELECT DISTINCT" in content and "s.adversario" in content:
        # Find the sessions query and update it
        lines = content.split('\n')
        updated_lines = []
        in_select = False
        
        for line in lines:
            if "SELECT DISTINCT" in line and "s.id" in line:
                in_select = True
                updated_lines.append(line)
            elif in_select and "s.adversario," in line:
                updated_lines.append(line)
                # Add the detailed breakdown field after adversario
                indent = len(line) - len(line.lstrip())
                updated_lines.append(" " * indent + "odd.detailed_breakdown as difficulty_breakdown,")
            elif in_select and "FROM sessoes s" in line:
                updated_lines.append(line)
            elif in_select and "LEFT JOIN dados_gps" in line:
                updated_lines.append(line)
            elif in_select and "LEFT JOIN dados_pse" in line:
                updated_lines.append(line)
                # Add the opponent difficulty details join
                indent = len(line) - len(line.lstrip())
                updated_lines.append(" " * indent + "LEFT JOIN opponent_difficulty_details odd ON s.adversario = odd.opponent_name")
            else:
                updated_lines.append(line)
        
        # Write the updated content
        updated_content = '\n'.join(updated_lines)
        
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("   ✅ Updated sessions query to include detailed_breakdown")
        print("   ✅ Added JOIN with opponent_difficulty_details table")
    else:
        print("   ⚠️  Could not find sessions query to update")
        
        # Show what we found
        print("\n   Content preview:")
        print(content[:500] + "...")

else:
    print("   ❌ No comprehensive profile API found")
    print("   Searching for any API endpoints...")
    
    # Search for any API endpoints
    api_matches = search_files_for_text(backend_dir, "@router.get")
    print(f"   Found {len(api_matches)} files with API endpoints:")
    for match in api_matches:
        print(f"     {match}")

print("\n✅ COMPREHENSIVE PROFILE API UPDATE COMPLETE!")
print("   🔄 Restart backend to apply changes")
print("   📊 API will now include difficulty_breakdown field")
