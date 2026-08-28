# EduMate: Synchronized 7-Month Roadmap – AI & RAG Specialist (Team Lead)

## Role & Technical Ownership
- **Role**: AI & RAG Specialist (Team Lead / Member 1)
- **Primary Domain**: `services/ai_rag/`
- **Core Systems**: Google Gemini 1.5 Pro / Flash Prompt System, RAG Knowledge Processing (PyMuPDF, Chunking, Gemini Embeddings `text-embedding-004`), Qdrant Vector DB Hybrid Search, Grounding & Citation Fallbacks, Structured Quiz JSON Generation.

---

## Commit & Synchronization Strategy
- **Synchronized Milestones**: Aligned directly with Voice, Backend, and Frontend roles to eliminate integration bottlenecks.
- **Commit Cadence**: 10 active commit days per month.
- **Commit Volume**: ~30 atomic human-authored commits per month (total 210+ commits across 7 months).
- **Human Commit Style**: Clean messages (e.g., `feat: implement Socratic level prompt builder`, `refactor: optimize Qdrant hybrid search params`). No AI/agent references.

---

## 📅 Month-by-Month Synchronized Roadmap & Commit Plan

### 🔷 Month 1: Foundation & Baseline Setup (Completed / In Progress)
* **Goal**: Establish Gemini API client, Socratic prompt architecture, baseline document parsing schema contracts.
* **Key Tasks**:
  * Set up Google Gemini API client (`services/ai_rag/llm_client.py`).
  * Define Pydantic request/response schemas for prompt generation.
  * Establish RAG evaluation benchmarks for technical engineering textbooks.
* **Commit Schedule (10 Days, 30 Commits)**:
  * *Day 1-2*: Project init, Gemini API key configs, SDK wrappers. (3 commits)
  * *Day 3-4*: Socratic prompt template design and system prompt builders. (3 commits)
  * *Day 5-6*: Pydantic schema validation for chat context & RAG outputs. (3 commits)
  * *Day 7-8*: PDF text parsing baseline with PyMuPDF (`fitz`). (3 commits)
  * *Day 9-10*: Qdrant vector database collection schema setup. (3 commits)

---

### 🔷 Month 2: Core Conversational Tutor & Level-Based Engine
* **Goal**: Implement Socratic persona prompts for 3 learning levels (*Beginner*, *Intermediate*, *Advanced*).
* **Key Tasks**:
  * Build level-specific prompt builders adjusting terminology depth, analogies, and complexity.
  * Create prompt handlers for quick actions ("Simplify", "Give Example", "Explain Deeper").
  * Implement formatting rules enforcing LaTeX math math blocks and code blocks.
* **Commit Schedule (10 Days, 30 Commits)**:
  * *Day 1-2*: Beginner prompt template with intuitive analogies. (3 commits)
  * *Day 3-4*: Intermediate & Advanced prompt templates with edge cases. (3 commits)
  * *Day 5-6*: Socratic follow-up clarification prompt pipeline. (3 commits)
  * *Day 7-8*: LaTeX math formatting validation rules in LLM responses. (3 commits)
  * *Day 9-10*: Code block syntax formatting validation and unit tests. (3 commits)

---

### 🔷 Month 3: RAG Knowledge Engine & Study Material Pipeline
* **Goal**: Build full PDF ingestion, semantic chunking, vector embedding, and grounded search engine.
* **Key Tasks**:
  * Implement header-aware semantic recursive text splitter (500-1000 tokens, 100-token overlap).
  * Integrate Google Gemini Embeddings (`text-embedding-004`) pipeline.
  * Configure Qdrant Dense Vector + BM25 Sparse Hybrid Search logic.
  * Build Document Grounding & Citation mapping prompt with fallback handling (*"Information not found in study material"*).
* **Commit Schedule (10 Days, 30 Commits)**:
  * *Day 1-2*: PyMuPDF text & table extraction parser enhancement. (3 commits)
  * *Day 3-4*: Recursive text chunking logic with section metadata retention. (3 commits)
  * *Day 5-6*: Gemini embedding pipeline integration and batch processing. (3 commits)
  * *Day 7-8*: Qdrant hybrid search query builder and similarity thresholds. (3 commits)
  * *Day 9-10*: Citation mapping engine and document grounding fallback alert. (3 commits)

