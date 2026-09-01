from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.router import route_query
from graph.retrieve import retrieve_docs, retrieve_financials, retrieve_news, retrieve_multi
from graph.grade import grade_relevance
from graph.rewrite import rewrite_query
from graph.synthesize import synthesize_answer


def route_decision(state: GraphState) -> str:
    """After router node: which retrieval node to go to."""
    return state["route"]  # "docs" | "financials" | "news" | "multi"


def relevance_decision(state: GraphState) -> str:
    """After grading: proceed to synthesis, or retry (max 1 retry)."""
    if state["is_relevant"] or state["retry_count"] >= 1:
        return "synthesize"
    return "rewrite"


def rewrite_route_decision(state: GraphState) -> str:
    """After rewriting: route back to the ORIGINAL route type, not always docs.
    This preserves multi-source retrieval on retry instead of silently
    downgrading a 'multi' query to docs-only."""
    return state["route"]


def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("router", route_query)
    workflow.add_node("retrieve_docs", retrieve_docs)
    workflow.add_node("retrieve_financials", retrieve_financials)
    workflow.add_node("retrieve_news", retrieve_news)
    workflow.add_node("retrieve_multi", retrieve_multi)
    workflow.add_node("grade", grade_relevance)
    workflow.add_node("rewrite", rewrite_query)
    workflow.add_node("synthesize", synthesize_answer)

    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "docs": "retrieve_docs",
            "financials": "retrieve_financials",
            "news": "retrieve_news",
            "multi": "retrieve_multi",
        }
    )

    # all retrieval paths go to grading
    workflow.add_edge("retrieve_docs", "grade")
    workflow.add_edge("retrieve_financials", "grade")
    workflow.add_edge("retrieve_news", "grade")
    workflow.add_edge("retrieve_multi", "grade")

    workflow.add_conditional_edges(
        "grade",
        relevance_decision,
        {
            "synthesize": "synthesize",
            "rewrite": "rewrite",
        }
    )

    # after rewriting, route back to the ORIGINAL source type (not always docs)
    workflow.add_conditional_edges(
        "rewrite",
        rewrite_route_decision,
        {
            "docs": "retrieve_docs",
            "financials": "retrieve_financials",
            "news": "retrieve_news",
            "multi": "retrieve_multi",
        }
    )

    workflow.add_edge("synthesize", END)

    return workflow.compile()


if __name__ == "__main__":
    app = build_graph()

    initial_state: GraphState = {
        "query": "What was Infosys's net profit in Q4 FY26?",
        "route": "", "retrieved_context": "", "is_relevant": False,
        "retry_count": 0, "final_answer": "", "sources": []
    }

    result = app.invoke(initial_state)

    print("\n" + "=" * 50)
    print("FINAL ANSWER:")
    print(result["final_answer"])
    print("\nSources used:", result["sources"])