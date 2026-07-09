"""
Quick test for aggregation query
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financebot.settings')
django.setup()

from chatbot.agents import finance_agent

CSV_PATH = '/Users/rkkbti/Downloads/Finance-bot/media/uploads/MSFT Historical Data (1).csv'

print("Testing aggregation query...")
print("="*80)

query = "What is the total traded volume across the dataset?"
print(f"Query: {query}\n")

try:
    result = finance_agent(query, CSV_PATH, file_type='tabular')
    print("SUCCESS!")
    print("="*80)
    print(result)
    print("="*80)
except Exception as e:
    print("ERROR!")
    print("="*80)
    print(f"Error: {e}")
    print("="*80)
