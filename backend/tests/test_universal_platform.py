import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_curriculum_levels():
    response = client.get("/api/curriculum/levels")
    assert response.status_code == 200
    levels = response.json()
    assert len(levels) >= 5
    level_ids = [l["id"] for l in levels]
    assert "class_10" in level_ids
    assert "intermediate" in level_ids
    assert "btech" in level_ids
    assert "gate" in level_ids
    assert "govt_exams" in level_ids


def test_curriculum_hierarchy():
    response = client.get("/api/curriculum/hierarchy?level_id=class_10&stream=TG%20SSC%20Regular%20(All%20Subjects)")
    assert response.status_code == 200
    data = response.json()
    assert data["education_level"] == "class_10"
    assert len(data["subjects"]) >= 2
    subject_names = [s["subject"] for s in data["subjects"]]
    assert any("Mathematics" in s for s in subject_names)


def test_goals_lifecycle():
    # 1. List goals
    res = client.get("/api/goals")
    assert res.status_code == 200
    initial_goals = res.json()
    assert isinstance(initial_goals, list)

    # 2. Create goal
    new_goal = {
        "name": "GATE CSE 2028 Test",
        "goal_type": "exam",
        "target_exam": "GATE 2028",
        "target_date": "2028-02-10",
        "priority": "HIGH",
        "available_hours_per_day": 2.5,
        "current_level": "Beginner",
        "target_level": "Advanced"
    }
    create_res = client.post("/api/goals", json=new_goal)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["name"] == "GATE CSE 2028 Test"
    assert created["is_active"] is True
    goal_id = created["id"]

    # 3. Toggle goal
    tog_res = client.post(f"/api/goals/{goal_id}/toggle")
    assert tog_res.status_code == 200
    assert tog_res.json()["is_active"] is False

    # 4. Delete goal
    del_res = client.delete(f"/api/goals/{goal_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"


def test_daily_dashboard():
    response = client.get("/api/dashboard/daily")
    assert response.status_code == 200
    data = response.json()
    assert "greeting" in data
    assert "student_name" in data
    assert "today_tasks" in data
    assert len(data["today_tasks"]) >= 1

    # Test toggling task
    first_task = data["today_tasks"][0]
    task_id = first_task["id"]
    initial_status = first_task["is_completed"]

    tog_res = client.post(f"/api/dashboard/tasks/{task_id}/toggle")
    assert tog_res.status_code == 200
    assert tog_res.json()["is_completed"] != initial_status


def test_adaptive_planner():
    req = {
        "goal_name": "TG SSC 10/10 GPA (Board Exam 2027)",
        "target_date": "2027-03-01",
        "available_hours_per_day": 3.0,
        "current_level": "Beginner"
    }
    res = client.post("/api/planner/generate", json=req)
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert "weekly_breakdown" in data
    assert len(data["weekly_breakdown"]) >= 4
    assert data["total_hours_planned"] > 0


def test_recommendation_engine():
    res = client.get("/api/recommendations/next")
    assert res.status_code == 200
    rec = res.json()
    assert "recommended_action" in rec
    assert "topic" in rec
    assert "reason" in rec
    assert rec["estimated_minutes"] > 0


def test_spaced_revision():
    # 1. Fetch revision items
    res = client.get("/api/revision/items")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1

    # 2. Complete revision
    first_item = items[0]
    comp_res = client.post("/api/revision/complete", json={"item_id": first_item["id"], "score": 90.0})
    assert comp_res.status_code == 200
    updated = comp_res.json()
    assert updated["mastery_score"] == 90.0


def test_career_explorer():
    res = client.get("/api/career/paths")
    assert res.status_code == 200
    paths = res.json()
    assert len(paths) >= 4
    path_ids = [p["id"] for p in paths]
    assert "career-swe" in path_ids
    assert "career-upsc" in path_ids

    detail_res = client.get("/api/career/paths/career-swe")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["title"] == "Software Development Engineer (SDE)"
    assert len(detail["core_subjects"]) >= 3


def test_voice_session():
    voice_payload = {
        "language": "Telugu",
        "topic": "Binary Search Trees",
        "duration_seconds": 145,
        "transcript_summary": "Socratic dialogue on BST balancing and AVL rotations in Telugu."
    }
    res = client.post("/api/voice/session", json=voice_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "Telugu"
    assert data["duration_seconds"] == 145

    list_res = client.get("/api/voice/sessions")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_select_active_goal():
    res = client.post("/api/goals/tg-goal-polycet/select")
    assert res.status_code == 200
    assert res.json()["id"] == "tg-goal-polycet"
    assert res.json()["is_active"] is True

    dash = client.get("/api/dashboard/daily").json()
    assert any("POLYCET" in t["title"] for t in dash["today_tasks"])


def test_onboarding_flow():
    onboard_payload = {
        "name": "Arjun Sharma",
        "preferred_language": "English",
        "education_level": "Telangana State Board SSC (Class 10)",
        "institution": "Telangana State Model School",
        "stream_branch": "TG SSC (English & Telugu Medium)",
        "academic_year_semester": "10th Standard",
        "daily_study_hours": 2.5,
        "initial_goals": ["TG SSC 10/10 GPA (Board Exam 2027)", "TS POLYCET 2027"]
    }
    res = client.post("/api/onboarding", json=onboard_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["profile"]["name"] == "Arjun Sharma"
    assert "Telangana" in data["profile"]["education_level"]
    assert len(data["active_goals"]) >= 2


def test_onboarding_deduplication():
    # Calling onboarding again with identical goals should not duplicate them
    initial_goals_res = client.get("/api/goals")
    assert initial_goals_res.status_code == 200
    initial_count = len(initial_goals_res.json())

    payload = {
        "name": "Arjun Sharma",
        "preferred_language": "English",
        "education_level": "Telangana State Board SSC (Class 10)",
        "institution": "Telangana State Model School",
        "stream_branch": "TG SSC (English & Telugu Medium)",
        "academic_year_semester": "10th Standard",
        "daily_study_hours": 2.5,
        "initial_goals": ["TG SSC 10/10 GPA (Board Exam 2027)", "TS POLYCET 2027"]
    }
    res = client.post("/api/onboarding", json=payload)
    assert res.status_code == 200

    after_goals_res = client.get("/api/goals")
    assert after_goals_res.status_code == 200
    after_count = len(after_goals_res.json())
    # Count must remain the same because the goals already existed
    assert after_count == initial_count

