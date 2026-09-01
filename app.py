import streamlit as st
from graph.flow import build_graph
from graph.state import GraphState

st.set_page_config(page_title="Equity Research Assistant", page_icon="📊", layout="wide")

# ---------- ChatGPT-style theming ----------
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    html, body, [class*="css"] {
        font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }

    .stApp {
        background-color: #0f0f10;
    }

    /* The fixed bottom input container has its own background layer by
       default - force it to match the app background so there's no visible seam */
    div[data-testid="stBottom"],
    div[data-testid="stBottomBlockContainer"],
    .stChatInputContainer {
        background-color: #0f0f10 !important;
    }

    .main .block-container {
        max-width: 768px;
        padding-top: 2.5rem;
        padding-bottom: 8rem;
    }

    /* Header */
    .app-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    .app-header h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ececec;
        margin-bottom: 0.3rem;
    }
    .app-subtitle {
        color: #8e8ea0;
        font-size: 0.88rem;
    }

    /* Message rows */
    .msg-row {
        display: flex;
        margin-bottom: 1.6rem;
        gap: 0.75rem;
    }
    .msg-row.user {
        justify-content: flex-end;
    }
    .msg-row.assistant {
        justify-content: flex-start;
    }

    /* User bubble - right aligned pill, like ChatGPT */
    .user-bubble {
        background-color: #2a2b32;
        color: #ececec;
        padding: 0.65rem 1.1rem;
        border-radius: 20px;
        max-width: 75%;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Assistant - plain full-width text, no bubble, like ChatGPT */
    .assistant-content {
        color: #d1d5db;
        font-size: 0.95rem;
        line-height: 1.65;
        max-width: 100%;
    }
    .assistant-avatar {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        background: linear-gradient(135deg, #10a37f, #1a7f64);
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
    }

    /* Badges */
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin-top: 0.7rem;
    }
    .badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .badge-route {
        background: rgba(16, 163, 127, 0.15);
        color: #4dd4ac;
    }
    .badge-source {
        background: rgba(255,255,255,0.05);
        color: #9a9ba1;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #171717;
    }
    section[data-testid="stSidebar"] button {
        text-align: left;
        border-radius: 10px;
        background-color: #2a2a2a;
        border: 1px solid rgba(255,255,255,0.08);
        color: #d1d5db;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #333333;
        border-color: rgba(255,255,255,0.15);
    }

    /* Chat input - rounded pill, ChatGPT style */
    .stChatInput textarea, .stChatInput input {
        border-radius: 24px !important;
    }
    div[data-testid="stChatInput"] {
        max-width: 768px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_graph():
    return build_graph()

app = get_graph()

# ---------- Header ----------
st.markdown("""
<div class="app-header">
    <h1>📊 Equity Research Assistant</h1>
    <div class="app-subtitle">Agentic RAG over Infosys and TCS — reports, live news, and financials, with cited answers</div>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### How it works")
    st.markdown("""
Each question is routed automatically:

- **Annual reports** — strategy, risk, governance
- **Financials database** — exact quarterly numbers
- **Live news** — recent developments
- **Multi-source** — cross-referencing questions
    """)
    st.divider()
    st.markdown("### Try asking")
    example_queries = [
        "What was Infosys's net profit in Q4 FY26?",
        "What are Infosys's key risk factors?",
        "What's the latest news on TCS?",
        "How does Infosys's Q4 FY26 profit compare to what the annual report says?",
    ]
    for eq in example_queries:
        if st.button(eq, use_container_width=True):
            st.session_state.pending_query = eq

# ---------- Chat state ----------
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_user(content: str):
    st.markdown(f"""
    <div class="msg-row user">
        <div class="user-bubble">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_assistant(content: str, route: str = None, sources: list = None):
    badges = ""
    if route:
        badges = f'<span class="badge badge-route">route · {route}</span>'
        for s in (sources or []):
            badges += f'<span class="badge badge-source">{s}</span>'
        badges = f'<div class="badge-row">{badges}</div>'

    st.markdown(f"""
    <div class="msg-row assistant">
        <div class="assistant-avatar">📊</div>
        <div class="assistant-content">{content}{badges}</div>
    </div>
    """, unsafe_allow_html=True)


for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user(msg["content"])
    else:
        render_assistant(msg["content"], msg.get("route"), msg.get("sources"))

# ---------- Input handling ----------
query = st.chat_input("Message Equity Research Assistant...")
if "pending_query" in st.session_state:
    query = st.session_state.pending_query
    del st.session_state.pending_query

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    render_user(query)

    with st.spinner("Thinking..."):
        initial_state: GraphState = {
            "query": query, "route": "", "retrieved_context": "",
            "is_relevant": False, "retry_count": 0,
            "final_answer": "", "sources": []
        }
        result = app.invoke(initial_state)

    render_assistant(result["final_answer"], result["route"], result["sources"])

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["final_answer"],
        "route": result["route"],
        "sources": result["sources"],
    })