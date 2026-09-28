import os
import shutil
import uuid
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.schemas import (
    SocraticChatRequest,
    SocraticChatResponse,
    QuizGenerationRequest,
    QuizQuestionSchema,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
    AnalyticsProfileResponse,
    RagSearchRequest,
    RagSearchResponse,
    StudyMaterialItem,
    UpdateProfileRequest,
)

# Import AI & RAG Engine Services
from services.ai_rag.prompts.level_builders import prompt_factory
from services.ai_rag.prompts.grounding_prompts import GroundedPromptBuilder
from services.ai_rag.validators.citation_validator import CitationValidator
from services.ai_rag.llm_client import llm_client
from services.ai_rag.document_processing.pdf_parser import pdf_parser
from services.ai_rag.document_processing.text_chunker import text_chunker
from services.ai_rag.vector_store.qdrant_client import qdrant_store
from services.ai_rag.vector_store.hybrid_search import HybridSearchEngine
from services.ai_rag.schemas.vector_schemas import HybridSearchQuery, SearchResult, SearchQuery
from services.ai_rag.embeddings import gemini_embedder

# Import Backend Database & Engine Services
from backend.database import (
    list_study_materials,
    insert_study_material,
    delete_study_material,
    update_student_settings,
)
from backend.services.quiz_engine import quiz_state_machine
from backend.services.analytics_engine import analytics_engine

from services.ai_rag.validators.language_detector import multilingual_detector
from services.ai_rag.prompts.multilingual_prompts import multilingual_prompt_factory

hybrid_search_engine = HybridSearchEngine(vector_store=qdrant_store)
grounded_prompt_builder = GroundedPromptBuilder()
citation_validator = CitationValidator()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="EduMate Multilingual AI Tutor Gateway & RAG Engine API"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """Service health check endpoint."""
    return {"status": "ok", "app": settings.app_name, "version": settings.version}

