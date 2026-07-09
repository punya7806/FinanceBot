"""
Interactive Testing Suite for Finance Bot
Shows each query, you test it in browser, then mark pass/fail
"""

import json
from datetime import datetime

# All test queries organized by category
TEST_SUITE = {
    "Category 1: Basic Retrieval": [
        "What was Microsoft's closing price on 18-06-2026?",
        "What was the opening price on 15-06-2026?",
        "What was the highest price on 16-06-2026?",
        "What was the lowest price on 17-06-2026?",
        "What was the trading volume on 12-06-2026?",
        "What was the percentage change on 18-06-2026?"
    ],

    "Category 2: Compare Two Dates": [
        "Compare the closing price on 17-06-2026 and 18-06-2026.",
        "Which day had the higher trading volume: 15-06-2026 or 16-06-2026?",
        "Was Microsoft's stock price higher on 12-06-2026 or 18-06-2026?",
        "Compare the high prices of 15-06-2026 and 17-06-2026.",
        "Which day had a larger percentage gain?"
    ],

    "Category 3: Highest / Lowest": [
        "Which day had the highest closing price in the dataset?",
        "Which day had the lowest closing price?",
        "Which day recorded the highest trading volume?",
        "Which day had the lowest trading volume?",
        "Which day had the highest daily gain?",
        "Which day had the largest daily loss?",
        "What was the maximum intraday high?",
        "What was the minimum intraday low?"
    ],

    "Category 4: Average Calculations": [
        "What is the average closing price?",
        "What is the average opening price?",
        "What is the average daily trading volume?",
        "What is the average percentage change?",
        "What is the average daily price range (High − Low)?"
    ],

    "Category 5: Filtering": [
        "Show all days where the closing price was above $390.",
        "List all trading days where Microsoft closed below $380.",
        "Find all days with a positive daily change.",
        "Find all days with a negative daily change.",
        "Show days where trading volume exceeded 50 million.",
        "List all days where the opening price was higher than the closing price.",
        "Find all days where the closing price was greater than the opening price."
    ],

    "Category 6: Sorting": [
        "List the top 10 highest closing prices.",
        "List the top 5 trading volume days.",
        "Show the five lowest closing prices.",
        "Rank all trading days by percentage change."
    ],

    "Category 7: Date Range Queries": [
        "What was Microsoft's average closing price during June 2026?",
        "Show all trading days in May 2026.",
        "How many trading days are available in March 2026?",
        "What was the highest closing price in April 2026?",
        "What was the lowest price recorded during January 2026?"
    ],

    "Category 8: Trend Analysis": [
        "Did Microsoft's stock generally increase or decrease during June 2026?",
        "How many consecutive days did the stock gain?",
        "What was the longest losing streak?",
        "Was the stock more volatile in May or June?",
        "Describe the overall price trend over the dataset."
    ],

    "Category 9: Multi-Step Reasoning": [
        "Which day had both a positive return and trading volume above 50 million?",
        "Find the date where the stock closed higher than it opened and also had the highest trading volume.",
        "Which month had the highest average closing price?",
        "What is the difference between the highest and lowest closing prices?",
        "On which day was the gap between High and Low the largest?"
    ],

    "Category 10: Mathematical Questions": [
        "What is the percentage increase from the first trading day to the last trading day?",
        "Calculate the average daily return.",
        "Calculate the median closing price.",
        "What is the standard deviation of the closing price?",
        "What is the total traded volume across the dataset?"
    ],

    "Category 11: Ranking": [
        "Top 10 biggest gains.",
        "Top 10 biggest losses.",
        "Top 10 highest volumes.",
        "Top 10 lowest volumes.",
        "Top 20 closing prices."
    ],

    "Category 12: Counting": [
        "How many trading days had a positive return?",
        "How many had a negative return?",
        "How many days closed above $400?",
        "How many days had trading volume greater than 40 million?",
        "How many days opened higher than they closed?"
    ],

    "Category 13: Retrieval Accuracy Tests": [
        "Tell me about trading on 18 June 2026.",
        "Give me all information for 17-06-2026.",
        "Summarize the market data for 15-06-2026.",
        "What happened on 12-06-2026?",
        "Show the complete record for 16-06-2026."
    ],

    "Category 14: Hallucination Tests (CRITICAL)": [
        "What was Microsoft's closing price on 01-01-2028?",
        "What happened on 30-02-2025?",
        "Tell me about Tesla stock in this dataset.",
        "What was Apple's highest closing price?",
        "What was Microsoft's dividend payment in this dataset?",
        "What was the PE ratio?",
        "What were Microsoft's earnings?",
        "What was the RSI on 17-06-2026?",
        "What was the MACD?",
        "What was the moving average for 20 days?"
    ],

    "Category 15: Complex RAG Evaluation": [
        "Summarize Microsoft's stock performance over the entire dataset.",
        "Identify the five most volatile trading days and explain why.",
        "Which month showed the strongest bullish trend?",
        "Which month had the largest average trading volume?",
        "Identify any unusual spikes in trading volume.",
        "Find dates where Microsoft gained more than 2% in a single day.",
        "Find dates where Microsoft lost more than 3% in a single day.",
        "Explain whether higher trading volume generally corresponded with larger price movements.",
        "Which trading day had the widest intraday range (High − Low)?",
        "Provide a month-by-month summary of Microsoft's stock performance."
    ]
}

