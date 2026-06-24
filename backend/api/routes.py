import logging
from fastapi import APIRouter
from pydantic import BaseModel
from backend.graph.pipeline import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter()

conversation_history = []

class QueryRequest(BaseModel):
    question: str
    include_retrieval_info: bool = False  # NEW: Optional detailed info

@router.post("/query")
def query(request: QueryRequest):
    """
    Process a natural language question and return SQL query with results.

    NEW: Uses 2-node architecture (Retrieval + Generation)
    - Node 1 (Retrieval): Identifies tables and relationships
    - Node 2 (Generation): Generates SQL using only retrieved tables

    Args:
        question: Natural language question
        include_retrieval_info: If True, returns table info from Node 1

    Returns:
        {
            "response": "Query results or error message",
            "sql": "Generated SQL query",
            "retrieval_info": {  # NEW: Only if include_retrieval_info=True
                "primary_table": "main table",
                "tables_used": ["list", "of", "tables"],
                "sparse_warnings": ["warnings"],
                "relationships": ["FK paths"]
            }
        }
    """
    global conversation_history

    logger.info(f"API Request: {request.question[:100]}...")

    # Run the 2-node pipeline
    result = run_pipeline(request.question, conversation_history)

    # Add to conversation history
    conversation_history.append({"role": "user", "content": request.question})
    conversation_history.append({"role": "assistant", "content": result.get("sql", "")})

    # Build response
    response = {
        "response": result.get("response", "No results found."),
        "sql": result.get("sql", ""),
    }

    # NEW: Include retrieval information if requested
    if request.include_retrieval_info:
        retrieval_result = result.get("retrieval_result", {})
        response["retrieval_info"] = {
            "primary_table": retrieval_result.get("primary_table"),
            "tables_used": result.get("retrieved_tables", []),
            "sparse_warnings": result.get("sparse_warnings", []),
            "relationships": [
                f"{r.get('join_type')} {r.get('table')} ON {r.get('on')}"
                for r in result.get("relationships", [])
            ]
        }
        logger.info(f"✓ Query processed with Node 1+2 pipeline")
        logger.info(f"  Tables: {response['retrieval_info']['tables_used']}")
        logger.info(f"  Warnings: {response['retrieval_info']['sparse_warnings']}")

    return response

@router.delete("/history")
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    logger.info("Conversation history cleared")
    return {"message": "Conversation history cleared."}