"""
Comprehensive Test Suite for Finance Bot Dynamic Agent
Tests all query categories systematically
"""

import os
import sys
import django


# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financebot.settings')
django.setup()

from chatbot.agents import finance_agent
import pandas as pd
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Path to CSV file
CSV_PATH = 'C:/Users/RKK/Downloads/financeBotv1/media/uploads/MSFT Historical Data (1).csv'


# Test Results TrackerC:\Users\RKK\Downloads\financeBotv1\media\uploads\MSFT Historical Data (1).csv
results = {
    'passed': [],
    'failed': [],
    'errors': []
}

def run_test(category, query_num, query, expected_behavior=None):
    """Run a single test query"""
    print(f"\n{'='*80}")
    print(f"{Fore.CYAN}Category: {category}")
    print(f"{Fore.YELLOW}Query {query_num}: {query}")
    print(f"{'='*80}")

    try:
        answer = finance_agent(query, CSV_PATH, file_type='tabular')
        
        print(f"\n{Fore.GREEN}✓ Response:")
        print(f"{Style.DIM}{answer}{Style.RESET_ALL}")

        # Check for error indicators
        if 'error' in answer.lower() or 'unfortunately' in answer.lower():
            if expected_behavior == 'should_fail':
                results['passed'].append(f"{category} - Q{query_num}: {query}")
                print(f"\n{Fore.GREEN}✓ PASS (correctly rejected)")
            else:
                results['failed'].append(f"{category} - Q{query_num}: {query}")
                print(f"\n{Fore.RED}✗ FAIL (unexpected error)")
        else:
            results['passed'].append(f"{category} - Q{query_num}: {query}")
            print(f"\n{Fore.GREEN}✓ PASS")

        return True

    except Exception as e:
        results['errors'].append(f"{category} - Q{query_num}: {query} | Error: {str(e)}")
        print(f"\n{Fore.RED}✗ ERROR: {str(e)}")
        return False


# ============================================================================
# CATEGORY 1: BASIC RETRIEVAL
# ============================================================================
print(f"\n\n{Fore.MAGENTA}{'='*80}")
print(f"CATEGORY 1: BASIC RETRIEVAL")
print(f"{'='*80}\n")

basic_queries = [
    "What was Microsoft's closing price on 18-06-2026?",
    "What was the opening price on 15-06-2026?",
    "What was the highest price on 16-06-2026?",
    "What was the lowest price on 17-06-2026?",
    "What was the trading volume on 12-06-2026?",
    "What was the percentage change on 18-06-2026?"
]

for i, query in enumerate(basic_queries, 1):
    run_test("Basic Retrieval", i, query)
    input(f"\n{Fore.BLUE}Press Enter to continue to next query...")


# ============================================================================
# CATEGORY 2: COMPARE TWO DATES
# ============================================================================
print(f"\n\n{Fore.MAGENTA}{'='*80}")
print(f"CATEGORY 2: COMPARE TWO DATES")
print(f"{'='*80}\n")

comparison_queries = [
    "Compare the closing price on 17-06-2026 and 18-06-2026.",
    "Which day had the higher trading volume: 15-06-2026 or 16-06-2026?",
    "Was Microsoft's stock price higher on 12-06-2026 or 18-06-2026?",
    "Compare the high prices of 15-06-2026 and 17-06-2026.",
    "Which day had a larger percentage gain?"
]

for i, query in enumerate(comparison_queries, 1):
    run_test("Compare Two Dates", i, query)
    input(f"\n{Fore.BLUE}Press Enter to continue to next query...")


# ============================================================================
# CATEGORY 3: HIGHEST / LOWEST
# ============================================================================
print(f"\n\n{Fore.MAGENTA}{'='*80}")
print(f"CATEGORY 3: HIGHEST / LOWEST")
print(f"{'='*80}\n")

minmax_queries = [
    "Which day had the highest closing price in the dataset?",
    "Which day had the lowest closing price?",
    "Which day recorded the highest trading volume?",
    "Which day had the lowest trading volume?",
    "Which day had the highest daily gain?",
    "Which day had the largest daily loss?",
    "What was the maximum intraday high?",
    "What was the minimum intraday low?"
]

for i, query in enumerate(minmax_queries, 1):
    run_test("Highest/Lowest", i, query)
    input(f"\n{Fore.BLUE}Press Enter to continue to next query...")


# ============================================================================
# CATEGORY 4: AVERAGE CALCULATIONS
# ============================================================================
print(f"\n\n{Fore.MAGENTA}{'='*80}")
print(f"CATEGORY 4: AVERAGE CALCULATIONS")
print(f"{'='*80}\n")

average_queries = [
    "What is the average closing price?",
    "What is the average opening price?",
    "What is the average daily trading volume?",
    "What is the average percentage change?",
    "What is the average daily price range (High − Low)?"
]

for i, query in enumerate(average_queries, 1):
    run_test("Average Calculations", i, query)
    input(f"\n{Fore.BLUE}Press Enter to continue to next query...")


# ============================================================================
# CATEGORY 5: FILTERING
# ============================================================================
print(f"\n\n{Fore.MAGENTA}{'='*80}")
print(f"CATEGORY 5: FILTERING")
print(f"{'='*80}\n")

filtering_queries = [
    "Show all days where the closing price was above $390.",
    "List all trading days where Microsoft closed below $380.",
    "Find all days with a positive daily change.",
    "Find all days with a negative daily change.",
    "Show days where trading volume exceeded 50 million.",
    "List all days where the opening price was higher than the closing price."
]

for i, query in enumerate(filtering_queries, 1):
    run_test("Filtering", i, query)
    input(f"\n{Fore.BLUE}Press Enter to continue to next query...")


# ============================================================================
# FINAL SUMMARY
# ============================================================================
print(f"\n\n{Fore.MAGENTA}{'='*80}")
print(f"TEST SUMMARY")
print(f"{'='*80}\n")

total = len(results['passed']) + len(results['failed']) + len(results['errors'])
print(f"{Fore.GREEN}✓ Passed: {len(results['passed'])}/{total}")
print(f"{Fore.RED}✗ Failed: {len(results['failed'])}/{total}")
print(f"{Fore.RED}✗ Errors: {len(results['errors'])}/{total}")

if results['failed']:
    print(f"\n{Fore.RED}Failed Tests:")
    for fail in results['failed']:
        print(f"  - {fail}")

if results['errors']:
    print(f"\n{Fore.RED}Error Tests:")
    for error in results['errors']:
        print(f"  - {error}")

# Calculate pass rate
pass_rate = (len(results['passed']) / total * 100) if total > 0 else 0
print(f"\n{Fore.CYAN}Pass Rate: {pass_rate:.1f}%")

if pass_rate >= 90:
    print(f"\n{Fore.GREEN}🎉 EXCELLENT! Agent is working very well!")
elif pass_rate >= 70:
    print(f"\n{Fore.YELLOW}⚠️  GOOD! Some improvements needed.")
else:
    print(f"\n{Fore.RED}❌ NEEDS WORK! Significant issues to fix.")
