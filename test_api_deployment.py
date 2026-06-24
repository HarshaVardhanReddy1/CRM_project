#!/usr/bin/env python3
"""
Test script for deployed API with 2-node pipeline
Tests the /query endpoint with various questions
"""

import requests
import json
import sys
from time import sleep

# API endpoint
API_URL = "http://localhost:8000/api/query"
HISTORY_CLEAR_URL = "http://localhost:8000/api/history"

# Test cases
test_cases = [
    {
        "question": "List all active leads",
        "description": "Simple single table query"
    },
    {
        "question": "Get the attendance record for each user showing present and absent days",
        "description": "Aggregation with GROUP BY"
    },
    {
        "question": "Show me all leads with their detailed information",
        "description": "Leads with LeadDetails (sparse join)"
    },
    {
        "question": "How many messages are in each chat?",
        "description": "Count with GROUP BY"
    },
    {
        "question": "List all leads that have documents attached",
        "description": "Critical sparse table (94.8% NULL)"
    }
]


def test_api():
    """Test deployed API"""

    print("=" * 80)
    print("TESTING DEPLOYED API (2-Node Pipeline)")
    print("=" * 80)
    print(f"\nAPI Endpoint: {API_URL}")

    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/docs", timeout=2)
        if response.status_code == 404:
            print("\n⚠️  WARNING: API docs not found at /docs")
        else:
            print("\n✓ API is running")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API at http://localhost:8000")
        print("Please start the FastAPI server first:")
        print("  uvicorn backend.main:app --reload")
        return False

    # Clear history
    print("\nClearing conversation history...")
    try:
        requests.delete(HISTORY_CLEAR_URL, timeout=5)
        print("✓ History cleared")
    except Exception as e:
        print(f"⚠️  Could not clear history: {e}")

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        description = test_case["description"]

        print(f"\n[Test {i}/{len(test_cases)}] {question[:70]}...")
        print(f"  Description: {description}")

        try:
            # Make API request with retrieval info
            payload = {
                "question": question,
                "include_retrieval_info": True
            }

            print(f"  📡 Calling API...")
            response = requests.post(API_URL, json=payload, timeout=30)

            if response.status_code != 200:
                print(f"  ❌ HTTP Error: {response.status_code}")
                print(f"     {response.text[:200]}")
                failed += 1
                continue

            result = response.json()

            # Check response structure
            if "sql" not in result or "response" not in result:
                print(f"  ❌ Invalid response structure")
                print(f"     Keys: {list(result.keys())}")
                failed += 1
                continue

            sql = result.get("sql", "")
            response_text = result.get("response", "")
            retrieval_info = result.get("retrieval_info", {})

            # Validate SQL
            if not sql or len(sql.strip()) == 0:
                print(f"  ❌ No SQL generated")
                failed += 1
                continue

            sql_upper = sql.upper()
            if "SELECT" not in sql_upper or "FROM" not in sql_upper:
                print(f"  ❌ Invalid SQL structure (missing SELECT or FROM)")
                failed += 1
                continue

            print(f"  ✓ SQL generated ({len(sql)} chars)")
            print(f"    Preview: {sql[:100]}...")

            # Check retrieval info
            if retrieval_info:
                primary = retrieval_info.get("primary_table")
                tables = retrieval_info.get("tables_used", [])
                warnings = retrieval_info.get("sparse_warnings", [])

                print(f"  ✓ Retrieval Info:")
                print(f"    - Primary table: {primary}")
                print(f"    - Tables used: {tables}")
                if warnings:
                    print(f"    - Warnings: {warnings}")

            # Check response
            if response_text and response_text != "No results found.":
                result_lines = str(response_text).split("\n")[:3]
                print(f"  ✓ Results returned ({len(str(response_text))} chars)")
                for line in result_lines:
                    if line.strip():
                        print(f"    {line[:70]}")
            else:
                print(f"  ℹ️  No results or empty result set")

            print(f"  ✓ PASS")
            passed += 1

        except requests.exceptions.Timeout:
            print(f"  ❌ Request timeout (30 seconds)")
            failed += 1
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection error")
            failed += 1
        except json.JSONDecodeError:
            print(f"  ❌ Invalid JSON response")
            failed += 1
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{len(test_cases)} passed, {failed}/{len(test_cases)} failed")
    print("=" * 80)

    if passed == len(test_cases):
        print("\n🎉 All API tests passed!")
        print("\nAPI is ready for use:")
        print(f"  POST {API_URL}")
        print("\nExample curl command:")
        print("""
  curl -X POST http://localhost:8000/api/query \\
    -H "Content-Type: application/json" \\
    -d '{
      "question": "Get the attendance record for each user",
      "include_retrieval_info": true
    }'
        """)
        return True
    else:
        print(f"\n❌ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
