import os
import tempfile
import uuid

from fastapi.testclient import TestClient

import backend.database as database
from backend.config import settings
from backend.main import app


def test_accounts_are_authenticated_and_data_isolated(monkeypatch):
    database_path = os.path.join(
        tempfile.gettempdir(),
        f"edumate-test-{uuid.uuid4().hex}.db",
    )
    monkeypatch.setattr(database, "DATABASE_URL", f"sqlite:///{database_path.replace(os.sep, '/')}")
    monkeypatch.setattr(database, "IS_POSTGRES", False)
    monkeypatch.setattr(settings, "jwt_secret_key", "test-secret-key-long-enough-for-local-tests")

    try:
        with TestClient(app) as client:
            assert client.get("/api/goals").status_code == 401

            first = client.post(
                "/api/auth/register",
                json={"email": "first@example.com", "password": "FirstStrongPassword!2026"},
            )
            second = client.post(
                "/api/auth/register",
                json={"email": "second@example.com", "password": "SecondStrongPassword!2026"},
            )
            assert first.status_code == 200
            assert second.status_code == 200
            login = client.post(
                "/api/auth/login",
                json={"email": "first@example.com", "password": "FirstStrongPassword!2026"},
            )
            assert login.status_code == 200
            assert "password_hash" not in login.json()["user"]
            invalid_login = client.post(
                "/api/auth/login",
                json={"email": "first@example.com", "password": "IncorrectPassword!2026"},
            )
            assert invalid_login.status_code == 401

            first_headers = {"Authorization": f"Bearer {first.json()['access_token']}"}
            second_headers = {"Authorization": f"Bearer {second.json()['access_token']}"}
            saved = client.put(
                "/api/settings/profile",
                headers=first_headers,
                json={"name": "First learner", "current_topic": "Fractions"},
            )
            assert saved.status_code == 200

            first_profile = client.get("/api/analytics/profile", headers=first_headers).json()
            second_profile = client.get("/api/analytics/profile", headers=second_headers).json()
            assert first_profile["name"] == "First learner"
            assert first_profile["currentTopic"] == "Fractions"
            assert second_profile["name"] == ""
            assert second_profile["currentTopic"] == ""

            first_id = database.get_user_account_by_email("first@example.com")["student_id"]
            second_id = database.get_user_account_by_email("second@example.com")["student_id"]
            database.insert_student_goal("first-goal", "First goal", student_id=first_id)
            assert [goal["id"] for goal in database.list_student_goals(first_id)] == ["first-goal"]
            assert database.list_student_goals(second_id) == []
    finally:
        if os.path.exists(database_path):
            os.remove(database_path)