@app.post("/api/rag/search", response_model=RagSearchResponse)
async def perform_rag_search(req: RagSearchRequest):
    """Execute hybrid dense vector + BM25 keyword search over study material chunks."""
    try:
        # Generate query embedding vector
        query_vec = gemini_embedder.embed_query(req.query_text)

        search_query = HybridSearchQuery(
            query_text=req.query_text,
            query_vector=query_vec,
            top_k=req.top_k,
            subject_filter=req.subject,
            topic_filter=req.topic,
        )

        results = hybrid_search_engine.search(search_query)

        formatted_results = [
            {
                "chunk_id": res.chunk_id,
                "document_name": res.document_name,
                "page_number": res.page_number,
                "text_snippet": res.text_snippet,
                "section_title": res.section_title,
                "score": res.score,
                "dense_score": res.dense_score,
                "bm25_score": res.bm25_score,
                "rrf_score": res.rrf_score,
            }
            for res in results
        ]

        return RagSearchResponse(
            query=req.query_text,
            total_results=len(formatted_results),
            results=formatted_results,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hybrid search failed: {str(e)}")

@app.post("/api/chat/socratic", response_model=SocraticChatResponse)
async def generate_socratic_chat(req: SocraticChatRequest):
    """Generate Socratic tutor response tailored by student level, language, and RAG grounding."""
    try:
        context_chunks: List[SearchResult] = []

        # If RAG document retrieval requested or vector store populated
        if req.query:
            try:
                query_vec = gemini_embedder.embed_query(req.query)
                hybrid_q = HybridSearchQuery(
                    query_text=req.query,
                    query_vector=query_vec,
                    top_k=3,
                    score_threshold=0.3,
                )
                hybrid_res = hybrid_search_engine.search(hybrid_q)
                context_chunks = [
                    SearchResult(
                        chunk_id=r.chunk_id,
                        score=r.score,
                        document_name=r.document_name,
                        page_number=r.page_number,
                        text_snippet=r.text_snippet,
                        section_title=r.section_title,
                    )
                    for r in hybrid_res
                ]
            except Exception:
                context_chunks = []

        # Detect query language and align pedagogical persona
        detected_lang, _ = multilingual_detector.detect_language(req.query, fallback_language=req.language or "English")
        effective_lang = req.language if req.language in ("Hindi", "Telugu") else detected_lang

        # Build grounded system prompt & user payload
        if effective_lang in ("Hindi", "Telugu"):
            base_prompt = multilingual_prompt_factory.get_system_prompt(effective_lang, req.level)
            system_prompt = f"{base_prompt}\n\n{grounded_prompt_builder.build_system_prompt(user_level=req.level)}"
            enriched_query = multilingual_prompt_factory.prepare_multilingual_query(req.query, effective_lang)
        else:
            system_prompt = grounded_prompt_builder.build_system_prompt(user_level=req.level)
            enriched_query = req.query

        user_payload = grounded_prompt_builder.assemble_grounded_prompt(
            user_query=enriched_query,
            context_chunks=context_chunks,
            user_level=req.level,
        )

        # Query LLM
        raw_response_text = await llm_client.generate_tutor_response(
            system_prompt=system_prompt,
            user_query=user_payload,
            conversation_history=req.conversation_history,
        )

        # Validate grounding & extract citations
        validation_res = citation_validator.validate_and_format(
            llm_response=raw_response_text,
            context_chunks=context_chunks,
        )

        citations_dict = [
            {"document_name": c.document_name, "page_number": c.page_number, "raw_tag": c.raw_tag}
            for c in validation_res.parsed_citations
        ]

        quick_actions = [
            "Simplify explanation",
            "Give real-world analogy",
            "Show code example",
            "Test my understanding",
        ]

        return SocraticChatResponse(
            response=validation_res.formatted_response,
            level=req.level,
            language=effective_lang,
            quick_actions=quick_actions,
            citations=citations_dict if citations_dict else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate tutor response: {str(e)}")

# ==========================================
# Study Materials CRUD Endpoints
# ==========================================

@app.get("/api/materials", response_model=List[StudyMaterialItem])
async def get_study_materials():
    """Retrieve all uploaded and indexed PDF study materials from persistent SQLite DB."""
    try:
        materials = list_study_materials()
        return [
            StudyMaterialItem(
                id=m["id"],
                name=m["name"],
                subject=m["subject"],
                uploadDate=m["upload_date"],
                size=m["size_str"],
                pages=m["pages"],
                chunks=m["chunks"],
                status=m["status"],
            )
            for m in materials
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch materials: {str(e)}")

@app.post("/api/materials/upload")
async def upload_study_material(
    file: UploadFile = File(...),
    subject: str = Form("Computer Science"),
):
    """Upload PDF, extract content, chunk text, embed vectors, index in Qdrant, and save to DB."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        size_bytes = os.path.getsize(temp_path)
        size_str = f"{round(size_bytes / (1024 * 1024), 1)} MB" if size_bytes > 1024 * 1024 else f"{round(size_bytes / 1024, 1)} KB"

        # 1. Parse PDF using PyMuPDF engine
        extracted_doc = pdf_parser.extract_pdf_content(temp_path)

        # 2. Chunk text using recursive header-aware chunker
        chunk_documents = text_chunker.chunk_document(extracted_doc)

        # 3. Batch embed chunks using Gemini Embeddings
        embed_result = gemini_embedder.embed_chunks(chunk_documents.chunks)

        # 4. Upsert vectors into Qdrant collection
        if chunk_documents.chunks and embed_result.vectors:
            qdrant_store.upsert_chunks(
                chunks=chunk_documents.chunks,
                vectors=embed_result.vectors,
                document_name=file.filename,
                subject=subject,
            )

        # 5. Persist record in SQLite database
        doc_id = f"doc-{uuid.uuid4().hex[:6]}"
        saved_record = insert_study_material(
            doc_id=doc_id,
            name=file.filename,
            subject=subject,
            size_str=size_str,
            pages=extracted_doc.total_pages,
            chunks=len(chunk_documents.chunks),
            status="Ready",
        )

        return {
            "status": "success",
            "document": saved_record,
            "message": f"Successfully parsed, embedded, and indexed '{file.filename}'.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process study material: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.delete("/api/materials/{doc_id}")
async def remove_study_material(doc_id: str):
    """Delete study material record from database."""
    success = delete_study_material(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Study material not found.")
    return {"status": "success", "deleted_id": doc_id}

# ==========================================
# Quiz State Machine Endpoints
# ==========================================

@app.post("/api/quizzes/generate")
async def generate_quiz(req: QuizGenerationRequest):
    """Generate structured AI quiz questions and initialize a state machine session."""
    try:
        session = await quiz_state_machine.create_session(
            topic=req.topic,
            difficulty=req.difficulty,
            num_questions=req.num_questions,
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@app.post("/api/quizzes/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(req: QuizSubmissionRequest):
    """Submit student answers to Quiz State Machine, evaluate results, and update weak areas."""
    try:
        result = quiz_state_machine.evaluate_submission(
            session_id=req.session_id,
            user_answers=req.user_answers,
        )
        return QuizSubmissionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate quiz submission: {str(e)}")

# ==========================================
# Student Analytics & Settings Endpoints
# ==========================================

@app.get("/api/analytics/profile", response_model=AnalyticsProfileResponse)
async def get_student_profile_endpoint():
    """Retrieve dynamic student mastery score, streak, strong, and weak area analytics."""
    try:
        profile_data = analytics_engine.get_full_profile()
        return AnalyticsProfileResponse(**profile_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student analytics: {str(e)}")

@app.put("/api/settings/profile")
async def update_profile_settings(req: UpdateProfileRequest):
    """Update student learning settings (level, language, current subject/topic)."""
    try:
        updated = update_student_settings(
            level=req.level,
            language=req.language,
            current_subject=req.current_subject,
            current_topic=req.current_topic,
        )
        return {"status": "success", "profile": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile settings: {str(e)}")

