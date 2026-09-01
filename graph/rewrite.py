import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from graph.state import GraphState

load_dotenv()

llm = Groq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

REWRITE_PROMPT = """The following query did not retrieve useful results:
"{query}"

Rewrite it to be more specific and likely to retrieve relevant information from an
Infosys/TCS annual report or financial database. Respond with ONLY the rewritten query, nothing else.
"""


def rewrite_query(state: GraphState) -> GraphState:
    prompt = REWRITE_PROMPT.format(query=state["query"])
    response = llm.complete(prompt)
    new_query = response.text.strip()

    print(f"[rewrite_query] '{state['query']}' -> '{new_query}'")

    state["query"] = new_query
    state["retry_count"] += 1
    return state