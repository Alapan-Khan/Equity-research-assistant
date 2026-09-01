from graph.flow import build_graph
from graph.state import GraphState

app = build_graph()

test_queries = [
    ("docs", "What are Infosys's key risk factors according to the annual report?"),
    ("news", "What's the latest news on TCS?"),
    ("multi", "How does Infosys's Q4 FY26 net profit compare to what the annual report said about margin pressures?"),
]

for expected_route, query in test_queries:
    print("\n" + "=" * 70)
    print(f"QUERY: {query}")
    print(f"(expecting route: {expected_route})")
    print("=" * 70)

    initial_state: GraphState = {
        "query": query, "route": "", "retrieved_context": "",
        "is_relevant": False, "retry_count": 0,
        "final_answer": "", "sources": []
    }

    result = app.invoke(initial_state)

    print(f"\nFINAL ANSWER:\n{result['final_answer']}")
    print(f"\nSources used: {result['sources']}")