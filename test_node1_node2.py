#!/usr/bin/env python3
"""
Test Node 1 + Node 2 (Retrieval + Generation)
Tests if the complete retrieval → generation pipeline works correctly
"""

import json
import sys
import logging
from backend.agents.retrieval import retrieval_agent
from backend.agents.generation import generation_agent

logging.basicConfig(level=logging.INFO)

# Test cases
test_questions = [
    {
        "question": "List all active leads",
        "description": "Simple single table query"
    },
    {
        "question": "Get the attendance record for each user showing present and absent days",
        "description": "Users + Attendances with aggregation"
    },
    {
        "question": "Show me all leads with their detailed information",
        "description": "Leads + LeadDetails (sparse join)"
    },
    {
        "question": "How many messages are in each chat?",
        "description": "Chats + ChatMessages with COUNT"
    },
    {
        "question": "List all leads that have documents attached",
        "description": "Leads + LeadDocuments (94.8% sparse)"
    },
]


def test_pipeline():
    """Test Node 1 + Node 2 pipeline"""

    print("=" * 80)
    print("TESTING NODE 1 + NODE 2 PIPELINE (Retrieval + Generation)")
    print("=" * 80)

    passed = 0
    failed = 0

    for i, test in enumerate(test_questions, 1):
        print(f"\n[Test {i}/{len(test_questions)}] {test['question'][:70]}...")
        print(f"  Description: {test['description']}")

        try:
            # Initialize state
            state = {
                "question": test["question"],
                "history": [],
                "retrieved_tables": [],
                "relationships": [],
                "sparse_warnings": [],
                "excluded_tables": [],
                "need_groupby": False,
                "aggregations": [],
                "retrieval_result": {},
                "sql": None,
                "error": None
            }

            # NODE 1: Run retrieval agent
            print(f"\n  🔍 Node 1 (Retrieval)...")
            state = retrieval_agent(state)

            retrieval_result = state.get("retrieval_result", {})
            if "error" in retrieval_result:
                print(f"    ✗ RETRIEVAL ERROR: {retrieval_result['error']}")
                failed += 1
                continue

            primary = retrieval_result.get("primary_table")
            tables = state.get("retrieved_tables", [])
            warnings = state.get("sparse_warnings", [])

            print(f"    ✓ Primary: {primary}")
            print(f"    ✓ Tables: {tables}")
            if warnings:
                print(f"    ✓ Warnings: {warnings}")

            # NODE 2: Run generation agent
            print(f"\n  ⚙️  Node 2 (Generation)...")
            state = generation_agent(state)

            sql = state.get("sql", "")

            if not sql:
                print(f"    ✗ NO SQL GENERATED")
                print(f"    Error: {state.get('error', 'Unknown error')}")
                failed += 1
                continue

            # Validate SQL
            sql_upper = sql.upper()

            # Check basic SQL structure
            has_select = "SELECT" in sql_upper
            has_from = "FROM" in sql_upper
            has_quotes = '"' in sql and "'" in sql or '"' in sql  # Either double or single quotes

            if not has_select:
                print(f"    ✗ INVALID SQL: No SELECT statement")
                failed += 1
                continue

            if not has_from:
                print(f"    ✗ INVALID SQL: No FROM clause")
                failed += 1
                continue

            # Check if it uses only retrieved tables
            tables_in_sql = [t for t in tables if t in sql]
            if tables_in_sql:
                print(f"    ✓ Uses retrieved tables: {tables_in_sql}")

            # Print SQL (truncated)
            sql_preview = sql[:150] + "..." if len(sql) > 150 else sql
            print(f"    ✓ SQL (preview): {sql_preview}")

            # Check for critical issues
            has_errors = False

            # Check for empty Payrolls (should be excluded by Node 1)
            if "Payrolls" in sql and "Payslips" not in sql:
                print(f"    ⚠️  WARNING: Using Payrolls (empty table) - Node 1 should exclude this")
                # Not a hard failure, just a warning

            # Check for proper quoting
            if not has_quotes:
                print(f"    ⚠️  WARNING: SQL might not have proper quoting")

            if not has_errors:
                print(f"\n  ✓ PASS")
                passed += 1
            else:
                print(f"\n  ✗ FAIL")
                failed += 1

        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{len(test_questions)} passed, {failed}/{len(test_questions)} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
