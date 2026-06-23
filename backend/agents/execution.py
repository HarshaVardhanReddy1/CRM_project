from backend.db.connection import run_query

def execution_agent(state: dict) -> dict:
    try:
        result = run_query(state["sql"])
        state["result"] = result
        state["error"] = None
    except Exception as e:
        state["result"] = None
        state["error"] = str(e)
    return state