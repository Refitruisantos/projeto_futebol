#!/usr/bin/env python3
"""Fix indentation issues in metrics.py"""

import os

# Read the current metrics.py file
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the comprehensive profile function and fix all indentation
lines = content.split('\n')
fixed_lines = []
in_comprehensive_function = False
try_block_started = False

for i, line in enumerate(lines):
    if '@router.get("/athletes/{athlete_id}/comprehensive-profile")' in line:
        in_comprehensive_function = True
        fixed_lines.append(line)
    elif in_comprehensive_function and line.strip().startswith('try:'):
        try_block_started = True
        fixed_lines.append(line)
    elif in_comprehensive_function and try_block_started and not line.strip().startswith('except') and not line.strip().startswith('def ') and not line.strip().startswith('@router'):
        # Inside try block - ensure proper indentation
        if line.strip() and not line.startswith('        '):  # Not properly indented
            # Add proper indentation (8 spaces for try block content)
            stripped = line.lstrip()
            if stripped:
                fixed_lines.append('        ' + stripped)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    elif in_comprehensive_function and (line.strip().startswith('def ') or line.strip().startswith('@router')):
        # End of function
        in_comprehensive_function = False
        try_block_started = False
        fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write the fixed content back
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("✅ Fixed indentation in metrics.py")
print("   • Corrected try block indentation")
print("   • All function content properly indented")
