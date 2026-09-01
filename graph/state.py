from typing import TypedDict, List


class GraphState(TypedDict):
    query: str                  # the user's original question
    route: str                  # "docs" | "financials" | "news" | "multi"
    retrieved_context: str      # text pulled from whichever source(s)
    is_relevant: bool           # set by the grading node
    retry_count: int            # how many times we've rewritten the query
    final_answer: str           # the synthesized answer
    sources: List[str]          # which sources contributed (for citations)