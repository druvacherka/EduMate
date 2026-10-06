import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

import backend.main as main
import backend.database as database
from backend.services.revision_engine import revision_engine
from backend.config import settings as backend_settings
from ai_rag.config import settings as rag_settings
from ai_rag.embeddings.gemini_embedder import gemini_embedder
from ai_rag.llm_client import llm_client


@pytest.fixture(scope="module")
def client():
    database_path = os.path.join(
        tempfile.gettempdir(),
        f"edumate-api-test-{uuid.uuid4().hex}.db",
    )
    patcher = pytest.MonkeyPatch()
    patcher.setattr(database, "DATABASE_URL", f"sqlite:///{database_path.replace(os.sep, '/')}")
    patcher.setattr(database, "IS_POSTGRES", False)
    patcher.setattr(database, "engine", None)
    patcher.setattr(
        backend_settings,
        "jwt_secret_key",
        "test-secret-key-long-enough-for-local-tests",
    )
    patcher.setattr(backend_settings, "gemini_api_key", "")
    patcher.setattr(rag_settings, "gemini_api_key", "")
    patcher.setattr(gemini_embedder, "_client", None)
    patcher.setattr(llm_client, "_client", None)

    async def generate_test_tutor_response(
        system_prompt,
        user_query,
        conversation_history=None,
        use_fast_model=False,
        generation_temperature=None,
    ):
        return "Test tutor response based on the submitted question."

    patcher.setattr(llm_client, "generate_tutor_response", generate_test_tutor_response)

    async def generate_test_document_answer(system_prompt, document_question_prompt):
        return "Test document answer [Doc: Test.pdf, Page 1]."

    patcher.setattr(llm_client, "generate_grounded_document_answer", generate_test_document_answer)

    async def generate_test_quiz(topic, num_questions, difficulty):
        return [
            {
                "id": f"q{index + 1}",
                "type": "mcq",
                "question": f"Test question {index + 1} about {topic}?",
                "options": ["Distractor A", "Correct test answer", "Distractor C", "Distractor D"],
                "correctAnswer": 1,
                "explanation": f"This is the test explanation for question {index + 1}.",
                "difficulty": difficulty,
                "topic": topic,
            }
            for index in range(num_questions)
        ]

    patcher.setattr(llm_client, "generate_structured_quiz", generate_test_quiz)

    async def generate_test_study_plan(**plan_inputs):
        return [
            {
                "week_number": week,
                "theme": f"{plan_inputs['goal_name']} learning focus {week}",
                "focus_topics": [
                    (plan_inputs["weak_areas"] or ["Goal fundamentals"])[0],
                    f"Practice topic {week}",
                ],
                "target_milestone": f"Complete and review week {week} practice.",
            }
            for week in range(1, plan_inputs["num_weeks"] + 1)
        ]

    patcher.setattr(llm_client, "generate_adaptive_study_plan", generate_test_study_plan)
    patcher.setattr(
        main.gemini_embedder,
        "embed_query",
        lambda text: main.gemini_embedder._generate_fallback_vector(text),
    )
    patcher.setattr(main.hybrid_search_engine, "search", lambda _query: [])

    with TestClient(main.app) as test_client:
        email = f"api-test-{uuid.uuid4().hex}@example.com"
        response = test_client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "ApiTestStrongPassword!2026",
            },
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        test_client.headers.update({"Authorization": f"Bearer {token}"})

        student_id = database.get_user_account_by_email(email)["student_id"]
        database.insert_student_goal(
            goal_id="tg-goal-polycet",
            name="TS POLYCET test goal",
            target_exam="TS POLYCET",
            student_id=student_id,
        )
        database.insert_daily_task(
            task_id="api-test-daily-task",
            title="Review test mathematics topic",
            subject="Mathematics",
            topic="Algebra",
            student_id=student_id,
        )
        revision_engine.add_topic_to_revision(
            subject="Mathematics",
            topic="Algebra",
            student_id=student_id,
        )
        yield test_client

    patcher.undo()
    if os.path.exists(database_path):
        os.remove(database_path)
