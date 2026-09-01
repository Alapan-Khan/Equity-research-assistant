import os
import fitz  # pymupdf
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

load_dotenv()

# 1. Load the embedding model (runs locally, no API cost)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")


def load_pdf_clean(path):
    """Extract clean readable text from a PDF using PyMuPDF, page by page."""
    doc = fitz.open(path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
    doc.close()
    return full_text


# 2. Load PDFs from data/docs/ using clean text extraction
print("Loading documents...")
docs_paths = {
    "infosys_annual_report.pdf": "data/docs/infosys_annual_report.pdf",
    "tcs_annual_report.pdf": "data/docs/tcs_annual_report.pdf",
}

documents = []
for name, path in docs_paths.items():
    text = load_pdf_clean(path)
    documents.append(Document(text=text, metadata={"source": name}))
    print(f"{name}: extracted {len(text)} characters")

print(f"Loaded {len(documents)} document(s)")

# 3. Split into chunks
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

# 4. Set up ChromaDB as the vector store (persists to disk)
#    Delete any old/dirty collection first so we start clean
chroma_client = chromadb.PersistentClient(path="./chroma_db")
try:
    chroma_client.delete_collection("annual_reports")
    print("Deleted old collection to rebuild clean.")
except Exception:
    pass  # collection didn't exist yet, that's fine

chroma_collection = chroma_client.get_or_create_collection("annual_reports")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 5. Build the index (this embeds every chunk - takes a few minutes for 2 full annual reports)
print("Building index... this will take a few minutes")
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model,
    transformations=[splitter],
    show_progress=True,
)

print(f"Index built and persisted to ./chroma_db")
print(f"Total chunks in collection: {chroma_collection.count()}")

# 6. Quick sanity check - use Groq as the LLM, not the OpenAI default
llm = Groq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))
query_engine = index.as_query_engine(embed_model=embed_model, llm=llm, similarity_top_k=10)
response = query_engine.query("What was Infosys's operating margin guidance range for FY26?")

print("\n--- ANSWER ---")
print(response)

print("\n--- RETRIEVED CHUNKS ---")
for i, node in enumerate(response.source_nodes):
    print(f"\n[{i}] score={node.score:.3f} source={node.metadata.get('source')}")
    print(node.text[:200])