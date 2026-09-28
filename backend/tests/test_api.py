from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "EduMate" in data["app"]

def test_socratic_chat_endpoint():
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
    assert len(data["quick_actions"]) > 0

def test_quiz_generation_endpoint():
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
    assert len(data["questions"]) >= 1


def test_quiz_submit_endpoint():
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
    answers = {str(q["id"]): q.get("correctAnswer", 1) for q in questions}
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


def test_study_materials_endpoint():
    response = client.get("/api/materials")
    assert response.status_code == 200
    materials = response.json()
    assert isinstance(materials, list)
    assert len(materials) >= 1
    assert "name" in materials[0]
    assert "chunks" in materials[0]


def test_update_profile_settings():
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


def test_analytics_profile_endpoint():
    response = client.get("/api/analytics/profile")
    assert response.status_code == 200
    data = response.json()
    assert "masteryScore" in data
    assert "weakAreas" in data
    assert "subjectProgress" in data
    assert len(data["weakAreas"]) > 0


def test_rag_search_endpoint():
    payload = {
        "query_text": "Binary search algorithms",
        "top_k": 3
    }
    response = client.post("/api/rag/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Binary search algorithms"
    assert "total_results" in data
    assert isinstance(data["results"], list)


