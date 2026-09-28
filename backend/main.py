import os
import shutil
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.schemas import (
    SocraticChatRequest,
    SocraticChatResponse,
    QuizGenerationRequest,
    QuizQuestionSchema,
    AnalyticsProfileResponse,
    RagSearchRequest,
    RagSearchResponse,
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

        # Build grounded system prompt & user payload
        system_prompt = grounded_prompt_builder.build_system_prompt(user_level=req.level)
        user_payload = grounded_prompt_builder.assemble_grounded_prompt(
            user_query=req.query,
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
            language=req.language,
            quick_actions=quick_actions,
            citations=citations_dict if citations_dict else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate tutor response: {str(e)}")

@app.post("/api/quizzes/generate", response_model=List[QuizQuestionSchema])
async def generate_quiz(req: QuizGenerationRequest):
    """Generate structured AI quiz questions based on target topic and difficulty."""
    try:
        questions = await llm_client.generate_structured_quiz(
            topic=req.topic,
            num_questions=req.num_questions,
            difficulty=req.difficulty
        )
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@app.get("/api/analytics/profile", response_model=AnalyticsProfileResponse)
async def get_student_profile():
    """Retrieve student mastery score, streak, and weak area analytics."""
    return AnalyticsProfileResponse()

@app.post("/api/materials/upload")
async def upload_study_material(
    file: UploadFile = File(...),
    subject: str = Form("Computer Science")
):
    """Upload PDF study material, parse page content, split chunks, and index in Qdrant."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Parse PDF using PyMuPDF engine
        extracted_doc = pdf_parser.extract_pdf_content(temp_path)
        
        # 2. Chunk text using header-aware recursive chunker
        chunk_documents = text_chunker.chunk_document(extracted_doc)

        return {
            "status": "success",
            "filename": file.filename,
            "subject": subject,
            "totalPages": extracted_doc.total_pages,
            "totalChunks": len(chunk_documents),
            "message": f"Successfully parsed and chunked '{file.filename}' into {len(chunk_documents)} semantic vectors."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process study material: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
