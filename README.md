# EduMate — Multilingual AI Personal Tutor Platform

EduMate is an intelligent, multilingual AI personal tutor platform designed for students. It provides adaptive Socratic tutoring, PDF study material RAG (Retrieval-Augmented Generation), automated diagnostic quizzes, weak-area analytics, and curriculum planning across English, Hindi, and Telugu.

---

## 🏛 System Architecture

```text
                  ┌────────────────────────┐
                  │     React Frontend     │
                  │   Vite + TypeScript    │
                  └───────────┬────────────┘
                              │ REST API
                              ▼
                  ┌────────────────────────┐
                  │  Python FastAPI        │
                  │  Backend API Gateway   │
                  └───────────┬────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
     ┌─────────┐         ┌──────────┐        ┌───────────┐
     │ AI Tutor│         │   RAG    │        │ Learning  │
     │ Engine  │         │ Pipeline │        │ Engine    │
     └────┬────┘         └────┬─────┘        └─────┬─────┘
          │                   │                    │
          ▼                   ▼                    ▼
     Gemini LLM          Qdrant Vector          MongoDB
     (STT / TTS)           Database             Database
```

---

## 📂 Project Structure

```text
EduMate/
├── frontend/               # React 19 + TypeScript + Vite UI
│   ├── src/                # Views, components, API client, types
│   ├── public/             # Static assets (favicons, etc.)
│   ├── package.json        # Frontend scripts and dependencies
│   └── vite.config.ts      # Vite dev server & build configuration
│
├── backend/                # FastAPI Application & Domain Services
│   ├── main.py             # API Gateway routers & WebSocket endpoints
│   ├── config.py           # Application settings & environment config
│   ├── schemas.py          # Pydantic v2 request/response schemas
│   ├── services/           # Analytics, Quiz, Planner, Revision engines
│   ├── tests/              # Backend endpoint & unit tests
│   └── requirements.txt    # Python dependencies for backend
│
├── database/               # Dedicated MongoDB Database Layer
│   ├── connection.py       # PyMongo client & connection lifecycle
│   ├── models.py           # Document schemas & type definitions
│   ├── repository.py       # CRUD operations & queries
│   ├── seed_data.py        # Seed datasets & initial curriculum
│   ├── vector_store.py     # MongoDB document vector persistence
│   └── __init__.py         # Package exports
│
├── ai_rag/                 # AI & Knowledge Retrieval Engine
│   ├── llm_client.py       # Google Gemini 1.5 client wrapper
│   ├── document_processing/# PDF parsing (PyMuPDF) & text chunking
│   ├── embeddings/         # Gemini text-embedding-004 integration
│   ├── prompts/            # Socratic prompts & adaptive difficulty scaler
│   ├── validators/         # LaTeX, code snippet, and citation checkers
│   ├── vector_store/       # Qdrant client & BM25 hybrid search
│   └── tests/              # AI & RAG unit test suite
│
├── temp_uploads/           # Local workspace for temporary PDF uploads (ignored)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
* **Python**: 3.11+
* **Node.js**: 18+ (Node 20+ recommended)
* **MongoDB**: Running locally at `mongodb://localhost:27017`

### 1. Run the Backend API
From the root directory:
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
* **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Run the Frontend
In a separate terminal:
```bash
cd frontend
npm run dev
```
* **Web UI**: [http://localhost:5173](http://localhost:5173)

### 3. Run Automated Tests
```bash
python -m pytest backend/tests/ ai_rag/tests/
```
