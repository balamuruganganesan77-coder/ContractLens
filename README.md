# ContractLens ⚖️
### AI Contract Intelligence & Obligation Tracking Agent

> **Understand Every Contract. Track Every Obligation.**

ContractLens is a production-grade, hackathon-ready SaaS application built with Python, Streamlit, PyMuPDF, Google Gemini API (`gemini-2.5-flash`), ChromaDB, SQLite, and Plotly. It transforms complex legal PDF contracts into structured, searchable, explainable business intelligence.

---

## 📌 Executive Summary

Businesses handle contracts across vendors, customers, partners, and service providers. Key information such as renewal dates, payment terms, termination clauses, service commitments, deadlines, and obligations can be difficult to track manually. 

ContractLens solves this by using a **Multi-Agent AI Architecture** to:
1. Parse PDF documents while preserving exact page numbers.
2. Index chunks into **ChromaDB** for vector-based Retrieval-Augmented Generation (RAG).
3. Automatically extract structured fields, parties, deadlines, and terms into **Pydantic** models.
4. Detect high, medium, and low-risk clauses requiring human legal review.
5. Extract operational obligations and persist completion status in **SQLite**.
6. Render interactive milestone timelines with **30-day proximity alerts** using **Plotly**.
7. Compare PDF contract versions (V1 vs V2) using Python `difflib` and explain business/financial impacts.
8. Answer natural language questions strictly grounded in contract context with **Page X citations**.

---

## 🏗 System Architecture

```
ContractLens/
├── app.py                      # Streamlit SaaS UI & Feature Navigation
├── models.py                   # Pydantic Data Models & Extraction Schemas
├── db.py                       # SQLite Database Storage & Persistence Layer
├── requirements.txt            # Package Dependencies
├── .env.example                # Environment Template
├── .env                        # Active Environment Variables
├── .gitignore                  # Git Ignore Rules
├── README.md                   # Documentation & Workflow Guide
│
└── agents/                     # Multi-Agent Architecture Pipeline
    ├── __init__.py             # Agent Package Exports
    ├── ingest.py               # Agent 1: Ingestion (PyMuPDF + ChromaDB RAG Indexing)
    ├── extract.py              # Agent 2: Contract Extraction (Gemini Structured Parsing)
    ├── risk.py                 # Agent 3: Risk Center (Automated Risk Flag Detector)
    ├── timeline.py             # Agent 4: Timeline & 30-Day Proximity Alerts (Plotly)
    ├── compare.py              # Agent 5: Version Comparison (difflib + AI Impact)
    └── chat.py                 # Agent 6: Contract Chat (RAG Q&A with Citation Tracking)
```

---

## 🛠 Tech Stack

- **Framework**: Python 3.11+
- **Frontend UI**: Streamlit with custom CSS (Indigo/Dark SaaS aesthetic)
- **PDF Parsing**: PyMuPDF (`fitz`)
- **AI Model**: Google Gemini API (`gemini-2.5-flash`)
- **Structured Output**: Pydantic v2
- **Vector Database (RAG)**: ChromaDB
- **Relational Storage**: SQLite3
- **Data Visualization**: Plotly Express & Plotly Graph Objects
- **Text Comparison**: Python `difflib`
- **Environment**: `python-dotenv`

---

## 🚀 Quickstart & Installation

### 1. Clone or Open Workspace
Ensure you are in the project folder:
```bash
cd ContractLens
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Open `.env` and add your **Google Gemini API Key**:
```env
GEMINI_API_KEY=AIzaSy...
```

### 4. Run Application
Launch the Streamlit web app:
```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

## 🎬 Hackathon Demo Workflow (12 Steps)

1. **Launch App**: Open `http://localhost:8501` to view the modern ContractLens dashboard.
2. **Upload Contract**: Navigate to **Upload Contracts** and drag-and-drop a sample contract PDF.
3. **Trigger Pipeline**: Click **🚀 Analyze Contracts**. Watch the multi-agent ingestion, RAG indexing, extraction, and risk scanning execute seamlessly.
4. **View Summary**: Navigate to **Contract Analysis** to review the Executive Summary and key fields.
5. **Inspect Citations**: Click expanders to view source clause quotes with exact page numbers.
6. **Search Contract**: Type keywords (e.g. `liability`, `Net 30`) into the live contract search bar.
7. **Track Obligations**: Navigate to **Obligations**. View assigned responsibilities, deadlines, and click **Mark Completed** to update state in SQLite.
8. **Inspect Risk Center**: Open **Risk Center** to inspect red flags (unlimited liability, auto-renewals) labeled with **Human Review Recommended**.
9. **Interactive Timeline**: Open **Timeline** to view the interactive Plotly Gantt chart and review 30-day alerts (🔴 Overdue, 🟠 Due within 30 days, 🟢 Upcoming).
10. **Ask Chatbot**: Navigate to **Contract Chat** and ask: *"When does this contract expire?"* or *"What are the payment terms?"*.
11. **Review Source Evidence**: Expand **🔍 View Source Evidence** under the bot answer to inspect the retrieved page text.
12. **Version Comparison**: Navigate to **Version Compare**, upload `V1.pdf` and `V2.pdf`, and click **Compare Versions** to inspect textual diffs paired with AI business impact explanations.

---

## ⚖️ Legal Disclaimer

> **IMPORTANT**: ContractLens is an AI assistant designed to streamline contract review and obligation tracking. It is **NOT** a replacement for licensed legal professionals and does **NOT** provide formal legal advice.
