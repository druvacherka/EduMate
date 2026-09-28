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
    questions = response.json()
    assert isinstance(questions, list)
    assert len(questions) >= 1
    assert questions[0]["topic"] == "Binary Search Trees"

def test_analytics_profile_endpoint():
    response = client.get("/api/analytics/profile")
    assert response.status_code == 200
    data = response.json()
    assert "masteryScore" in data
    assert "weakAreas" in data
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

