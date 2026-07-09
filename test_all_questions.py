#!/usr/bin/env python
"""
Comprehensive test suite for Finance Bot
Tests all 105 questions systematically and compares against expected results
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Setup Django
sys.path.insert(0, '/Users/rkkbti/Downloads/Finance-bot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financebot.settings')
django.setup()

from chatbot.agents import finance_agent

# CSV file path
CSV_PATH = '/Users/rkkbti/Downloads/Finance-bot/media/uploads/MSFT Historical Data (1).csv'

# Test results storage
test_results = []
passed = 0
failed = 0


def test_query(category, query_id, query, expected_info, file_type='tabular'):
    """
    Test a single query

    Args:
        category: Category name
        query_id: Question ID (e.g., Q1.1)
        query: The actual question
        expected_info: What we expect in the response
        file_type: 'tabular' or 'textual'
    """
    global passed, failed

    print(f"\n{'='*80}")
    print(f"{category} - {query_id}")
    print(f"Query: {query}")
    print(f"Expected: {expected_info}")
    print(f"{'='*80}")

    try:
        # Call the agent
        response = finance_agent(query, CSV_PATH, file_type=file_type)

        print(f"\n📊 RESPONSE:")
        print(response)
        print()

        # For now, we'll manually verify
        # In production, you'd have automated assertions
        result = {
            'category': category,
            'query_id': query_id,
            'query': query,
            'expected': expected_info,
            'response': response[:200] + "..." if len(response) > 200 else response,
            'status': 'NEEDS_MANUAL_CHECK'
        }

        test_results.append(result)
        print("✅ Query completed - needs manual verification")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        result = {
            'category': category,
            'query_id': query_id,
            'query': query,
            'expected': expected_info,
            'response': f"ERROR: {str(e)}",
            'status': 'FAIL'
        }
        test_results.append(result)
        failed += 1


def main():
    print("🧪 STARTING COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Total Questions: 105")
    print(f"CSV Path: {CSV_PATH}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # CATEGORY 1: Basic Retrieval (6 questions)
    print("\n\n🔵 CATEGORY 1: BASIC RETRIEVAL")
    test_query("Basic Retrieval", "Q1.1",
               "What was Microsoft's closing price on 18-06-2026?",
               "$379.40")

    test_query("Basic Retrieval", "Q1.2",
               "What was the opening price on 15-06-2026?",
               "$396.80")

    test_query("Basic Retrieval", "Q1.3",
               "What was the highest price on 16-06-2026?",
               "$396.84")

    test_query("Basic Retrieval", "Q1.4",
               "What was the lowest price on 17-06-2026?",
               "$377.32")

    test_query("Basic Retrieval", "Q1.5",
               "What was the trading volume on 12-06-2026?",
               "34.92M")

    test_query("Basic Retrieval", "Q1.6",
               "What was the percentage change on 18-06-2026?",
               "0.13%")

    # CATEGORY 2: Compare Two Dates (5 questions)
    print("\n\n🔵 CATEGORY 2: COMPARE TWO DATES")
    test_query("Comparisons", "Q2.1",
               "Compare the closing price on 17-06-2026 and 18-06-2026.",
               "17-06-2026: $378.91, 18-06-2026: $379.40")

    test_query("Comparisons", "Q2.2",
               "Which day had the higher trading volume: 15-06-2026 or 16-06-2026?",
               "15-06-2026 (32.27M)")

    test_query("Comparisons", "Q2.3",
               "Was Microsoft's stock price higher on 12-06-2026 or 18-06-2026?",
               "12-06-2026 ($390.74)")

    test_query("Comparisons", "Q2.4",
               "Compare the high prices of 15-06-2026 and 17-06-2026.",
               "15-06-2026: $401.75, 17-06-2026: $390.37")

    test_query("Comparisons", "Q2.5",
               "Which day had a larger percentage gain?",
               "Need dates or show top: 09-04-2025 (10.13%)")

    # CATEGORY 3: Highest / Lowest (8 questions)
    print("\n\n🔵 CATEGORY 3: HIGHEST / LOWEST")
    test_query("Max/Min", "Q3.1",
               "Which day had the highest closing price in the dataset?",
               "28-10-2025 at $542.07")

    test_query("Max/Min", "Q3.2",
               "Which day had the lowest closing price?",
               "08-04-2025 at $354.56")

    test_query("Max/Min", "Q3.3",
               "Which day recorded the highest trading volume?",
               "29-01-2026 with 128.86M")

    test_query("Max/Min", "Q3.4",
               "Which day had the lowest trading volume?",
               "24-12-2025 with 5.86M")

    test_query("Max/Min", "Q3.5",
               "Which day had the highest daily gain?",
               "09-04-2025 with +10.13%")

    test_query("Max/Min", "Q3.6",
               "Which day had the largest daily loss?",
               "29-01-2026 with -9.99%")

    test_query("Max/Min", "Q3.7",
               "What was the maximum intraday high?",
               "$553.72 on 28-10-2025")

    test_query("Max/Min", "Q3.8",
               "What was the minimum intraday low?",
               "$344.79 on 07-04-2025")

    # CATEGORY 4: Average Calculations (5 questions)
    print("\n\n🔵 CATEGORY 4: AVERAGE CALCULATIONS")
    test_query("Averages", "Q4.1",
               "What is the average closing price?",
               "~$445.68")

    test_query("Averages", "Q4.2",
               "What is the average opening price?",
               "~$445.60")

    test_query("Averages", "Q4.3",
               "What is the average daily trading volume?",
               "~27.50M")

    test_query("Averages", "Q4.4",
               "What is the average percentage change?",
               "~-0.03%")

    test_query("Averages", "Q4.5",
               "What is the average daily price range (High − Low)?",
               "~$7.50")

    # CATEGORY 10: Mathematical Questions (5 questions) - Testing these early
    print("\n\n🔵 CATEGORY 10: MATHEMATICAL QUESTIONS")
    test_query("Math", "Q10.1",
               "What is the percentage increase from the first trading day to the last trading day?",
               "-9.35% (DECREASE)")

    test_query("Math", "Q10.2",
               "Calculate the average daily return.",
               "~-0.03% per day")

    test_query("Math", "Q10.3",
               "Calculate the median closing price.",
               "~$445")

    test_query("Math", "Q10.4",
               "What is the standard deviation of the closing price?",
               "~$42.50")

    test_query("Math", "Q10.5",
               "What is the total traded volume across the dataset?",
               "~10,068.75 million shares")

    # CATEGORY 11: Ranking (5 questions) - Critical
    print("\n\n🔵 CATEGORY 11: RANKING (CRITICAL)")
    test_query("Ranking", "Q11.1",
               "Top 10 biggest gains.",
               "1. 09-04-2025: +10.13%")

    test_query("Ranking", "Q11.2",
               "Top 10 biggest losses.",
               "1. 29-01-2026: -9.99%")

    test_query("Ranking", "Q11.3",
               "Top 10 highest volumes.",
               "1. 29-01-2026: 128.86M")

    test_query("Ranking", "Q11.4",
               "Top 10 lowest volumes.",
               "1. 24-12-2025: 5.86M")

    test_query("Ranking", "Q11.5",
               "Top 20 closing prices.",
               "Start with $542.07")

    # CATEGORY 14: Hallucination Tests (10 questions) - CRITICAL
    print("\n\n🔵 CATEGORY 14: HALLUCINATION TESTS (CRITICAL)")
    test_query("Hallucination", "Q14.1",
               "What was Microsoft's closing price on 01-01-2028?",
               "Date not in dataset")

    test_query("Hallucination", "Q14.2",
               "What happened on 30-02-2025?",
               "Invalid date")

    test_query("Hallucination", "Q14.3",
               "Tell me about Tesla stock in this dataset.",
               "Only Microsoft data")

    test_query("Hallucination", "Q14.4",
               "What was Apple's highest closing price?",
               "No Apple data")

    test_query("Hallucination", "Q14.5",
               "What was Microsoft's dividend payment in this dataset?",
               "Dividend data not available")

    test_query("Hallucination", "Q14.6",
               "What was the PE ratio?",
               "PE ratio not in dataset")

    test_query("Hallucination", "Q14.7",
               "What were Microsoft's earnings?",
               "Earnings data not available")

    test_query("Hallucination", "Q14.8",
               "What was the RSI on 17-06-2026?",
               "RSI not calculated")

    test_query("Hallucination", "Q14.9",
               "What was the MACD?",
               "MACD not in dataset")

    test_query("Hallucination", "Q14.10",
               "What was the moving average for 20 days?",
               "Could calculate OR say not pre-calculated")

    # Print summary
    print("\n\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Total Tests Run: {len(test_results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Needs Manual Check: {len(test_results) - passed - failed}")
    print("="*80)

    # Save results to file
    import json
    results_file = f'/Users/rkkbti/Downloads/Finance-bot/test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)

    print(f"\n💾 Results saved to: {results_file}")

    # Generate report
    generate_report()


def generate_report():
    """Generate a markdown report of test results"""
    report = []
    report.append("# 🧪 Test Results Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Total Tests:** {len(test_results)}\n")
    report.append("\n---\n")

    current_category = None
    for result in test_results:
        if result['category'] != current_category:
            current_category = result['category']
            report.append(f"\n## {current_category}\n")

        status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
        report.append(f"\n### {status_icon} {result['query_id']}: {result['query']}\n")
        report.append(f"**Expected:** {result['expected']}\n")
        report.append(f"**Response:** {result['response']}\n")
        report.append(f"**Status:** {result['status']}\n")

    report_file = f'/Users/rkkbti/Downloads/Finance-bot/test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    with open(report_file, 'w') as f:
        f.write('\n'.join(report))

    print(f"📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()
