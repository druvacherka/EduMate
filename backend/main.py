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
    StudentGoalSchema,
    CreateGoalRequest,
    DailyTaskSchema,
    DailyDashboardResponse,
    StudyPlanSchema,
    GeneratePlanRequest,
    CurriculumLevelSchema,
    CurriculumHierarchyResponse,
    RevisionItemSchema,
    CompleteRevisionRequest,
    CareerPathSchema,
    VoiceSessionCreateRequest,
    VoiceSessionResponse,
    OnboardingRequest,
    OnboardingResponse,
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
    get_student_profile,
)
from backend.services.quiz_engine import quiz_state_machine
from backend.services.analytics_engine import analytics_engine
from backend.services.goals_engine import goals_engine
from backend.services.planner_engine import planner_engine
from backend.services.curriculum_engine import curriculum_engine
from backend.services.recommendation_engine import recommendation_engine
from backend.services.revision_engine import revision_engine
from backend.services.career_engine import career_engine
from backend.services.context_builder import context_builder
from backend.services.voice_engine import voice_engine

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

        # Dynamically inject scoped student pedagogical context (Education Level, Active Goal, Weak Areas)
        tutor_ctx = context_builder.build_tutor_context(student_id=1)
        ctx_prompt_slice = context_builder.format_tutor_context_prompt(tutor_ctx)
        system_prompt = f"{ctx_prompt_slice}\n\n{system_prompt}"

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
    subject: str = Form("General"),
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
    """Update student learning settings and return updated profile."""
    try:
        updated = update_student_settings(
            level=req.level,
            language=req.language,
            current_subject=req.current_subject,
            current_topic=req.current_topic,
            name=req.name,
            education_level=req.education_level,
            institution=req.institution,
            stream_branch=req.stream_branch,
            academic_year_semester=req.academic_year_semester,
            daily_study_hours=req.daily_study_hours,
            onboarding_completed=req.onboarding_completed,
        )
        return {"status": "success", "profile": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile settings: {str(e)}")


# ==========================================
# Student Goals Management Endpoints
# ==========================================

@app.get("/api/goals", response_model=List[StudentGoalSchema])
async def get_student_goals():
    """Retrieve all active and target goals for the student."""
    try:
        return goals_engine.get_goals(student_id=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch goals: {str(e)}")


@app.post("/api/goals", response_model=StudentGoalSchema)
async def create_new_goal(req: CreateGoalRequest):
    """Create a new simultaneous goal (academic, exam, career, skill)."""
    try:
        return goals_engine.create_goal(req=req, student_id=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create goal: {str(e)}")


@app.delete("/api/goals/{goal_id}")
async def remove_student_goal(goal_id: str):
    """Delete a student goal."""
    success = goals_engine.delete_goal(goal_id=goal_id, student_id=1)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return {"status": "success", "deleted_id": goal_id}


@app.post("/api/goals/{goal_id}/toggle", response_model=StudentGoalSchema)
async def toggle_goal_active_status(goal_id: str):
    """Toggle a goal active or inactive."""
    updated = goals_engine.toggle_goal(goal_id=goal_id, student_id=1)
    if not updated:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return updated


@app.post("/api/goals/{goal_id}/select", response_model=StudentGoalSchema)
async def set_active_goal_selection(goal_id: str):
    """Set the primary active goal, dynamically recalculating tasks and focus for that goal."""
    updated = goals_engine.select_goal(goal_id=goal_id, student_id=1)
    if not updated:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return updated


# ==========================================
# Daily Study Dashboard & Tasks Endpoints
# ==========================================

@app.get("/api/dashboard/daily", response_model=DailyDashboardResponse)
async def get_daily_study_dashboard():
    """Retrieve personalized daily study dashboard with greeting, tasks, and streaks."""
    try:
        return planner_engine.get_daily_dashboard(student_id=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate daily dashboard: {str(e)}")


@app.post("/api/dashboard/tasks/{task_id}/toggle", response_model=DailyTaskSchema)
async def toggle_study_task_status(task_id: str):
    """Toggle completion status of a daily learning task."""
    updated = planner_engine.toggle_task(task_id=task_id, student_id=1)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found.")
    return updated


# ==========================================
# Adaptive Study Planner Endpoints
# ==========================================

@app.post("/api/planner/generate", response_model=StudyPlanSchema)
async def generate_adaptive_study_plan(req: GeneratePlanRequest):
    """Generate dynamic multi-week adaptive roadmap based on active goal and deadline."""
    try:
        return planner_engine.generate_adaptive_plan(req=req, student_id=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate study plan: {str(e)}")


# ==========================================
# Unified Curriculum & Hierarchy Endpoints
# ==========================================

@app.get("/api/curriculum/levels", response_model=List[CurriculumLevelSchema])
async def get_all_education_levels():
    """List universal education tiers (Class 10, Intermediate, B.Tech, GATE, Govt, etc.)."""
    return curriculum_engine.get_education_levels()


@app.get("/api/curriculum/hierarchy", response_model=CurriculumHierarchyResponse)
async def get_curriculum_hierarchy(level_id: str = "btech", stream: str = "Computer Science & Engineering"):
    """Retrieve subject -> chapter -> topic hierarchy for given level and stream."""
    try:
        subjects = curriculum_engine.get_subjects_hierarchy(level_id=level_id, stream=stream)
        return CurriculumHierarchyResponse(
            education_level=level_id,
            stream=stream,
            subjects=subjects,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch curriculum hierarchy: {str(e)}")


# ==========================================
# Adaptive Recommendation Engine Endpoints
# ==========================================

@app.get("/api/recommendations/next")
async def get_next_learning_action():
    """Compute deterministic Next Best Learning Action based on retention and mastery."""
    try:
        return recommendation_engine.get_next_recommendation(student_id=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate recommendation: {str(e)}")


# ==========================================
# Spaced Revision Schedule Endpoints
# ==========================================

@app.get("/api/revision/items", response_model=List[RevisionItemSchema])
async def get_spaced_revision_items(due_only: bool = False):
    """Retrieve spaced repetition review items."""
    try:
        return revision_engine.get_revision_items(student_id=1, due_only=due_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch revision items: {str(e)}")


@app.post("/api/revision/complete", response_model=RevisionItemSchema)
async def complete_spaced_revision_session(req: CompleteRevisionRequest):
    """Record revision completion and recalibrate interval."""
    updated = revision_engine.complete_revision(req=req, student_id=1)
    if not updated:
        raise HTTPException(status_code=404, detail="Revision item not found.")
    return updated


# ==========================================
# Career Explorer Endpoints
# ==========================================

@app.get("/api/career/paths", response_model=List[CareerPathSchema])
async def get_all_career_pathways():
    """Retrieve factual blueprints of engineering, public service, and academic career paths."""
    return career_engine.list_paths()


@app.get("/api/career/paths/{path_id}", response_model=CareerPathSchema)
async def get_career_pathway_detail(path_id: str):
    """Retrieve detailed roadmap and requirements for a specific career."""
    path_data = career_engine.get_path_detail(path_id)
    if not path_data:
        raise HTTPException(status_code=404, detail="Career pathway not found.")
    return path_data


# ==========================================
# Voice Tutoring Session Endpoints
# ==========================================

@app.post("/api/voice/session", response_model=VoiceSessionResponse)
async def log_voice_interaction(req: VoiceSessionCreateRequest):
    """Log metadata of a voice tutoring conversation session."""
    try:
        return voice_engine.log_session(req=req, student_id=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log voice session: {str(e)}")


@app.get("/api/voice/sessions")
async def list_past_voice_interactions():
    """Retrieve recent voice sessions."""
    try:
        return voice_engine.get_recent_sessions(student_id=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve voice sessions: {str(e)}")


# ==========================================
# Student Onboarding Flow Endpoint
# ==========================================

@app.post("/api/onboarding", response_model=OnboardingResponse)
async def complete_student_onboarding(req: OnboardingRequest):
    """Process student onboarding flow and configure personalized goals."""
    try:
        # 1. Update Profile
        updated_profile = update_student_settings(
            name=req.name,
            language=req.preferred_language,
            education_level=req.education_level,
            institution=req.institution or "",
            stream_branch=req.stream_branch,
            academic_year_semester=req.academic_year_semester or "",
            daily_study_hours=req.daily_study_hours,
            onboarding_completed=1,
        )

        # 2. Add requested initial goals if provided (deduplicating by name)
        existing_goals = goals_engine.get_goals(student_id=1)
        existing_goal_names = {g.name.strip().lower() for g in existing_goals}
        for goal_title in req.initial_goals:
            if goal_title.strip().lower() not in existing_goal_names:
                goals_engine.create_goal(
                    req=CreateGoalRequest(
                        name=goal_title,
                        goal_type="academic",
                        priority="HIGH",
                        available_hours_per_day=round(req.daily_study_hours / max(1, len(req.initial_goals)), 1),
                        current_level="Beginner",
                        target_level="Advanced",
                    ),
                    student_id=1,
                )

        active_goals = goals_engine.get_goals(student_id=1)

        return OnboardingResponse(
            status="success",
            message=f"Welcome {req.name}! Your {req.education_level} learning path has been personalized.",
            profile=updated_profile,
            active_goals=active_goals,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete onboarding: {str(e)}")


