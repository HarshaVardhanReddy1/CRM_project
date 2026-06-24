import json
import logging
from langchain_groq import ChatGroq
from backend.prompts.retrieval_prompt import get_retrieval_prompt
import os
from dotenv import load_dotenv

load_dotenv()



logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)


def retrieval_agent(state: dict) -> dict:
    """
    Node 1: Retrieval Agent

    Analyzes the user question and determines:
    - Which tables are primary
    - Which tables need to join
    - What type of joins (LEFT vs INNER)
    - Sparse table warnings
    - Tables to exclude

    Input: state["question"]
    Output: state with retrieval_result, retrieved_tables, relationships, sparse_warnings
    """

    try:
        question = state.get("question", "")
        logger.info(f"Retrieval Agent: Processing question: {question[:100]}...")

        # Build messages for LLM
        messages = [
            {
                "role": "system",
                "content": get_retrieval_prompt()
            },
            {
                "role": "user",
                "content": question
            }
        ]

        # Call LLM to get retrieval decision
        response = llm.invoke(messages)
        response_text = response.content.strip()

        logger.debug(f"Raw LLM Response: {response_text[:200]}...")

        # Parse JSON response
        try:
            retrieved_schema = json.loads(response_text)
            logger.info(f"✓ Retrieval parsed successfully")
            logger.info(f"  Primary table: {retrieved_schema.get('primary_table')}")
            logger.info(f"  Tables needed: {retrieved_schema.get('tables_needed')}")
            logger.info(f"  Sparse warnings: {retrieved_schema.get('sparse_warnings')}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}")

            # Fallback: return empty schema
            retrieved_schema = {
                "primary_table": None,
                "join_tables": [],
                "tables_needed": [],
                "sparse_warnings": [],
                "exclude_tables": [],
                "need_groupby": False,
                "aggregations": [],
                "error": f"Could not parse schema: {str(e)}",
                "raw_response": response_text[:500]
            }

        # Extract information for next node
        state["retrieved_tables"] = retrieved_schema.get("tables_needed", [])
        state["relationships"] = retrieved_schema.get("join_tables", [])
        state["sparse_warnings"] = retrieved_schema.get("sparse_warnings", [])
        state["excluded_tables"] = retrieved_schema.get("exclude_tables", [])
        state["need_groupby"] = retrieved_schema.get("need_groupby", False)
        state["aggregations"] = retrieved_schema.get("aggregations", [])

        # Store full retrieval result for generation node
        state["retrieval_result"] = retrieved_schema

        logger.info(f"Retrieval Agent completed successfully")

        return state

    except Exception as e:
        logger.error(f"Retrieval Agent Error: {str(e)}", exc_info=True)

        # Return state with error information
        state["retrieval_result"] = {
            "error": str(e),
            "primary_table": None,
            "join_tables": [],
            "tables_needed": [],
            "sparse_warnings": [],
            "exclude_tables": []
        }

        return state
