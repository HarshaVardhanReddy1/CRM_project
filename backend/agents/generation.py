import logging
from langchain_groq import ChatGroq
from backend.prompts.generation_prompt import get_generation_prompt, get_simple_generation_prompt

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)


def generation_agent(state: dict) -> dict:
    """
    Node 2: Generation Agent

    Generates SQL using ONLY the tables identified by Node 1 (Retrieval Agent).
    The prompt is focused and contextual - no hallucination of non-existent tables.

    Input:
      - state["question"]: User's natural language question
      - state["retrieval_result"]: Output from Node 1 with tables_needed, relationships, etc.
      - state["history"]: Conversation history

    Output:
      - state["sql"]: Generated SQL query
    """

    try:
        question = state.get("question", "")
        retrieval_result = state.get("retrieval_result", {})
        history = state.get("history", [])

        logger.info(f"Generation Agent: Processing question: {question[:100]}...")
        logger.info(f"  Using tables: {retrieval_result.get('tables_needed', [])}")

        # Check if retrieval was successful
        if not retrieval_result or "error" in retrieval_result:
            logger.warning("No valid retrieval result, using simple prompt")
            system_prompt = get_simple_generation_prompt()
        else:
            # Use focused prompt with only retrieved tables
            system_prompt = get_generation_prompt(retrieval_result)

        # Build messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            *history,
            {
                "role": "user",
                "content": question
            }
        ]

        logger.debug(f"System prompt length: {len(system_prompt)} characters")
        logger.debug(f"History items: {len(history)}")

        # Generate SQL
        response = llm.invoke(messages)
        sql = response.content.strip()

        logger.info(f"✓ SQL generated successfully ({len(sql)} characters)")
        logger.debug(f"Generated SQL preview: {sql[:100]}...")

        state["sql"] = sql

        return state

    except Exception as e:
        logger.error(f"Generation Agent Error: {str(e)}", exc_info=True)
        state["sql"] = ""
        state["error"] = str(e)
        return state