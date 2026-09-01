import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from graph.state import GraphState

load_dotenv()

llm = Groq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

ROUTER_PROMPT = """You are a routing assistant for an equity research system covering Infosys and TCS.

Classify the user's query into exactly ONE of these categories:
- "docs": questions about company strategy, business segments, risk factors, governance, or anything found in the annual report narrative
- "financials": questions about specific quarterly numbers - revenue, net profit, EPS, for a specific quarter
- "news": questions about recent/current events, latest news, or anything time-sensitive that wouldn't be in the annual report
- "multi": questions that clearly need more than one source (e.g. "how does the latest quarter compare to what was said in the annual report")

Respond with ONLY the single word: docs, financials, news, or multi

Query: {query}
"""


def route_query(state: GraphState) -> GraphState:
    query = state["query"]
    prompt = ROUTER_PROMPT.format(query=query)

    response = llm.complete(prompt)
    route = response.text.strip().lower()

    # safety fallback in case the LLM doesn't return exactly what we expect
    if route not in ("docs", "financials", "news", "multi"):
        route = "docs"

    print(f"[router] query classified as: {route}")

    state["route"] = route
    return state


if __name__ == "__main__":
    # quick standalone test - try a few different query types
    test_queries = [
        "What was TCS's net profit in Q4 FY26?",
        "What are Infosys's key risk factors?",
        "What's the latest news on Infosys?",
        "How does Infosys's Q4 performance compare to their FY26 outlook in the annual report?",
    ]
    for q in test_queries:
        state: GraphState = {
            "query": q, "route": "", "retrieved_context": "",
            "is_relevant": False, "retry_count": 0,
            "final_answer": "", "sources": []
        }
        result = route_query(state)
        print(f"Query: {q}\n  -> Route: {result['route']}\n")