def clear_screen():
    """Clear terminal screen"""
    import os
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    """Print test banner"""
    print("\n" + "="*80)
    print("🧪 FINANCE BOT - INTERACTIVE TEST SUITE")
    print("="*80)
    print("\n📋 Instructions:")
    print("  1. Copy the query shown below")
    print("  2. Paste it into the Finance Bot web UI (http://localhost:8000)")
    print("  3. Check the response")
    print("  4. Mark it as Pass (p) or Fail (f)")
    print("  5. Press Enter to continue to next query")
    print("\n" + "="*80 + "\n")

def run_interactive_tests():
    """Run interactive test suite"""
    results = {
        'passed': [],
        'failed': [],
        'skipped': [],
        'notes': {}
    }

    total_queries = sum(len(queries) for queries in TEST_SUITE.values())
    current_num = 0

    print_banner()
    input("Press Enter to start testing...")

    for category, queries in TEST_SUITE.items():
        clear_screen()
        print(f"\n{'='*80}")
        print(f"📂 {category}")
        print(f"{'='*80}\n")

        for i, query in enumerate(queries, 1):
            current_num += 1

            print(f"\n{'─'*80}")
            print(f"Query {current_num}/{total_queries} ({category} - Q{i})")
            print(f"{'─'*80}\n")

            # Show the query in a box
            print("┌" + "─"*78 + "┐")
            print(f"│ {query:<76} │")
            print("└" + "─"*78 + "┘\n")

            # Show what to check
            if "Category 14" in category:
                print("⚠️  HALLUCINATION TEST")
                print("   ✓ Should say 'data not available' or similar")
                print("   ✗ Should NOT make up data\n")

            # Get user input
            print("Options:")
            print("  [p] Pass - Works correctly")
            print("  [f] Fail - Wrong answer or error")
            print("  [s] Skip - Test later")
            print("  [n] Note - Add a note about this query")
            print("  [q] Quit - Save and exit")

            while True:
                choice = input("\nYour choice: ").strip().lower()

                if choice == 'p':
                    results['passed'].append(f"{category} - Q{i}: {query}")
                    print("✅ Marked as PASS\n")
                    break
                elif choice == 'f':
                    note = input("What went wrong? (optional): ").strip()
                    results['failed'].append(f"{category} - Q{i}: {query}")
                    if note:
                        results['notes'][query] = note
                    print("❌ Marked as FAIL\n")
                    break
                elif choice == 's':
                    results['skipped'].append(f"{category} - Q{i}: {query}")
                    print("⏭️  Skipped\n")
                    break
                elif choice == 'n':
                    note = input("Add note: ").strip()
                    if note:
                        results['notes'][query] = note
                    print("📝 Note saved. Now mark as pass/fail/skip.\n")
                    continue
                elif choice == 'q':
                    save_results(results, total_queries, current_num)
                    return
                else:
                    print("Invalid choice. Use p/f/s/n/q")

            # Show progress
            tested = len(results['passed']) + len(results['failed'])
            print(f"Progress: {tested} tested, {len(results['passed'])} passed, {len(results['failed'])} failed")

            input("\nPress Enter for next query...")
            clear_screen()

    # All done!
    save_results(results, total_queries, current_num)

def save_results(results, total, tested):
    """Save test results to file"""
    clear_screen()

    # Calculate stats
    num_passed = len(results['passed'])
    num_failed = len(results['failed'])
    num_skipped = len(results['skipped'])

    pass_rate = (num_passed / tested * 100) if tested > 0 else 0

    # Print summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80 + "\n")

    print(f"✅ Passed:  {num_passed}/{tested}")
    print(f"❌ Failed:  {num_failed}/{tested}")
    print(f"⏭️  Skipped: {num_skipped}")
    print(f"\n📈 Pass Rate: {pass_rate:.1f}%\n")

    if pass_rate >= 95:
        print("🎉 EXCELLENT! Agent is production-ready!")
    elif pass_rate >= 90:
        print("✨ GREAT! Just a few minor issues to fix.")
    elif pass_rate >= 80:
        print("👍 GOOD! Some improvements needed.")
    elif pass_rate >= 70:
        print("⚠️  FAIR! Significant work needed.")
    else:
        print("❌ NEEDS MAJOR WORK!")

    # Show failed queries
    if results['failed']:
        print(f"\n{'='*80}")
        print("❌ FAILED QUERIES:")
        print("="*80)
        for fail in results['failed']:
            print(f"\n  • {fail}")
            # Extract just the query text
            query_text = fail.split(': ', 1)[1] if ': ' in fail else fail
            if query_text in results['notes']:
                print(f"    Note: {results['notes'][query_text]}")

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"

    report = {
        'timestamp': timestamp,
        'total_queries': total,
        'tested': tested,
        'passed': num_passed,
        'failed': num_failed,
        'skipped': num_skipped,
        'pass_rate': pass_rate,
        'details': results
    }

    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*80}")
    print(f"💾 Results saved to: {filename}")
    print("="*80 + "\n")

    # Show what to do next
    if results['failed']:
        print("\n📋 NEXT STEPS:")
        print("  1. Review failed queries above")
        print("  2. Check server console for error details")
        print("  3. Report issues for debugging")
        print("  4. Re-test after fixes\n")

if __name__ == "__main__":
    try:
        run_interactive_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted. Progress will be saved.\n")
        # Could save partial results here if needed