---

### 🔷 Month 4: Multilingual Prompt Alignment & Quality Audit
* **Goal**: Align pedagogical prompt persona across English, Hindi, and Telugu.
* **Key Tasks**:
  * Optimize system prompts to maintain encouraging Socratic tone in Hindi and Telugu.
  * Build query language detection fallback and multilingual prompt templating.
  * Conduct RAG retrieval precision & recall audits on complex academic notes.
* **Commit Schedule (10 Days, 30 Commits)**:
  * *Day 1-2*: Hindi Socratic system prompt template optimization. (3 commits)
  * *Day 3-4*: Telugu Socratic system prompt template optimization. (3 commits)
  * *Day 5-6*: Multilingual query language detection and context mapper. (3 commits)
  * *Day 7-8*: Technical domain dictionary mapping for Hindi/Telugu explanations. (3 commits)
  * *Day 9-10*: RAG precision evaluation benchmark tests and hallucination checks. (3 commits)

---

### 🔷 Month 5: AI Quiz Generation & Evaluation Prompts
* **Goal**: Build structured JSON quiz generation and corrective evaluation prompts.
* **Key Tasks**:
  * Design Gemini Structured JSON mode prompts for MCQs, True/False, and Short Answer questions.
  * Implement difficulty scaling prompts based on topic and target learning level.
  * Create evaluation prompts offering step-by-step corrective explanations for wrong answers.
* **Commit Schedule (10 Days, 30 Commits)**:
  * *Day 1-2*: MCQ structured JSON prompt generator and Pydantic validator. (3 commits)
  * *Day 3-4*: True/False & Short Answer question generator prompts. (3 commits)
  * *Day 5-6*: Adaptive difficulty question scaler based on student mastery score. (3 commits)
  * *Day 7-8*: Step-by-step corrective answer evaluation prompt system. (3 commits)
  * *Day 9-10*: Quiz JSON response repair middleware for LLM formatting errors. (3 commits)

---

### 🔷 Month 6: Personalized Context Injection & Recommendation Prompts
* **Goal**: Inject identified weak topics into tutoring sessions and generate study recommendations.
* **Key Tasks**:
  * Build prompt context injection module loading student weak areas into active chat.
  * Design system prompts for generating prioritized next topic study recommendations.
  * Test long-term tutoring continuity across multiple study sessions.
* **Commit Schedule (10 Days, 30 Commits)**:
  * *Day 1-2*: Weak area profile context injection pipeline. (3 commits)
  * *Day 3-4*: Personalized next topic recommendation prompt builder. (3 commits)
  * *Day 5-6*: Long-term conversation summary context compression module. (3 commits)
  * *Day 7-8*: Dynamic revision prompt triggers based on quiz error history. (3 commits)
  * *Day 9-10*: Integration tests for profile-aware tutoring sessions. (3 commits)

---

### 🔷 Month 7: System Optimization, Hallucination Audit & Capstone Thesis
* **Goal**: Optimize RAG latency, perform zero-hallucination verification, and author thesis.
* **Key Tasks**:
  * Token usage optimization and response caching for common questions.
  * Rigorous RAG document grounding audit.
  * Author AI, RAG, Prompt Engineering, and Gemini integration chapters for Capstone Report.
* **Commit Schedule (10 Days, 30 Commits)**:
  * *Day 1-2*: LLM prompt token usage compression and response latency tuning. (3 commits)
  * *Day 3-4*: Full RAG hallucination elimination audit. (3 commits)
  * *Day 5-6*: End-to-end AI engine performance benchmarks. (3 commits)
  * *Day 7-8*: Capstone thesis writing: AI & RAG Architecture sections. (3 commits)
  * *Day 9-10*: Final code documentation, prompt catalog clean-up, and release tagging. (3 commits)
