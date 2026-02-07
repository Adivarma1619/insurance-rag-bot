"""
Insurance RAG Chatbot – self-contained Streamlit app.
Works locally (with backend/.env) and on Streamlit Community Cloud (with st.secrets).
"""
import os
import sys
import tempfile

import streamlit as st

# ── 1. Inject Streamlit secrets into os.environ BEFORE importing rag ──────
# Streamlit Cloud: keys live in st.secrets  |  Local: python-dotenv loads .env
try:
    for _k in ("GROQ_API_KEY", "OPENAI_API_KEY", "EMBED_MODEL", "CHAT_MODEL"):
        if _k in st.secrets and _k not in os.environ:
            os.environ[_k] = st.secrets[_k]
except Exception:
    pass  # No secrets file – local .env will be used below

# ── 2. Make backend/rag importable ─────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE, "backend"))

# Load backend/.env explicitly so that rag modules pick up the keys at import time
from dotenv import load_dotenv                                   # noqa: E402
load_dotenv(os.path.join(_BASE, "backend", ".env"))

from rag.pdf_to_text import extract_text, SUPPORTED_EXTENSIONS  # noqa: E402
from rag.chunking import chunk_text                              # noqa: E402
from rag.embed_store import build_and_save_index, load_index     # noqa: E402
from rag.rag_answer import retrieve, generate_answer             # noqa: E402

# ── 3. Directories ─────────────────────────────────────────────────────────
# Writable cache – survives reruns within one Streamlit session
_CACHE   = os.path.join(tempfile.gettempdir(), "st_rag_cache")
_UPLOADS = os.path.join(_CACHE, "uploads")
INDEX_PATH  = os.path.join(_CACHE, "index.faiss")
CHUNKS_PATH = os.path.join(_CACHE, "chunks.json")
os.makedirs(_UPLOADS, exist_ok=True)

# Sample knowledge base shipped with the repo (used when no file is uploaded)
SAMPLE_PDF = os.path.join(_BASE, "backend", "data", "knowledge.pdf")


# ──────────────────────────────────────────────────────────────────────────
# Page config & CSS
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Insurance Agency Chatbot",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1a1a1a;
        padding: 20px 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .user-message {
        background-color: #1a1a1a;
        color: white;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #f0f0f0;
        color: #1a1a1a;
        margin-right: 20%;
    }
    .stButton>button {
        width: 100%;
        background-color: #1a1a1a;
        color: white;
        border-radius: 8px;
        padding: 10px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #333;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me anything about your insurance policy or claims."}
    ]

if "index_loaded" not in st.session_state:
    st.session_state.index_loaded = False


# ──────────────────────────────────────────────────────────────────────────
# Helper functions (direct calls – no HTTP)
# ──────────────────────────────────────────────────────────────────────────
def get_file_list() -> list[str]:
    """List every supported file in the uploads cache."""
    try:
        return sorted(
            f for f in os.listdir(_UPLOADS)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        )
    except Exception:
        return []


def save_uploaded_file(uploaded_file) -> tuple[bool, str]:
    """Persist an uploaded Streamlit file to the cache dir."""
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported format '{ext}'. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    dest = os.path.join(_UPLOADS, uploaded_file.name)
    with open(dest, "wb") as fh:
        fh.write(uploaded_file.getvalue())
    return True, f"Uploaded '{uploaded_file.name}'. Select it and click Build Knowledge Base."


def build_index_from(file_path: str) -> tuple[bool, str]:
    """Run the full ingest pipeline on one file."""
    try:
        text   = extract_text(file_path)
        chunks = chunk_text(text, chunk_tokens=450, overlap_tokens=80)
        build_and_save_index(chunks, INDEX_PATH, CHUNKS_PATH)
        st.session_state.index_loaded = True
        return True, f"Successfully indexed {len(chunks)} chunks!"
    except Exception as e:
        return False, str(e)


def chat(user_input: str) -> tuple[bool, str]:
    """Retrieve relevant chunks and generate an answer."""
    try:
        index, chunks = load_index(INDEX_PATH, CHUNKS_PATH)
        relevant      = retrieve(user_input, index, chunks, k=4)
        answer        = generate_answer(user_input, relevant)
        return True, answer
    except Exception as e:
        return False, str(e)


# ──────────────────────────────────────────────────────────────────────────
# UI – Header
# ──────────────────────────────────────────────────────────────────────────
st.markdown("<h1 class='main-header'>🏥 Insurance Agency Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Get instant answers about your insurance policies, claims, and coverage</p>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# UI – Sidebar
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Upload ──
    st.header("📄 Upload Knowledge Base")
    st.caption("PDF · TXT · MD · DOCX · CSV · JSON · XLSX")

    uploaded_file = st.file_uploader(
        "Drag & drop or browse",
        type=['pdf', 'txt', 'md', 'docx', 'csv', 'json', 'xlsx'],
        help="Any supported format will be converted to text and indexed automatically"
    )

    if uploaded_file is not None:
        if st.button("⬆️ Upload", key="upload_btn"):
            ok, msg = save_uploaded_file(uploaded_file)
            if ok:
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(msg)

    st.divider()

    # ── Knowledge-base management ──
    st.header("🔧 Knowledge Base Management")

    available_files = get_file_list()

    if available_files:
        st.write(f"**Available files:** {len(available_files)}")

        selected_file = st.selectbox(
            "Select file to build knowledge base",
            options=available_files,
            help="The selected file will be chunked and indexed for Q&A"
        )

        if selected_file:
            st.info(f"📑 Selected: **{selected_file}**")

        if st.button("🔨 Build Knowledge Base", key="build_from_selected"):
            if selected_file:
                with st.spinner(f"Building knowledge base from {selected_file}..."):
                    ok, msg = build_index_from(os.path.join(_UPLOADS, selected_file))
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.warning("No files found. Upload one or use the sample knowledge base.")

    # Sample PDF button (only shown when the file exists in the repo)
    if os.path.exists(SAMPLE_PDF):
        if st.button("📋 Use Sample Insurance PDF", key="use_sample"):
            with st.spinner("Building knowledge base from sample..."):
                ok, msg = build_index_from(SAMPLE_PDF)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # Status indicator
    if st.session_state.index_loaded:
        st.success("✅ Knowledge base is ready")
    else:
        st.warning("⚠️ Knowledge base not loaded")

    st.divider()

    # ── Clear ──
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! Ask me anything about your insurance policy or claims."}
        ]
        st.rerun()

    st.divider()

    st.caption("💡 **Tips:**")
    st.caption("- Ask about claims, coverage, deductibles")
    st.caption("- Request specific policy details")
    st.caption("- Inquire about required documents")


# ──────────────────────────────────────────────────────────────────────────
# UI – Chat area
# ──────────────────────────────────────────────────────────────────────────
st.divider()

for message in st.session_state.messages:
    role, content = message["role"], message["content"]
    if role == "user":
        st.markdown(
            f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-message bot-message"><strong>Assistant:</strong><br>{content}</div>',
            unsafe_allow_html=True
        )

if not st.session_state.index_loaded:
    st.warning("⚠️ Please build the knowledge base first using the sidebar.")
else:
    user_input = st.chat_input("Type your question here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            ok, bot_response = chat(user_input)

        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_response if ok else f"Sorry, I encountered an error: {bot_response}"
        })
        st.rerun()


# Footer
st.divider()
st.caption("🤖 Powered by Groq AI | Built with Streamlit")
