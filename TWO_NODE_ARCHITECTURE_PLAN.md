# CRM Query Generation: 2-Node Architecture Plan

**Architecture Upgrade**: Single Generation Node → **Retrieval Node + Generation Node**  
**Database**: PostgreSQL (25 tables, ~30,000+ records)  
**Current Pipeline**: 4 nodes → **Proposed: 5 nodes**

---

## PROBLEM WITH CURRENT APPROACH

Current: `question → generation (guess all tables) → validation → execution → formatting`

**Issues**:
- LLM must hold all 25 tables in context
- Hallucination: generates columns from non-existent tables
- No awareness of relationships (when to use LEFT vs INNER JOIN)
- Sparse tables treated same as dense tables
- Empty Payrolls table still gets queried

---

## NEW ARCHITECTURE

```
question
   ↓
Node 1: RETRIEVAL (NEW)
   ├─ Understands question intent
   ├─ Picks relevant tables
   ├─ Maps relationships
   ├─ Warns about sparse data
   └─ Returns: [tables needed, FK paths, JOIN types, warnings]
   ↓
Node 2: GENERATION (UPDATED)
   ├─ Receives ONLY retrieved table schema
   ├─ Generates SQL with correct JOINs
   ├─ No hallucination (schema is limited)
   └─ Returns: SQL query
   ↓
Node 3: VALIDATION (existing)
Node 4: EXECUTION (existing)
Node 5: FORMATTING (existing)
```

---

## 1. NODE 1: RETRIEVAL AGENT

### What It Does
Analyzes natural language to determine:
1. **Which tables are primary?** (Leads? Users? Chats?)
2. **Which tables must join?** (What relationships exist?)
3. **What JOIN type?** (INNER for required, LEFT for optional)
4. **Sparse table warnings?** (94.8% NULL in LeadDocuments)
5. **Exclude which tables?** (Payrolls is empty!)

### Input
```
Question: "Get the attendance record for each user showing present and absent days"
```

### Output
```json
{
  "primary_table": "Users",
  "join_tables": [
    {
      "table": "Attendances",
      "on": "Users.id = Attendances.userId",
      "join_type": "LEFT JOIN",
      "reason": "Some users may have no attendance records"
    }
  ],
  "sparse_warnings": [],
  "exclude_tables": [],
  "tables_needed": ["Users", "Attendances"],
  "need_groupby": true,
  "aggregations": ["COUNT(present)", "COUNT(absent)"]
}
```

### Implementation

**File: `backend/prompts/retrieval_prompt.py`**
```python
def get_retrieval_prompt():
    return """You are a database schema expert. Analyze the user question and identify:

1. PRIMARY TABLE: Main table for this query
2. JOIN TABLES: Related tables needed with FK paths
3. JOIN TYPES: Use LEFT for optional relationships
4. SPARSE WARNINGS: Alert for sparse tables (>30% NULL)
5. EXCLUDED TABLES: Tables to skip (e.g., Payrolls - empty!)

SCHEMA RELATIONSHIPS:

Leads (641 records)
├─ LeadDetails (227) - 35.4% coverage [SPARSE - use LEFT JOIN]
├─ LeadCoApplicants (235) - 36.7% coverage [SPARSE - use LEFT JOIN]
├─ LeadDocuments (33) - 5.1% coverage [CRITICAL SPARSE - 94.8% NULL - use LEFT JOIN]
├─ LeadStageTransitions (2070) - 3.2 avg per lead [DENSE - can use INNER]
├─ LeadLoanProcesses (226) - 35.2% coverage [SPARSE - use LEFT JOIN]
├─ leadLogs (13383) - audit trail [INNER with filters]
├─ Payouts (97) - 15% coverage [SPARSE - use LEFT JOIN]
└─ LeadShareLinks (15) - rare [SPARSE - use LEFT JOIN]

Users (102 records)
├─ Attendances (3789) - 37 avg per user [DENSE - can use INNER or LEFT]
├─ Payslips (107) - incomplete [SPARSE - use LEFT JOIN]
├─ Leaves (159) - sparse [SPARSE - use LEFT JOIN]
├─ LeaveBalances (41) - 40% coverage [SPARSE - use LEFT JOIN]
├─ Notifications (605) - 5.9 avg per user [MEDIUM - use LEFT JOIN]
├─ Payouts (97) - 15% coverage [SPARSE - use LEFT JOIN]
├─ UserSettings (57) - 56% coverage [SPARSE - use LEFT JOIN]
└─ Chats (28) - M:M relationship [SPECIAL handling]

Chats (28 records)
└─ ChatMessages (67) - 2.4 avg per chat [MEDIUM - can use INNER or LEFT]

SPARSE TABLE WARNINGS:
- LeadDocuments: 94.8% NULL → ALWAYS use LEFT JOIN
- LeadDetails: 35.4% coverage → Use LEFT JOIN unless explicitly filtering
- LeadCoApplicants: 36.7% coverage → Use LEFT JOIN
- Payslips: Incomplete, use LEFT JOIN
- Payrolls: EMPTY TABLE (0 records) → DO NOT USE AT ALL

EXCLUDED TABLES (Don't use):
- Payrolls: 0 records - completely empty
- LandingContents: Static content, not relevant
- lead_otps: Only for authentication, not data queries

OUTPUT FORMAT (JSON):
{
  "primary_table": "string",
  "join_tables": [
    {
      "table": "string",
      "on": "column = column",
      "join_type": "INNER JOIN|LEFT JOIN",
      "reason": "why this join"
    }
  ],
  "sparse_warnings": ["list of tables with >30% NULL"],
  "exclude_tables": ["tables to skip"],
  "tables_needed": ["list of final tables"],
  "need_groupby": boolean,
  "aggregations": ["list of needed aggregates if any"]
}

Generate only valid JSON, nothing else."""
```

