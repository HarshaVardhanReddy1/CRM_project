from backend.db.connection import engine
from sqlalchemy import inspect
import json

def get_schema_for_tables(tables: list) -> str:
    """
    Build focused schema for only the retrieved tables.
    Only includes columns from tables that were identified by Node 1 (Retrieval).
    """
    inspector = inspect(engine)

    schema_parts = []

    for table_name in tables:
        try:
            columns = inspector.get_columns(table_name)
            col_list = [f"{col['name']} ({col['type']})" for col in columns[:10]]  # Limit to 10 columns for brevity

            schema_parts.append(f"Table: {table_name}\n" +
                              "  Columns: " + ", ".join(col_list) +
                              (f"... ({len(columns)} total)" if len(columns) > 10 else ""))
        except Exception as e:
            schema_parts.append(f"Table: {table_name}\n  Error fetching schema: {str(e)}")

    return "\n".join(schema_parts)


def format_relationships(relationships: list) -> str:
    """Format the JOIN relationships for the prompt."""
    if not relationships:
        return "No relationships (single table query)"

    lines = []
    for rel in relationships:
        lines.append(f"  {rel.get('join_type', 'JOIN')} {rel.get('table')} ON {rel.get('on')}")
        if rel.get('reason'):
            lines.append(f"    → {rel.get('reason')}")

    return "\n".join(lines)


def format_warnings(warnings: list) -> str:
    """Format sparse table warnings."""
    if not warnings:
        return "No warnings"

    lines = ["⚠️  Sparse Tables (use LEFT JOIN):"]
    for warning in warnings:
        lines.append(f"  - {warning}")

    return "\n".join(lines)


def get_generation_prompt(retrieval_result: dict):
    """
    Generate SQL prompt using ONLY the tables identified by Node 1 (Retrieval Agent).

    Args:
        retrieval_result: Dict from Node 1 with tables_needed, join_tables, sparse_warnings, etc.
    """

    tables_needed = retrieval_result.get("tables_needed", [])
    relationships = retrieval_result.get("join_tables", [])
    sparse_warnings = retrieval_result.get("sparse_warnings", [])
    need_groupby = retrieval_result.get("need_groupby", False)
    aggregations = retrieval_result.get("aggregations", [])

    # Build focused schema - only for retrieved tables
    focused_schema = get_schema_for_tables(tables_needed)
    join_guide = format_relationships(relationships)
    warnings_text = format_warnings(sparse_warnings)

    # Determine if we need aggregation examples
    aggregation_hint = ""
    if need_groupby:
        aggregation_hint = f"""
This query requires GROUP BY and aggregations:
{json.dumps(aggregations, indent=2)}
Use these aggregation functions in your query."""

    return f"""You are a PostgreSQL SQL query generator. Generate ONLY a SELECT query based on the tables provided.

=== TABLES AVAILABLE (identified by Retrieval Agent) ===
{focused_schema}

=== RELATIONSHIPS TO USE ===
{join_guide}

=== SPARSE TABLE WARNINGS ===
{warnings_text}

=== CRITICAL RULES ===
1. Use ONLY the tables listed above - NO other tables
2. Follow the JOIN relationships exactly as specified
3. Always use double quotes around ALL identifiers: "TableName", "columnName", aliases like "t1"
4. Use single quotes ONLY for string values: 'active', '2024-01-01'
5. Add LIMIT 100 unless user specifically asks for all results
6. Return ONLY the SQL query - no explanation, no markdown, no comments
7. Use proper aliases for tables (e.g., "u" for Users, "l" for Leads)

{aggregation_hint}

=== EXAMPLE FORMAT ===
SELECT "u"."name", "a"."date", "a"."status"
FROM "Users" "u"
LEFT JOIN "Attendances" "a" ON "u"."id" = "a"."userId"
WHERE "a"."status" = 'present'
LIMIT 100;

=== NOW GENERATE THE SQL ===
Generate the SQL query for the user's question. Return ONLY the SQL, nothing else."""


def get_simple_generation_prompt():
    """Fallback prompt when retrieval fails or no tables are retrieved."""
    return """You are a PostgreSQL SQL query generator for a CRM system.

CRITICAL RULES:
1. Return ONLY raw SQL, no explanation or markdown
2. Use double quotes for all identifiers: "TableName", "columnName"
3. Use single quotes for string values: 'active', '2024-01-01'
4. Always add LIMIT 100
5. Only SELECT statements - never INSERT, UPDATE, DELETE, DROP, ALTER, CREATE

Generate the SQL query now:"""
