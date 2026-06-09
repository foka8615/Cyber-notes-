# Log Analyzer v1 — Foka Cybersecurity 
# Finds ERROR lines in any log file
import sys import os def 
analyze_log(filename):
    if not os.path.exists(filename): 
        print(f"File not found: 
        {filename}") return
    
    errors = [] with open(filename, 
    'r') as f:
        for line_num, line in 
        enumerate(f, 1):
            if 'ERROR' in 
            line.upper():
                errors.append(f"Line 
                {line_num}: 
                {line.strip()}")
    
    print(f"\n=== LOG ANALYSIS REPORT 
    ===") print(f"File: {filename}") 
    print(f"Errors found: 
    {len(errors)}") 
    print("===========================") 
    for error in errors:
        print(error)
# Create a test log file
def create_test_log(): with 
    open('test.log', 'w') as f:
        f.write("INFO: System 
        started\n") f.write("ERROR: 
        Failed to connect to 
        database\n") f.write("INFO: 
        Retrying connection\n") 
        f.write("ERROR: Timeout after 
        30 seconds\n") f.write("INFO: 
        Connection established\n") 
        f.write("WARNING: Low 
        memory\n") f.write("ERROR: 
        Disk space critical\n")
create_test_log()
analyze_log('test.log')