**File: `backend/agents/retrieval.py`**
```python
from langchain_groq import ChatGroq
from backend.prompts.retrieval_prompt import get_retrieval_prompt
import json

llm = ChatGroq(model="openai/gpt-4o-mini", temperature=0)

def retrieval_agent(state: dict) -> dict:
    """Node 1: Retrieve relevant tables for the question"""
    messages = [
        {"role": "system", "content": get_retrieval_prompt()},
        {"role": "user", "content": state["question"]}
    ]
    
    response = llm.invoke(messages)
    
    try:
        retrieved_schema = json.loads(response.content)
    except json.JSONDecodeError:
        retrieved_schema = {
            "primary_table": None,
            "join_tables": [],
            "tables_needed": [],
            "error": "Could not parse schema"
        }
    
    state["retrieved_tables"] = retrieved_schema.get("tables_needed", [])
    state["relationships"] = retrieved_schema.get("join_tables", [])
    state["sparse_warnings"] = retrieved_schema.get("sparse_warnings", [])
    state["retrieval_result"] = retrieved_schema
    
    return state
```

---

## 2. NODE 2: UPDATED GENERATION AGENT

### What Changed
- **Before**: Gets full schema with all 25 tables
- **After**: Gets ONLY the tables from retrieval + their FK relationships

### Input
```python
state["retrieval_result"] = {
    "tables_needed": ["Users", "Attendances"],
    "join_tables": [{...}],
    "sparse_warnings": [],
    ...
}
```

### Updated Generation Prompt

**File: `backend/prompts/generation_prompt.py`**
```python
def get_generation_prompt(retrieval_result: dict):
    """Build prompt with ONLY retrieved tables"""
    
    tables = retrieval_result.get("tables_needed", [])
    relationships = retrieval_result.get("join_tables", [])
    warnings = retrieval_result.get("sparse_warnings", [])
    
    # Build focused schema - only for retrieved tables
    focused_schema = build_focused_schema(tables)
    
    # Build relationship details
    join_guide = build_join_guide(relationships)
    
    return f"""You are a SQL query generator. Generate ONLY a SELECT query.

AVAILABLE TABLES (from retrieval node):
{focused_schema}

RELATIONSHIPS TO USE:
{join_guide}

SPARSE TABLE WARNINGS:
{format_warnings(warnings)}

CRITICAL RULES:
1. Use ONLY these tables (no others)
2. Follow the JOIN relationships exactly as specified
3. Use LEFT JOIN for sparse tables (from warnings above)
4. Always use double quotes around ALL identifiers
5. Use single quotes for string values
6. Add LIMIT 100 unless user asks for all results
7. No comments or explanations, only SQL

Example (if similar to this question):
[Show relevant example based on tables involved]

Generate the SQL query now:
"""

def build_focused_schema(tables: list) -> str:
    """Return only schema for needed tables"""
    # Fetch schema from DB for only these tables
    schema_map = {
        "Users": "id, name, email, phone, role, ...",
        "Attendances": "id, userId, date, status, ...",
        # etc
    }
    return "\n".join(f"Table: {t}\n  {schema_map.get(t, '')}" for t in tables)

def build_join_guide(relationships: list) -> str:
    """Show JOIN syntax for this query"""
    return "\n".join([
        f"{r['join_type']} {r['table']} ON {r['on']} -- {r['reason']}"
        for r in relationships
    ])
```

**File: `backend/agents/generation.py` (Updated)**
```python
from langchain_groq import ChatGroq
from backend.prompts.generation_prompt import get_generation_prompt

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

def generation_agent(state: dict) -> dict:
    """Node 2: Generate SQL from retrieved tables only"""
    
    # Get retrieval result from Node 1
    retrieval_result = state.get("retrieval_result", {})
    
    # Build prompt with only retrieved tables
    system_prompt = get_generation_prompt(retrieval_result)
    
    messages = [
        {"role": "system", "content": system_prompt},
        *state["history"],
        {"role": "user", "content": state["question"]}
    ]
    
    response = llm.invoke(messages)
    state["sql"] = response.content.strip()
    
    return state
```

---

## 3. UPDATED PIPELINE

