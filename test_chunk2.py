from graph.state import GraphState
from graph.retrieve import retrieve_docs
from graph.grade import grade_relevance

state: GraphState = {
    "query": "What are Infosys's key risk factors?",
    "route": "docs", "retrieved_context": "", "is_relevant": False,
    "retry_count": 0, "final_answer": "", "sources": []
}

state = retrieve_docs(state)
print(f"\nRetrieved context preview:\n{state['retrieved_context'][:500]}\n")

state = grade_relevance(state)
print(f"\nIs relevant: {state['is_relevant']}")