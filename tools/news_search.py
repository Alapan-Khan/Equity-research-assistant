import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_news(query: str, max_results: int = 3) -> str:
    """
    Search for recent news relevant to a query.
    Returns a formatted string of results (title + snippet + url) for the LLM to use.
    """
    results = tavily.search(query=query, max_results=max_results, search_depth="basic")

    formatted = []
    for r in results.get("results", []):
        formatted.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r.get('content', '')[:300]}\n"
        )

    if not formatted:
        return "No relevant news found."

    return "\n---\n".join(formatted)


if __name__ == "__main__":
    # quick standalone test
    result = search_news("Infosys Q1 FY27 results")
    print(result)