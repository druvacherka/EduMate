# EduMate Project Guidelines for Antigravity

## Project Overview
EduMate is a Multilingual AI Personal Tutor platform for B.Tech Capstone Project.
It combines voice/text interaction (English, Hindi, Telugu), Socratic tutoring, PDF study material RAG, AI quiz generation, weak area tracking, and progress analytics.

## Core System Architecture & Directory Structure
- `frontend/`: React 18 + TypeScript + Vite + CSS Modules (Frontend UI, KaTeX math, Prism code blocks, Audio visualizers).
- `backend/`: Python 3.11 FastAPI + PostgreSQL + Redis (API Gateway, Auth, Database Models, Quiz State Machine, Analytics APIs).
- `services/ai_rag/`: Google Gemini 1.5 Pro/Flash + Qdrant Vector Store + PyMuPDF RAG Engine (Role 1: AI & RAG Specialist).
- `services/voice/`: Google STT / Whisper + Google Neural2 / ElevenLabs TTS + WebSockets Gateway (Role 2: Voice & Multilingual Specialist).

## Code Standards
- **Python**: Use strict type hints and Pydantic v2 schemas for all models. Follow PEP8 conventions.
- **TypeScript/React**: Avoid using `any`. Define explicit interfaces in `src/types/`.
- **Styling**: Use CSS custom properties defined in `index.css`. Maintain glassmorphism dark theme aesthetics.
- **Error Handling**: Never swallow errors silently. Return clear HTTP error statuses and log tracebacks.

## Workspace Task Allocation & Documents
- Complete Architecture Plan: `implementation_plan.md`
- 4-Role Task Matrix: `team_task_allocation.md`
- Onboarding Prompts: `teammate_prompts.md`
