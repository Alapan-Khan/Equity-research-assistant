"""
Evaluation query set for the agentic RAG system.
Each entry has a query, the expected router classification, and a list of
keywords/facts that MUST appear in the final answer for it to be considered correct.
Ground truth for financials comes directly from data/financials.db (Step 2).
"""

EVAL_SET = [
    {
        "query": "What was Infosys's net profit in Q4 FY26?",
        "expected_route": "financials",
        "expected_keywords": ["8501", "8,501"],  # accept either format
    },
    {
        "query": "What was TCS's revenue in Q1 FY26?",
        "expected_route": "financials",
        "expected_keywords": ["63437", "63,437"],
    },
    {
        "query": "What was Infosys's EPS in Q3 FY26?",
        "expected_route": "financials",
        "expected_keywords": ["16.17"],
    },
    {
        "query": "What are Infosys's key risk factors mentioned in the annual report?",
        "expected_route": "docs",
        "expected_keywords": ["risk"],  # loose check - doc answers are narrative, not exact-match
    },
    {
        "query": "What does the annual report say about Infosys's approach to AI?",
        "expected_route": "docs",
        "expected_keywords": ["AI"],
    },
    {
        "query": "What's the latest news on TCS?",
        "expected_route": "news",
        "expected_keywords": ["TCS"],
    },
    {
        "query": "What's the latest news on Infosys?",
        "expected_route": "news",
        "expected_keywords": ["Infosys"],
    },
    {
        "query": "How does Infosys's Q4 FY26 net profit compare to what the annual report says?",
        "expected_route": "multi",
        "expected_keywords": ["8501", "8,501"],
    },
]