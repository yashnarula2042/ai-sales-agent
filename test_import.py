import sys
import os
from src.lead_manager import LeadManager

# Mocking Flask app context if needed, but LeadManager should work standalone
lm = LeadManager()
file_path = 'data/sample_leads (1) - sample_leads (1).csv.csv'
print(f"Testing import on: {file_path}")
try:
    result = lm.import_from_csv(file_path)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")

# Read the debug log
if os.path.exists('debug_import.log'):
    with open('debug_import.log', 'r') as f:
        print("\n--- DEBUG LOG ---")
        print(f.read())
