"""
HR Policy Q&A Bot — Employee Onboarding Assistant
RAG pipeline: PDF ingestion → chunking → embeddings → FAISS → grounded LLM response
Built with LangChain, FAISS, Groq API, and Streamlit
"""

import os
import streamlit as st
from dotenv import load_dotenv
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import PromptTemplate

load_dotenv()

# ── API key guard ─────────────────────────────────────────────────────────────
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "**GROQ_API_KEY is missing.** "
        "Create a `.env` file with `GROQ_API_KEY=your_key` and restart the app. "
        "Get a free key at https://console.groq.com"
    )
    st.stop()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Policy Q&A Bot",
    page_icon="📋",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Header */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 700; }
    .main-header p  { color: #888; font-size: 0.95rem; margin-top: 0.25rem; }

    /* Status badge */
    .status-badge {
        display: inline-block;
        background: #1a472a;
        color: #4ade80;
        border: 1px solid #4ade80;
        border-radius: 20px;
        padding: 0.3rem 1rem;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    /* Source citation expander */
    .streamlit-expanderHeader {
        font-size: 0.82rem !important;
        color: #888 !important;
    }

    /* Sidebar section headers */
    section[data-testid="stSidebar"] h2 { font-size: 1.1rem; }

    /* Chat input placeholder */
    .stChatInput textarea::placeholder { color: #666; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📋 HR Policy Q&amp;A Bot</h1>
    <p>Ask any question about your company's HR policies — answers are grounded in your documents with source citations.</p>
</div>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
VECTORSTORE_PATH = "vectorstore/hr_faiss_index"
CHUNK_SIZE       = 800
CHUNK_OVERLAP    = 100
EMBED_MODEL      = "BAAI/bge-small-en-v1.5"  # free, local, no torch/torchvision needed

# ── Helper: load & chunk PDFs ─────────────────────────────────────────────────
def load_and_chunk_pdfs(uploaded_files: list) -> list:
    """Load uploaded PDFs, split into overlapping chunks."""
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    for uploaded_file in uploaded_files:
        # Write temp file so PyPDFLoader can read it
        tmp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.read())
        loader = PyPDFLoader(tmp_path)
        pages  = loader.load()
        chunks = splitter.split_documents(pages)
        # Tag each chunk with its source filename and fix to 1-indexed page numbers
        for chunk in chunks:
            chunk.metadata["source"] = uploaded_file.name
            if "page" in chunk.metadata:
                chunk.metadata["page"] = chunk.metadata["page"] + 1
        all_docs.extend(chunks)
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    return all_docs

# ── Helper: build / load FAISS vectorstore ────────────────────────────────────
@st.cache_resource(show_spinner="Building vector index…")
def build_vectorstore(file_names_key: str, _docs: list):
    """
    Create FAISS index from document chunks.
    Uses FastEmbed (ONNX-based, runs locally, no torch/torchvision dependency).
    Cache key is the sorted filenames so re-uploading new files rebuilds.
    """
    embeddings = FastEmbedEmbeddings(model_name=EMBED_MODEL)
    vectorstore = FAISS.from_documents(_docs, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    return vectorstore

@st.cache_resource(show_spinner="Loading saved index…")
def load_saved_vectorstore():
    """Load a previously saved FAISS index from disk (no re-upload needed)."""
    embeddings = FastEmbedEmbeddings(model_name=EMBED_MODEL)
    return FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)

# ── Helper: build QA chain ────────────────────────────────────────────────────
def build_qa_chain(vectorstore):
    """
    RetrievalQAWithSourcesChain:
    - Retrieves top-k relevant chunks
    - Passes them as context to Claude
    - Returns answer + source citations
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=1024
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}          # retrieve 4 most relevant chunks
    )

    prompt_template = """You are a helpful HR assistant helping new employees understand company policies.
Use ONLY the context provided to answer the question. Be specific and cite exact numbers, 
percentages, and eligibility dates when they appear in the documents.
If the answer is not in the context, say: "I'm sorry, I don't have information related to this. Please feel free to ask me anything else, and I'll do my best to help!"

Context:
{summaries}

Question: {question}

Answer (be concise and cite specific policy details):"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["summaries", "question"]
    )

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    return chain

# ── Sidebar: document upload ──────────────────────────────────────────────────
saved_index_exists = os.path.exists(VECTORSTORE_PATH)

with st.sidebar:
    st.markdown("## 📁 Upload HR Documents")
    st.markdown(
        "Upload one or more PDF files:\n"
        "- Employee Handbook\n"
        "- Benefits Guide\n"
        "- 401k / Retirement Plan\n"
        "- PTO / Leave Policy\n"
    )
    with open("sample_docs/HR_Policy_Handbook.pdf", "rb") as f:
        st.download_button(
            label="⬇️ No doc? Download sample handbook",
            data=f,
            file_name="HR_Policy_Handbook.pdf",
            mime="application/pdf"
        )
    st.markdown("---")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} document(s) loaded")
        for f in uploaded_files:
            st.caption(f"📄 {f.name}")
    elif saved_index_exists:
        st.info("💾 Using saved index from last session.")
        if st.button("🗑️ Clear saved index"):
            import shutil
            shutil.rmtree(VECTORSTORE_PATH, ignore_errors=True)
            st.cache_resource.clear()
            st.rerun()

    st.markdown("---")
    st.markdown("**💬 Sample questions:**")
    
    sample_questions = [
        "How many PTO days do I get in my first year?",
        "When am I eligible for the 401k match?",
        "What percentage does the company match on retirement?",
        "How does sick leave accrue?",
        "What is the vacation carry-over policy?",
        "How many sick days do I get per year?",
        "What are the health and dental insurance benefits?",
        "How many days do I need to be in the office under the hybrid policy?",
        "How do I submit an expense report?",
        "How often are performance reviews conducted?",
        "Am I eligible for FMLA leave?",
        "What is the company's anti-harassment policy?",
    ]
    for q in sample_questions:
        st.caption(f"• {q}")

    st.markdown("---")
    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Powered by Groq · LangChain · FAISS · FastEmbed")

