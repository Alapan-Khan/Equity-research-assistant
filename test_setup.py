import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tavily import TavilyClient

load_dotenv()

# Test Groq
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))
response = llm.invoke("Say 'Groq is working' in exactly those words.")
print("Groq test:", response.content)

# Test Tavily
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
results = tavily.search(query="Infosys stock news", max_results=2)
print("Tavily test:", [r["title"] for r in results["results"]])