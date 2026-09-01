import os
from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from graph.state import GraphState
from tools.financials_query import query_financials
from tools.news_search import search_news

load_dotenv()

# Set up the doc index once at module load (reused across calls)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("annual_reports")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
doc_index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
retriever = doc_index.as_retriever(similarity_top_k=5)


def retrieve_docs(state: GraphState) -> GraphState:
    """Pull relevant chunks from the annual report index."""
    nodes = retriever.retrieve(state["query"])
    context = "\n---\n".join([n.text for n in nodes])
    sources = list(set([n.metadata.get("source", "unknown") for n in nodes]))

    print(f"[retrieve_docs] retrieved {len(nodes)} chunks")

    state["retrieved_context"] = context
    state["sources"] = sources
    return state


def retrieve_financials(state: GraphState) -> GraphState:
    """Pull data from the SQLite financials tool.
    Naive company detection for now - looks for 'Infosys' or 'TCS' in the query."""
    query = state["query"]
    company = "Infosys" if "infosys" in query.lower() else "TCS" if "tcs" in query.lower() else None

    if company:
        result = query_financials(company)
    else:
        result = query_financials("Infosys") + "\n\n" + query_financials("TCS")

    print(f"[retrieve_financials] pulled data for: {company or 'both companies'}")

    state["retrieved_context"] = result
    state["sources"] = ["financials.db"]
    return state


def retrieve_news(state: GraphState) -> GraphState:
    """Pull live news results via Tavily."""
    result = search_news(state["query"])

    print(f"[retrieve_news] search complete")

    state["retrieved_context"] = result
    state["sources"] = ["tavily_news_search"]
    return state


def retrieve_multi(state: GraphState) -> GraphState:
    """Pull from all three sources and combine, for cross-referencing queries.
    Each source gets its own truncation budget so one source (usually docs,
    which tends to be the largest) can't crowd out the others before the
    LLM ever sees them."""
    state = retrieve_docs(state)
    docs_context = state["retrieved_context"][:1500]
    docs_sources = state["sources"]

    state = retrieve_financials(state)
    fin_context = state["retrieved_context"][:1000]
    fin_sources = state["sources"]

    state = retrieve_news(state)
    news_context = state["retrieved_context"][:1000]
    news_sources = state["sources"]

    combined = (
        f"--- Annual Report Context ---\n{docs_context}\n\n"
        f"--- Financials ---\n{fin_context}\n\n"
        f"--- Recent News ---\n{news_context}"
    )

    state["retrieved_context"] = combined
    state["sources"] = list(set(docs_sources + fin_sources + news_sources))
    return state