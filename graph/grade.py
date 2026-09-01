import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from graph.state import GraphState

load_dotenv()

llm = Groq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

GRADE_PROMPT = """You are grading whether retrieved context is relevant enough to answer a user's question.

Question: {query}

Retrieved context:
{context}

Does this context contain information that could help answer the question?
Respond with ONLY one word: "yes" or "no"
"""


def grade_relevance(state: GraphState) -> GraphState:
    prompt = GRADE_PROMPT.format(query=state["query"], context=state["retrieved_context"][:3000])
    response = llm.complete(prompt)
    verdict = response.text.strip().lower()

    is_relevant = "yes" in verdict

    print(f"[grade_relevance] verdict: {'relevant' if is_relevant else 'NOT relevant'}")

    state["is_relevant"] = is_relevant
    return state