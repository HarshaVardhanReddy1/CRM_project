#!/usr/bin/env python3
"""
Test script for Node 1 (Retrieval Agent)
Tests if the retrieval agent correctly identifies tables, relationships, and warnings
"""

import json
import sys
from backend.agents.retrieval import retrieval_agent

# Test cases from SAMPLE_QUESTIONS.md
test_questions = [
    # Level 2 - Medium difficulty
    {
        "question": "List all active leads",
        "expected_primary": "Leads",
        "expected_tables": ["Leads"]
    },
    {
        "question": "Show me all leads with their detailed information",
        "expected_primary": "Leads",
        "expected_tables": ["Leads", "LeadDetails", "LeadStageTransitions"]
    },
    {
        "question": "How many messages are in each chat?",
        "expected_primary": "Chats",
        "expected_tables": ["Chats", "ChatMessages"]
    },
    {
        "question": "Get the attendance record for each user showing present and absent days",
        "expected_primary": "Users",
        "expected_tables": ["Users", "Attendances"]
    },
    {
        "question": "Show employee names and their total salary from payslips",
        "expected_primary": "Users",
        "expected_tables": ["Users", "Payslips"]
    },
    {
        "question": "List all leads that have documents attached",
        "expected_primary": "Leads",
        "expected_tables": ["Leads", "LeadDocuments"]
    },
    {
        "question": "Show leads with their stage transitions history",
        "expected_primary": "Leads",
        "expected_tables": ["Leads", "LeadStageTransitions"]
    },
    {
        "question": "Get payroll information with employee names and payslip details",
        "expected_primary": "Users",
        "expected_tables": ["Users", "Payslips"]
    },
    {
        "question": "Show all lead co-applicants with their main lead information",
        "expected_primary": "Leads",
        "expected_tables": ["Leads", "LeadCoApplicants"]
    },
    {
        "question": "List campaigns and count how many leads are associated with each",
        "expected_primary": "Campaigns",
        "expected_tables": ["Campaigns", "Leads"]
    },
]

def test_retrieval():
    """Test retrieval agent on sample questions"""

    print("=" * 80)
    print("TESTING NODE 1: RETRIEVAL AGENT")
    print("=" * 80)

    passed = 0
    failed = 0

    for i, test in enumerate(test_questions, 1):
        print(f"\n[Test {i}/{len(test_questions)}] {test['question'][:60]}...")

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
                "retrieval_result": {}
            }

            # Run retrieval agent
            result = retrieval_agent(state)

            # Check results
            primary = result.get("retrieval_result", {}).get("primary_table")
            tables = result.get("retrieved_tables", [])
            warnings = result.get("sparse_warnings", [])

            print(f"  Primary: {primary}")
            print(f"  Tables: {tables}")
            if warnings:
                print(f"  Warnings: {warnings}")

            # Validate
            primary_match = primary == test.get("expected_primary")

            # Check if expected tables are in retrieved tables
            expected = test.get("expected_tables", [])
            tables_match = all(t in tables for t in expected)

            if primary_match and tables_match:
                print(f"  ✓ PASS")
                passed += 1
            else:
                print(f"  ✗ FAIL")
                if not primary_match:
                    print(f"    - Expected primary: {test.get('expected_primary')}, got: {primary}")
                if not tables_match:
                    print(f"    - Expected tables: {expected}, got: {tables}")
                failed += 1

                # Print full result for debugging
                print(f"    Full result:")
                print(f"    {json.dumps(result['retrieval_result'], indent=2)}")

        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{len(test_questions)} passed, {failed}/{len(test_questions)} failed")
    print("=" * 80)

    return failed == 0

if __name__ == "__main__":
    success = test_retrieval()
    sys.exit(0 if success else 1)