**File: `backend/graph/pipeline.py`**
```python
from langgraph.graph import StateGraph, END
from backend.agents.retrieval import retrieval_agent
from backend.agents.generation import generation_agent
from backend.agents.validation import validation_agent
from backend.agents.execution import execution_agent
from backend.agents.formatting import formatting_agent

def create_pipeline():
    graph = StateGraph(dict)

    # Add all nodes
    graph.add_node("retrieval", retrieval_agent)      # NEW
    graph.add_node("generation", generation_agent)
    graph.add_node("validation", validation_agent)
    graph.add_node("execution", execution_agent)
    graph.add_node("formatting", formatting_agent)

    # Set entry point to retrieval
    graph.set_entry_point("retrieval")
    
    # Chain: retrieval → generation → validation
    graph.add_edge("retrieval", "generation")
    graph.add_edge("generation", "validation")

    # Conditional: if invalid, retry retrieval (better than generation)
    graph.add_conditional_edges(
        "validation",
        lambda state: (
            "execution" if state["valid"]
            else "retrieval" if state["retry_count"] < 2  # CHANGED: retry retrieval
            else END
        )
    )

    # Chain: validation → execution → formatting
    graph.add_edge("execution", "formatting")
    graph.add_edge("formatting", END)

    return graph.compile()

def run_pipeline(question: str, history: list) -> dict:
    state = {
        "question": question,
        "history": history,
        "retrieved_tables": [],
        "relationships": [],
        "sparse_warnings": [],
        "retrieval_result": {},    # NEW
        "sql": None,
        "valid": False,
        "error": None,
        "result": None,
        "response": None,
        "retry_count": 0
    }
    return pipeline.invoke(state)
```

---

## 4. IMPLEMENTATION CHECKLIST

### Step 1: Create Retrieval Node
- [ ] Create `backend/prompts/retrieval_prompt.py`
- [ ] Create `backend/agents/retrieval.py`
- [ ] Test retrieval on 5-10 sample questions
- [ ] Verify it picks correct tables

### Step 2: Update Generation Node
- [ ] Create `backend/prompts/generation_prompt.py`
- [ ] Update `backend/agents/generation.py`
- [ ] Remove all table-guessing logic
- [ ] Test with retrieved tables only

### Step 3: Update Pipeline
- [ ] Modify `backend/graph/pipeline.py`
- [ ] Update state initialization
- [ ] Change entry point to "retrieval"
- [ ] Update conditional flow (retry retrieval on failure)

### Step 4: Test End-to-End
- [ ] Test all Level 2 SAMPLE_QUESTIONS.md
- [ ] Test all Level 3 SAMPLE_QUESTIONS.md
- [ ] Verify sparse joins use LEFT JOIN
- [ ] Verify Payrolls never queried
- [ ] Measure accuracy improvement

### Step 5: Logging & Monitoring
- [ ] Add logging: what tables retrieved?
- [ ] Add logging: what relationships used?
- [ ] Add metrics: retrieval accuracy
- [ ] Add metrics: generation accuracy

---

## 5. EXPECTED IMPROVEMENTS

| Issue | Current | Fixed By |
|-------|---------|----------|
| Hallucinated columns | Common | Node 2 only uses retrieved tables |
| Wrong JOIN types | Common | Node 1 specifies LEFT vs INNER |
| Sparse table errors | 30% | Node 1 warns about sparse data |
| Empty table queries | Yes | Node 1 excludes Payrolls |
| Missing relationships | Common | Node 1 maps all FKs |
| Over-complex queries | Some | Node 1 picks only needed tables |

---

## 6. QUICK EXAMPLE FLOW

**Question**: "Get the attendance record for each user showing present and absent days"

### Node 1 (Retrieval) Output:
```json
{
  "primary_table": "Users",
  "join_tables": [
    {
      "table": "Attendances",
      "on": "Users.id = Attendances.userId",
      "join_type": "LEFT JOIN",
      "reason": "Some users may have no attendance records"
    }
  ],
  "sparse_warnings": [],
  "exclude_tables": [],
  "tables_needed": ["Users", "Attendances"],
  "need_groupby": true,
  "aggregations": ["COUNT(CASE WHEN status='present')", "COUNT(CASE WHEN status='absent')"]
}
```

### Node 2 (Generation) Input:
```
System prompt includes ONLY: Users and Attendances schema
WITH relationships: "LEFT JOIN Attendances ON Users.id = Attendances.userId"
```

### Node 2 (Generation) Output:
```sql
SELECT "u"."name",
  COUNT(CASE WHEN "a"."status" = 'present' THEN 1 END) as "present_days",
  COUNT(CASE WHEN "a"."status" = 'absent' THEN 1 END) as "absent_days"
FROM "Users" "u"
LEFT JOIN "Attendances" "a" ON "u"."id" = "a"."userId"
GROUP BY "u"."id", "u"."name"
ORDER BY "u"."id"
LIMIT 100;
```

---

## 7. SUCCESS METRICS

**Track before & after**:
1. ✅ % of queries with correct table selection
2. ✅ % of queries with correct JOIN types
3. ✅ % of queries with proper GROUP BY
4. ✅ % of queries that execute without error
5. ✅ % of queries returning expected results

**Target**:
- Retrieval accuracy: **95%+**
- Generation accuracy: **90%+**
- Overall accuracy: **85%+** (Level 2-3 questions)
