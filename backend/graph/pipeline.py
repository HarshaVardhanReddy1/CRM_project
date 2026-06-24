from langgraph.graph import StateGraph, END
from backend.agents.retrieval import retrieval_agent
from backend.agents.generation import generation_agent
from backend.agents.validation import validation_agent
from backend.agents.execution import execution_agent
from backend.agents.formatting import formatting_agent

def create_pipeline():
    graph = StateGraph(dict)

    # Add nodes
    graph.add_node("retrieval", retrieval_agent)        # NEW: Node 1
    graph.add_node("generation", generation_agent)      # Node 2
    graph.add_node("validation", validation_agent)      # Node 3
    graph.add_node("execution", execution_agent)        # Node 4
    graph.add_node("formatting", formatting_agent)      # Node 5

    # Set entry point to retrieval (NEW)
    graph.set_entry_point("retrieval")

    # Chain: retrieval → generation → validation
    graph.add_edge("retrieval", "generation")
    graph.add_edge("generation", "validation")

    # Conditional: validation determines next step
    graph.add_conditional_edges("validation", lambda state: (
        "execution" if state["valid"]
        else "retrieval" if state["retry_count"] < 2  # CHANGED: retry retrieval instead of generation
        else END
    ))

    # Chain: execution → formatting
    graph.add_edge("execution", "formatting")
    graph.add_edge("formatting", END)

    return graph.compile()

pipeline = create_pipeline()

def run_pipeline(question: str, history: list) -> dict:
    state = {
        "question": question,
        "history": history,
        # NEW: Retrieval node outputs
        "retrieved_tables": [],
        "relationships": [],
        "sparse_warnings": [],
        "excluded_tables": [],
        "need_groupby": False,
        "aggregations": [],
        "retrieval_result": {},
        # Existing
        "sql": None,
        "valid": False,
        "error": None,
        "result": None,
        "response": None,
        "retry_count": 0
    }
    return pipeline.invoke(state)