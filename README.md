# HR Policy Q&A Bot — Employee Onboarding Assistant

A **Retrieval-Augmented Generation (RAG)** chatbot that lets new employees ask natural language questions about company HR policies and receive grounded, cited answers — no more digging through 60-page handbooks.

Built with **LangChain**, **FAISS**, **FastEmbed**, and **Groq (Llama 3.3 70B)**, served via **Streamlit**.
**100% free to run** — no paid API required for embeddings; Groq offers a generous free tier.

---

## What It Does

Upload an HR/benefits PDF and ask questions like:

- *"How many PTO days do I get in my first year?"*
- *"When am I eligible for the 401k match?"*
- *"What percentage does the company match on retirement?"*
- *"How does sick leave accrue?"*
- *"What is the vacation carry-over policy?"*
- *"How many sick days do I get per year?"*
- *"What are the health and dental insurance benefits?"*
- *"How many days do I need to be in the office under the hybrid policy?"*
- *"How do I submit an expense report?"*
- *"How often are performance reviews conducted?"*
- *"Am I eligible for FMLA leave?"*
- *"What is the company's anti-harassment policy?"*

![HR Policy Q&A Bot Demo](https://raw.githubusercontent.com/robertciceroson/HR-Policy-QA-Bot/main/hr_policy_bot_demo.gif)

The bot retrieves the exact policy sections, generates a grounded answer, and cites the source document and page number. For questions outside the uploaded documents, it responds honestly that it doesn't have that information rather than guessing.

---

## Sample Document

The included `sample_docs/HR_Policy_Handbook.pdf` is a fictional "Acme Corp" employee handbook covering 12 policy areas:

| # | Section |
|---|---------|
| 1 | Paid Time Off (PTO) |
| 2 | Sick Leave |
| 3 | Vacation Policy (Legacy) |
| 4 | 401(k) Retirement Plan |
| 5 | Health & Dental Benefits |
| 6 | Company Holidays |
| 7 | Remote Work Policy |
| 8 | Expense Reimbursement |
| 9 | Performance Reviews & Compensation Cycle |
| 10 | Leave of Absence & FMLA |
| 11 | Code of Conduct & Equal Employment Opportunity |
| 12 | HR Contact Information |

It's entirely synthetic content, generated for demonstration purposes — not based on any real company's actual handbook.

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
| Persisted vectorstore | Index saved to disk locally — no re-upload needed between local restarts |
| `RetrievalQAWithSourcesChain` | Returns source citations alongside answers for traceability |
| `temperature=0` | Ensures deterministic, factual responses grounded in policy text |
| Groq free tier | Fast LLM inference at no cost |

---

## Project Structure

```
HR-Policy-QA-Bot/
├── app.py                    # Main Streamlit application
├── create_sample_docs.py     # Generates the synthetic sample handbook
├── requirements.txt          # Python dependencies
├── .env.example               # Environment variable template (copy to .env)
├── .gitignore
├── sample_docs/
│   └── HR_Policy_Handbook.pdf
└── vectorstore/               # FAISS index — generated locally after first
                                # upload, NOT committed to git (see .gitignore)
```

> `venv/`, `.env`, and `vectorstore/` are intentionally excluded from version control via `.gitignore` — they're either machine-specific, secret, or regenerable.

---

## Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/robertciceroson/HR-Policy-QA-Bot.git
cd HR-Policy-QA-Bot
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Configure your API key

```bash
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux
```

Then open `.env` and add your free Groq API key (get one at [console.groq.com](https://console.groq.com)):

```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501`, upload `sample_docs/HR_Policy_Handbook.pdf` (or your own HR PDF) from the sidebar, and start asking questions.

On subsequent local restarts, the saved index loads automatically — no re-upload needed, as long as `vectorstore/` still exists on disk.

---

## Document Persistence

| Action | Result |
|---|---|
| First upload | Index built and saved to `vectorstore/` |
| App restart (same machine) | Saved index auto-loaded, chat ready immediately |
| Upload a new/different PDF | New index replaces the old one |
| Click "Clear saved index" | Index deleted, upload prompt returns |

> ⚠️ **Stale index warning:** If you swap the source PDF but don't clear the old index first, the app will keep answering from the previous document's embeddings. Always click **"🗑️ Clear saved index"** in the sidebar before uploading a replacement document.

---

## Switching LLM Provider

Only a few lines change. The rest of the app stays identical.

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

1. Push this repo to GitHub (already done — `vectorstore/` is intentionally **not** included; it will be generated on first upload after deployment)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select this repo
3. Add `GROQ_API_KEY` under Advanced settings → Secrets
4. Deploy — get a public URL instantly
5. Note: on most free hosting tiers, disk storage isn't guaranteed to persist across restarts/redeploys, so you may need to re-upload your PDF after the app sleeps and wakes back up

### ngrok (instant, no GitHub needed)

```bash
# While streamlit is running:
ngrok http 8501
```

---

## Sample Output

**Question:** *How many PTO days do I get in my first year?*

**Answer:** *In your first year, you accrue 10 days (80 hours) of PTO per year, accrued at 0.833 days per month, as stated in the PTO Accrual Schedule for full-time employees (Years 0-1).*

**Source:** HR_Policy_Handbook.pdf — Section 1

---

## Technologies Used

| Tool | Purpose |
|---|---|
| [LangChain](https://python.langchain.com/) | RAG pipeline orchestration |
| [FAISS](https://github.com/facebookresearch/faiss) | Local vector similarity search |
| [FastEmbed](https://github.com/qdrant/fastembed) | ONNX-based local embeddings (no torch needed) |
| [Groq API](https://console.groq.com/) | Free LLM inference (Llama 3.3 70B via Groq) |
| [PyPDF](https://pypdf.readthedocs.io/) | PDF loading and text extraction |
| [Streamlit](https://streamlit.io/) | Chat UI |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | API key management |

---

## Responsible AI Notes

- **Grounded responses only** — the model answers exclusively from retrieved document chunks
- **Source citations** — every answer shows the source document and section
- **Honest fallback** — when the answer isn't in the documents, the bot says so rather than hallucinating (verified behavior: a question about vacation carry-over correctly returned "I don't have that information" since the source document's legacy vacation section doesn't specify a carry-over policy, unlike PTO and sick leave)
- **Local embeddings** — document content is embedded locally via FastEmbed; only the question and retrieved chunks are sent to Groq
---
Author

Robert C. Son
Technical Scrum Master · AI Business Process Analyst · Data Analyst · Translating AI/ML into ROI · CSM · CSPO · AI-Empowered SAFe Agilist · Active DoD Secret Clearance

