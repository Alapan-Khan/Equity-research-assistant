import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

load_dotenv()

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = Groq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("annual_reports")

# Sanity check 1: how many chunks actually got embedded?
print(f"Total chunks in collection: {chroma_collection.count()}")

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)

# Sanity check 2: retrieve more chunks (10 instead of default 2) and print what's retrieved
query_engine = index.as_query_engine(embed_model=embed_model, llm=llm, similarity_top_k=10)
response = query_engine.query("What was Infosys's operating margin guidance range for FY26?")

print("\n--- ANSWER ---")
print(response)

print("\n--- RETRIEVED CHUNKS ---")
for i, node in enumerate(response.source_nodes):
    print(f"\n[{i}] score={node.score:.3f}")
    print(node.text[:200])