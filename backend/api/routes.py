from fastapi import APIRouter
from pydantic import BaseModel
from backend.graph.pipeline import run_pipeline

router = APIRouter()

conversation_history = []

class QueryRequest(BaseModel):
    question: str

@router.post("/query")
def query(request: QueryRequest):
    global conversation_history
    result = run_pipeline(request.question, conversation_history)
    
    conversation_history.append({"role": "user", "content": request.question})
    conversation_history.append({"role": "assistant", "content": result["sql"]})

    if result["response"] == "No results found.":
        return {"response": "No results found.", "sql": result["sql"]}

    return {
        "response": result["response"],
        "sql": result["sql"]
    }

@router.delete("/history")
def clear_history():
    global conversation_history
    conversation_history = []
    return {"message": "Conversation history cleared."}