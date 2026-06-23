from langchain_groq import ChatGroq
from backend.prompts.prompts import get_generation_prompt

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

def generation_agent(state: dict) -> dict:
    messages = [
        {"role": "system", "content": get_generation_prompt()},
        *state["history"],
        {"role": "user", "content": state["question"]}
    ]
    response = llm.invoke(messages)
    state["sql"] = response.content.strip()
    return state