# ── Main: vectorstore + chat ──────────────────────────────────────────────────
if not uploaded_files and not saved_index_exists:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 📄 Upload")
        st.caption("Drop your HR policy PDFs in the sidebar")
    with col2:
        st.markdown("#### 🔍 Ask")
        st.caption("Type any policy question in plain English")
    with col3:
        st.markdown("#### ✅ Get Answers")
        st.caption("Receive grounded answers with source citations")
    st.markdown("---")
    st.markdown(
        "### How it works\n"
        "1. **Ingest** — PDFs are split into overlapping chunks\n"
        "2. **Embed** — Chunks are converted to vectors via FastEmbed (local, free)\n"
        "3. **Index** — Vectors stored in a FAISS similarity index and saved to disk\n"
        "4. **Retrieve** — Your question is matched to the most relevant chunks\n"
        "5. **Generate** — Groq (Llama 3.3 70B) answers using only the retrieved policy text\n"
        "6. **Cite** — Source document and page shown with every answer\n"
    )
else:
    # Build new vectorstore from upload, or load existing one from disk
    if uploaded_files:
        docs = load_and_chunk_pdfs(uploaded_files)
        if not docs:
            st.error("No extractable text was found in the uploaded PDF(s). The file may be a scanned image without a text layer, or empty.")
            st.stop()
        file_names_key = "_".join(sorted([f.name for f in uploaded_files]))
        vectorstore = build_vectorstore(file_names_key, docs)
        st.markdown(
            f'<div class="status-badge">✅ Indexed {len(docs)} chunks from '
            f'{len(uploaded_files)} document(s) — Ready</div>',
            unsafe_allow_html=True
        )
    else:
        vectorstore = load_saved_vectorstore()
        st.markdown(
            '<div class="status-badge">✅ Loaded saved index — Ready</div>',
            unsafe_allow_html=True
        )

    qa_chain = build_qa_chain(vectorstore)

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("📎 Source Citations"):
                    for src in msg["sources"]:
                        st.caption(
                            f"📄 **{src['source']}** — Page {src.get('page', 'N/A')}"
                        )  

    # Chat input
    if question := st.chat_input("Ask an HR policy question…  e.g. How many PTO days do I get?"):
        # Show user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("Searching policy documents…"):
                result  = qa_chain.invoke({"question": question})
                answer  = result.get("answer", "No answer found.")
                src_docs = result.get("source_documents", [])

                st.markdown(answer)

                # Only show citations when the answer came from the documents
                is_fallback = answer.strip().startswith("I'm sorry")
                seen = set()
                sources = []
                if not is_fallback:
                    for doc in src_docs:
                        key = (doc.metadata.get("source", "Unknown"),
                               doc.metadata.get("page", "N/A"))
                        if key not in seen:
                            seen.add(key)
                            sources.append({
                                "source": doc.metadata.get("source", "Unknown"),
                                "page":   doc.metadata.get("page", "N/A")
                            })

                if sources:
                    with st.expander("📎 Source Citations"):
                        for src in sources:
                            page = src['page'] if src['page'] != 'N/A' else 'N/A'
                            st.caption(
                                f"📄 **{src['source']}** — Page {page}"
                            )

        st.session_state.messages.append({
            "role":    "assistant",
            "content": answer,
            "sources": sources
        })
