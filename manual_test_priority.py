#!/usr/bin/env python3
"""
Manual testing script - tests priority queries one by one
Run this and manually verify each result
"""

import sys
import os

# Add project to path
sys.path.insert(0, '/Users/rkkbti/Downloads/Finance-bot')
os.chdir('/Users/rkkbti/Downloads/Finance-bot')

# Set environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financebot.settings')

# Import after setting up paths
import django
django.setup()

from chatbot.agents import finance_agent

CSV_PATH = '/Users/rkkbti/Downloads/Finance-bot/media/uploads/MSFT Historical Data (1).csv'

# Priority test queries
PRIORITY_TESTS = [
    ("Q1.1", "What was Microsoft's closing price on 18-06-2026?", "$379.40"),
    ("Q3.3", "Which day recorded the highest trading volume?", "29-01-2026 with 128.86M"),
    ("Q10.1", "What is the percentage increase from the first trading day to the last trading day?", "-9.35% (DECREASE)"),
    ("Q10.5", "What is the total traded volume across the dataset?", "~10,068.75 million"),
    ("Q11.1", "Top 10 biggest gains.", "1. 09-04-2025: +10.13%"),
    ("Q11.3", "Top 10 highest volumes.", "1. 29-01-2026: 128.86M"),
    ("Q14.1", "What was Microsoft's closing price on 01-01-2028?", "Date not in dataset"),
    ("Q14.3", "Tell me about Tesla stock in this dataset.", "Only Microsoft data"),
]

def main():
    print("🧪 PRIORITY TESTS - Run and verify manually")
    print("="*80)

    for query_id, query, expected in PRIORITY_TESTS:
        print(f"\n{'='*80}")
        print(f"Test {query_id}")
        print(f"Query: {query}")
        print(f"Expected: {expected}")
        print(f"{'='*80}")

        try:
            response = finance_agent(query, CSV_PATH, file_type='tabular')
            print(f"\n📊 RESPONSE:")
            print(response)
            print()

            # Ask user
            user_input = input("✅ PASS or ❌ FAIL? (p/f): ").strip().lower()
            if user_input == 'f':
                print(f"❌ MARKED AS FAIL")
            else:
                print(f"✅ MARKED AS PASS")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            input("Press Enter to continue...")

        print()

if __name__ == "__main__":
    main()
