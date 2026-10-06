from fastapi.testclient import TestClient

from backend.database import get_db_connection


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "EduMate" in data["app"]

def test_socratic_chat_endpoint(client: TestClient):
    payload = {
        "query": "What is binary search?",
        "level": "Beginner",
        "language": "English"
    }
    response = client.post("/api/chat/socratic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["level"] == "Beginner"
    assert data["language"] == "English"
    assert data["quick_actions"] == []
    assert data["response"] == "Test tutor response based on the submitted question."


def test_multilingual_chat_endpoint(client: TestClient):
    payload = {
        "query": "బైనరీ సెర్చ్ ట్రీ ఎలా పనిచేస్తుంది?",
        "level": "Intermediate",
        "language": "Telugu"
    }
    response = client.post("/api/chat/socratic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "Telugu"
    assert "response" in data


def test_quiz_generation_endpoint(client: TestClient):
    payload = {
        "topic": "Binary Search Trees",
        "num_questions": 2,
        "difficulty": "Medium"
    }
    response = client.post("/api/quizzes/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "questions" in data
    assert len(data["questions"]) == payload["num_questions"]
    assert data["topic"] == payload["topic"]
    assert data["difficulty"] == payload["difficulty"]
    assert all("correctAnswer" not in question for question in data["questions"])
    assert all("rubric_keywords" not in question for question in data["questions"])


def test_quiz_submit_endpoint(client: TestClient):
    # 1. Create a session
    gen_payload = {
        "topic": "Graph Algorithms",
        "num_questions": 2,
        "difficulty": "Medium"
    }
    gen_res = client.post("/api/quizzes/generate", json=gen_payload)
    assert gen_res.status_code == 200
    session_data = gen_res.json()
    session_id = session_data["session_id"]
    questions = session_data["questions"]

    # 2. Submit answers
    answers = {str(q["id"]): 1 for q in questions}
    sub_payload = {
        "session_id": session_id,
        "user_answers": answers
    }
    sub_res = client.post("/api/quizzes/submit", json=sub_payload)
    assert sub_res.status_code == 200
    result = sub_res.json()
    assert result["session_id"] == session_id
    assert result["status"] == "EVALUATED"
    assert result["score"] == len(questions)
    assert result["percentage"] == 100.0


def test_quiz_submission_increments_existing_weak_area(client: TestClient):
    topic = "Quiz regression existing weak area"

    for _ in range(2):
        quiz_response = client.post(
            "/api/quizzes/generate",
            json={"topic": topic, "num_questions": 2, "difficulty": "Medium"},
        )
        assert quiz_response.status_code == 200
        quiz = quiz_response.json()

        result = client.post(
            "/api/quizzes/submit",
            json={
                "session_id": quiz["session_id"],
                "user_answers": {question["id"]: 0 for question in quiz["questions"]},
            },
        )
        assert result.status_code == 200, result.text
        assert result.json()["mistakes_count"] == 2

    with get_db_connection() as conn:
        row = conn.cursor().execute(
            "SELECT mistake_count FROM weak_areas WHERE topic = ?;",
            (topic,),
        ).fetchone()

    assert row is not None
    assert row["mistake_count"] == 2


def test_study_materials_endpoint(client: TestClient):
    response = client.get("/api/materials")
    assert response.status_code == 200
    materials = response.json()
    assert isinstance(materials, list)


def test_update_profile_settings(client: TestClient):
    payload = {
        "level": "Advanced",
        "language": "Telugu",
        "current_topic": "AVL Trees"
    }
    response = client.put("/api/settings/profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["profile"]["level"] == "Advanced"
    assert data["profile"]["language"] == "Telugu"


def test_analytics_profile_endpoint(client: TestClient):
    response = client.get("/api/analytics/profile")
    assert response.status_code == 200
    data = response.json()
    assert "masteryScore" in data
    assert "weakAreas" in data
    assert "subjectProgress" in data
    assert isinstance(data["weakAreas"], list)
    assert isinstance(data["subjectProgress"], list)


def test_rag_search_endpoint(client: TestClient):
    payload = {
        "query_text": "Binary search algorithms",
        "top_k": 3
    }
    response = client.post("/api/rag/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Binary search algorithms"
    assert "couldn't find a relevant passage" in data["answer"]
    assert data["citations"] == []


def test_rag_search_returns_one_gemini_answer_grounded_in_retrieved_passages(
    client: TestClient,
    monkeypatch,
):
    from backend import main
    from ai_rag.schemas.vector_schemas import SearchResult

    captured = {}

    def capture_search(query):
        captured["search_query"] = query
        return [
            SearchResult(
                chunk_id="source-1",
                score=0.9,
                document_name="Notes.pdf",
                page_number=3,
                text_snippet="The division algorithm states a = bq + r, where 0 <= r < b.",
            ),
            SearchResult(
                chunk_id="source-2",
                score=0.8,
                document_name="Notes.pdf",
                page_number=4,
                text_snippet="The remainder is always less than the divisor.",
            ),
        ]

    async def generate_answer(system_prompt, document_question_prompt):
        captured["system_prompt"] = system_prompt
        captured["answer_prompt"] = document_question_prompt
        return "It states that a = bq + r with 0 <= r < b [Doc: Notes.pdf, Page 3]."

    monkeypatch.setattr(main.hybrid_search_engine, "search", capture_search)
    monkeypatch.setattr(main.llm_client, "generate_grounded_document_answer", generate_answer)
    monkeypatch.setattr(main.gemini_embedder, "embed_query", lambda _query: [0.1] * 768)

    response = client.post(
        "/api/rag/search",
        json={
            "query_text": "What does the division algorithm state?",
            "document_id": "selected-document",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"].startswith("It states that a = bq + r")
    assert len(data["citations"]) == 1
    assert data["citations"][0]["document_name"] == "Notes.pdf"
    assert data["citations"][0]["page_number"] == 3
    assert "results" not in data
    assert "What does the division algorithm state?" in captured["answer_prompt"]
    assert "The division algorithm states a = bq + r" in captured["answer_prompt"]
    assert captured["search_query"].document_id == "selected-document"
    assert captured["search_query"].top_k >= 2


def test_socratic_chat_uses_gemini_without_reading_rag_documents(client: TestClient, monkeypatch):
    from backend import main

    captured = {}

    def no_document_access(*_args, **_kwargs):
        raise AssertionError("Socratic tutor must not access RAG documents.")

    async def capture_tutor_response(system_prompt, user_query, conversation_history=None, **_kwargs):
        captured["system_prompt"] = system_prompt
        captured["user_query"] = user_query
        captured["history"] = conversation_history
        return "Let's reason through this together. What do you think the first step is?"

    monkeypatch.setattr(
        main.hybrid_search_engine, "search", no_document_access
    )
    monkeypatch.setattr(main.gemini_embedder, "embed_query", no_document_access)
    monkeypatch.setattr(main.llm_client, "generate_grounded_document_answer", no_document_access)
    monkeypatch.setattr(main.llm_client, "generate_tutor_response", capture_tutor_response)
    query = "How do I solve a quadratic equation?"
    response = client.post(
        "/api/chat/socratic",
        json={
            "query": query,
            "level": "Intermediate",
            "language": "English",
            "conversation_history": [
                {"sender": "student", "text": "I know about factoring."},
                {"sender": "tutor", "text": "Great, let's build on that."},
            ],
            "document_id": "must-be-ignored",
        },
    )

    assert response.status_code == 200
    assert captured["user_query"] == query
    assert captured["history"][0]["text"] == "I know about factoring."
    assert "Socratic tutor" in captured["system_prompt"]
    assert "Do not retrieve" in captured["system_prompt"]
    assert "INTERMEDIATE STUDENT" in captured["system_prompt"]
    assert response.json()["response"].startswith("Let's reason through")
    assert response.json()["citations"] is None
