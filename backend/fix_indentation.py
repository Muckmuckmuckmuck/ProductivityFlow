#!/usr/bin/env python3
"""
Fix indentation error in application.py
"""

def fix_indentation():
    """Fix the indentation error around line 535"""
    
    with open('application.py', 'r') as f:
        lines = f.readlines()
    
    # Fix the indentation around line 535
    for i, line in enumerate(lines):
        if 'init_scheduler()' in line and 'try:' in lines[i-1]:
            # Fix the indentation of the init_scheduler line
            lines[i] = '            init_scheduler()\n'
            # Fix the next line (logging.info)
            if i+1 < len(lines) and 'logging.info' in lines[i+1]:
                lines[i+1] = '            logging.info("✅ Scheduler initialization successful in ensure_initialization")\n'
    
    # Write the fixed content back
    with open('application.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Fixed indentation error in application.py")

if __name__ == "__main__":
    fix_indentation() 