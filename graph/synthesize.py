import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from graph.state import GraphState

load_dotenv()

llm = Groq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

SYNTHESIZE_PROMPT = """Answer the user's question using ONLY the context provided below.
If the context doesn't fully answer the question, say what's missing rather than guessing.
Cite which source (annual report, financials database, or news) each part of your answer comes from.

Question: {query}

Context:
{context}

Answer:
"""


def synthesize_answer(state: GraphState) -> GraphState:
    # 5000 chars instead of 4000 - retrieve_multi now pre-truncates each
    # source individually (docs/financials/news), so this is a final safety
    # cap rather than the thing doing the truncating.
    prompt = SYNTHESIZE_PROMPT.format(
        query=state["query"],
        context=state["retrieved_context"][:5000]
    )
    response = llm.complete(prompt)

    print(f"[synthesize_answer] answer generated")

    state["final_answer"] = response.text.strip()
    return state