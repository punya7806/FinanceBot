"""
Simple Test Script - Tests by calling the web API directly
No Django imports needed - just makes HTTP requests
"""

import requests
import json
import time
from datetime import datetime

# Server URL
BASE_URL = "http://localhost:8000"

# Test queries organized by priority
PRIORITY_TESTS = {
    "Bug Fix Tests": [
        "Which day recorded the highest trading volume?",
        "Was Microsoft's stock price higher on 12-06-2026 or 18-06-2026?",
        "Compare the closing price on 17-06-2026 and 18-06-2026.",
    ],

    "Hallucination Tests (CRITICAL)": [
        "What was Microsoft's closing price on 01-01-2028?",
        "Tell me about Tesla stock in this dataset.",
        "What was the PE ratio?",
    ],

    "Basic Functionality": [
        "What was Microsoft's closing price on 18-06-2026?",
        "Show all days where the closing price was above $390.",
        "What is the average closing price?",
        "Top 10 highest closing prices.",
    ]
}

def test_query(query, session_id="test123"):
    """Send a query to the bot and get response"""
    try:
        response = requests.post(
            f"{BASE_URL}/ask/",
            data={
                'question': query,
                'session_id': session_id
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'answer': data.get('answer', 'No answer'),
                'error': None
            }
        else:
            return {
                'success': False,
                'answer': None,
                'error': f"HTTP {response.status_code}: {response.text[:200]}"
            }

    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'answer': None,
            'error': "Server not running! Start with: python manage.py runserver"
        }
    except Exception as e:
        return {
            'success': False,
            'answer': None,
            'error': str(e)
        }

def print_header():
    """Print test header"""
    print("\n" + "="*80)
    print("🧪 FINANCE BOT - AUTOMATED TEST SUITE")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: {BASE_URL}")
    print("="*80 + "\n")

def check_hallucination(answer):
    """Check if response indicates hallucination"""
    hallucination_indicators = [
        'not available', 'not found', 'don\'t have',
        'not in', 'only microsoft', 'no information',
        'cannot find', 'doesn\'t contain'
    ]

    answer_lower = answer.lower()
    for indicator in hallucination_indicators:
        if indicator in answer_lower:
            return False  # Good - rejected the query

    return True  # Bad - might be hallucinating

def run_tests():
    """Run all priority tests"""
    print_header()

    # Check if server is running
    print("🔍 Checking if server is running...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running!\n")
    except:
        print("❌ Server is NOT running!")
        print("\nPlease start the server first:")
        print("  cd /Users/rkkbti/Downloads/Finance-bot")
        print("  python manage.py runserver\n")
        return

    # Results tracking
    results = {
        'passed': [],
        'failed': [],
        'errors': []
    }

    total = 0

    # Run tests by category
    for category, queries in PRIORITY_TESTS.items():
        print(f"\n{'='*80}")
        print(f"📂 {category}")
        print(f"{'='*80}\n")

        for i, query in enumerate(queries, 1):
            total += 1

            print(f"Query {total}: {query}")
            print(f"{'─'*80}")

            # Send query
            result = test_query(query)

            if not result['success']:
                # Error occurred
                print(f"❌ ERROR: {result['error']}\n")
                results['errors'].append({
                    'category': category,
                    'query': query,
                    'error': result['error']
                })
                continue

            answer = result['answer']
            print(f"\n📝 Response Preview:")
            print(f"{answer[:200]}..." if len(answer) > 200 else answer)

            # Check response quality
            is_hallucination = False
            if "Hallucination" in category:
                is_hallucination = check_hallucination(answer)

                if is_hallucination:
                    print(f"\n❌ FAIL: Possible hallucination detected!")
                    results['failed'].append({
                        'category': category,
                        'query': query,
                        'reason': 'Hallucination - made up data',
                        'answer': answer
                    })
                else:
                    print(f"\n✅ PASS: Correctly rejected query")
                    results['passed'].append({
                        'category': category,
                        'query': query
                    })
            else:
                # Check for error indicators in response
                error_keywords = ['error', 'unfortunately', 'cannot', 'unable']
                has_error = any(keyword in answer.lower() for keyword in error_keywords)

                if has_error and len(answer) < 100:
                    print(f"\n❌ FAIL: Got error or insufficient response")
                    results['failed'].append({
                        'category': category,
                        'query': query,
                        'reason': 'Error in response',
                        'answer': answer
                    })
                else:
                    print(f"\n✅ PASS: Got valid response")
                    results['passed'].append({
                        'category': category,
                        'query': query
                    })

            print()
            time.sleep(1)  # Be nice to the server

    # Print summary
    print_summary(results, total)

    # Save results
    save_results(results)

def print_summary(results, total):
    """Print test summary"""
    num_passed = len(results['passed'])
    num_failed = len(results['failed'])
    num_errors = len(results['errors'])

    pass_rate = (num_passed / total * 100) if total > 0 else 0

    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80 + "\n")

    print(f"Total Tests:  {total}")
    print(f"✅ Passed:    {num_passed} ({pass_rate:.1f}%)")
    print(f"❌ Failed:    {num_failed}")
    print(f"⚠️  Errors:    {num_errors}")

    if pass_rate >= 95:
        print(f"\n🎉 EXCELLENT! Agent is working great!")
    elif pass_rate >= 85:
        print(f"\n✨ GOOD! Minor improvements needed.")
    elif pass_rate >= 70:
        print(f"\n⚠️  FAIR! Some issues to fix.")
    else:
        print(f"\n❌ NEEDS WORK! Significant issues found.")

    # Show failures
    if results['failed']:
        print(f"\n{'='*80}")
        print("❌ FAILED TESTS:")
        print("="*80)
        for fail in results['failed']:
            print(f"\nCategory: {fail['category']}")
            print(f"Query: {fail['query']}")
            print(f"Reason: {fail['reason']}")
            print(f"Response: {fail['answer'][:100]}...")

    # Show errors
    if results['errors']:
        print(f"\n{'='*80}")
        print("⚠️  ERRORS:")
        print("="*80)
        for error in results['errors']:
            print(f"\nCategory: {error['category']}")
            print(f"Query: {error['query']}")
            print(f"Error: {error['error']}")

def save_results(results):
    """Save results to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*80}")
    print(f"💾 Results saved to: {filename}")
    print("="*80 + "\n")

if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure you have:")
    print("  1. Started the Django server (python manage.py runserver)")
    print("  2. Uploaded the CSV file in the web UI (http://localhost:8000)")
    print("\nPress Enter to start testing, or Ctrl+C to cancel...")

    try:
        input()
        run_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing cancelled.\n")
