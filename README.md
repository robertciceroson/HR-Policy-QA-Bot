# HR Policy Q&A Bot — Employee Onboarding Assistant

A **Retrieval-Augmented Generation (RAG)** chatbot that lets new employees ask natural language questions about company HR policies and receive grounded, cited answers — no more digging through 60-page handbooks.

Built with **LangChain**, **FAISS**, **FastEmbed**, and **Groq (Llama 3.3 70B)**, served via **Streamlit**.  
**100% free to run** — no paid API required for embeddings; Groq offers a generous free tier.

---

## What It Does

Upload any HR/benefits PDF and ask questions like:

- *"How many PTO days do I get in my first year?"*
- *"When am I eligible for the 401k match?"*
- *"What percentage does the company match on retirement contributions?"*
- *"How does sick leave accrue?"*
- *"What is the vacation carry-over policy?"*

The bot retrieves the exact policy sections, generates a grounded answer, and cites the source document and page number. For questions outside the uploaded documents it responds politely that it doesn't have that information.

---

## RAG Architecture

```
PDF Documents
     │
     ▼
[PyPDFLoader] ──► [RecursiveCharacterTextSplitter]
     │                  chunk_size=800, overlap=100
     ▼
[FastEmbedEmbeddings]  ←── BAAI/bge-small-en-v1.5
     │                      (ONNX-based, runs locally, no API key, no torch needed)
     ▼
[FAISS Vector Store] ──► persisted to disk (auto-loaded on restart)
     │
     │   User Question
     ▼
[Similarity Search] ──► top-4 most relevant chunks
     │
     ▼
[Groq API — Llama 3.3 70B] ──► grounded answer + source citations
     │
     ▼
[Streamlit Chat UI]
```

### Key Design Decisions

| Decision | Rationale |
|---|---|
| `RecursiveCharacterTextSplitter` | Preserves sentence boundaries better than fixed-size splitting |
| `FastEmbed / BAAI bge-small-en-v1.5` | ONNX-based, no torch/torchvision dependency, fast and free |
| `FAISS` vector store | Lightweight local index, no cloud vector DB required |
| `Persisted vectorstore` | Index saved to disk — no re-upload needed on restart |
| `RetrievalQAWithSourcesChain` | Returns source citations alongside answers for traceability |
| `temperature=0` | Ensures deterministic, factual responses grounded in policy text |
| `Groq free tier` | Fast LLM inference at no cost |

---

## Project Structure

```
HR-Policy-QA-Bot/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env                      # Your API key (not committed)
├── .env.example              # Environment variable template
├── .gitignore
├── .streamlit/
│   └── config.toml           # Streamlit config (disables torch file watcher)
├── sample_docs/
│   └── HR_Policy_Handbook.pdf
└── vectorstore/              # FAISS index — auto-saved after first upload
```

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/hr-policy-bot.git
cd hr-policy-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your API key
```bash
cp .env.example .env
# Add your Groq API key — get one free at https://console.groq.com
```
`.env` contents:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501`, upload your HR PDF from the sidebar, and start asking questions.  
On subsequent restarts the saved index loads automatically — **no re-upload needed**.

---

## Document Persistence

| Action | Result |
|---|---|
| First upload | Index built and saved to `vectorstore/` |
| App restart | Saved index auto-loaded, chat ready immediately |
| Upload new PDF | New index replaces the old one |
| Click "Clear saved index" | Index deleted, upload prompt returns |

> ⚠️ **Stale index warning:** If you swap the PDF but don't clear the old index first, the app will answer from the previous document's embeddings. Always click **"🗑️ Clear saved index"** in the sidebar before uploading a replacement document.

---

## Switching LLM Provider

Only 3 lines change. The rest of the app stays identical.

**OpenAI**
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
```

**Anthropic Claude**
```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-haiku-20241022", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"), temperature=0)
```

---

## Deployment

### Streamlit Community Cloud (free, permanent URL)
1. Push repo to GitHub (including `vectorstore/` folder)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select repo
3. Add `GROQ_API_KEY` under Advanced settings → Secrets
4. Deploy — get a public URL instantly

### ngrok (instant, no GitHub needed)
```bash
# While streamlit is running:
ngrok http 8501
```

---

## Sample Output

**Question:** *How many PTO days do I get in my first year?*

**Answer:** *You accrue 10 days (80 hours) per year in your first year, accrued at 0.833 days per month, as stated in the PTO Accrual Schedule for full-time employees (Years 0-1).*

**Source:** HR_Policy_Handbook.pdf — Page 0, Page 1

---

## Technologies Used

| Tool | Purpose |
|---|---|
| [LangChain](https://python.langchain.com/) | RAG pipeline orchestration |
| [FAISS](https://github.com/facebookresearch/faiss) | Local vector similarity search |
| [FastEmbed](https://github.com/qdrant/fastembed) | ONNX-based local embeddings (no torch needed) |
| [Groq API](https://console.groq.com/) | Free LLM inference (Llama 3.3 70B) |
| [PyPDF](https://pypdf.readthedocs.io/) | PDF loading and text extraction |
| [Streamlit](https://streamlit.io/) | Chat UI |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | API key management |

---

## Responsible AI Notes

- **Grounded responses only** — the model answers exclusively from retrieved document chunks
- **Source citations** — every answer shows the source document and page number
- **Polite fallback** — when the answer is not in the documents, the bot responds with a polite apology rather than hallucinating
- **Local embeddings** — document content is embedded locally via FastEmbed; only the question + retrieved chunks are sent to Groq
