#!/usr/bin/env python3
"""
Direct test of dynamic pandas agent - bypass Django
"""

import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment
load_dotenv('/Users/rkkbti/Downloads/Finance-bot/.env')

# Add project to path
sys.path.insert(0, '/Users/rkkbti/Downloads/Finance-bot')

# Import directly
from rag.dynamic_pandas_agent import DynamicPandasAgent, load_dataframe
from rag.llm_config import get_llm

CSV_PATH = '/Users/rkkbti/Downloads/Finance-bot/media/uploads/MSFT Historical Data (1).csv'

def test_query(query_id, query, expected):
    """Test a single query"""
    print(f"\n{'='*80}")
    print(f"Test {query_id}")
    print(f"Query: {query}")
    print(f"Expected: {expected}")
    print(f"{'='*80}\n")

    try:
        # Load data
        df = load_dataframe(CSV_PATH)
        print(f"✅ Loaded {len(df)} rows from CSV\n")

        # Get LLM
        llm = get_llm()

        # Create agent
        agent = DynamicPandasAgent(llm)

        # Process query
        answer = agent.process_query(query, df, debug=True)

        print(f"\n{'='*80}")
        print(f"FINAL ANSWER:")
        print(f"{'='*80}")
        print(answer)
        print(f"{'='*80}\n")

        return answer

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("🧪 DIRECT TESTING - Dynamic Pandas Agent")
    print("="*80)

    # Test 1: Basic retrieval
    test_query("Q1.1",
               "What was Microsoft's closing price on 18-06-2026?",
               "$379.40")

    input("\n⏸️  Press Enter to continue to next test...")

    # Test 2: Highest volume (previously failed)
    test_query("Q3.3",
               "Which day recorded the highest trading volume?",
               "29-01-2026 with 128.86M")

    input("\n⏸️  Press Enter to continue to next test...")

    # Test 3: Percentage change (previously had iloc error)
    test_query("Q10.1",
               "What is the percentage increase from the first trading day to the last trading day?",
               "-9.35% (DECREASE)")

    input("\n⏸️  Press Enter to continue to next test...")

    # Test 4: Total volume (aggregation)
    test_query("Q10.5",
               "What is the total traded volume across the dataset?",
               "~10,068.75 million")

    input("\n⏸️  Press Enter to continue to next test...")

    # Test 5: Top 10 gains (ranking - previously failed)
    test_query("Q11.1",
               "Top 10 biggest gains.",
               "1. 09-04-2025: +10.13%")

    input("\n⏸️  Press Enter to continue to next test...")

    # Test 6: Top 10 volumes (ranking)
    test_query("Q11.3",
               "Top 10 highest volumes.",
               "1. 29-01-2026: 128.86M")

    input("\n⏸️  Press Enter to continue to next test...")

    # Test 7: Hallucination test - future date
    test_query("Q14.1",
               "What was Microsoft's closing price on 01-01-2028?",
               "Date not in dataset")

    input("\n⏸️  Press Enter to continue to next test...")

    # Test 8: Hallucination test - wrong company
    test_query("Q14.3",
               "Tell me about Tesla stock in this dataset.",
               "Only Microsoft data")

    print("\n✅ ALL PRIORITY TESTS COMPLETE!")


if __name__ == "__main__":
    main()
