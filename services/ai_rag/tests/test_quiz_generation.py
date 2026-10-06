import json
from types import SimpleNamespace

import anyio
import pytest

from services.ai_rag.llm_client import GeminiLLMClient


def make_mcq(index=1, topic="Cell biology", difficulty="Hard"):
    return {
        "id": f"generated-{index}",
        "type": "mcq",
        "question": f"Which statement about {topic} is correct, question {index}?",
        "options": ["First option", "Correct option", "Third option", "Fourth option"],
        "correctAnswer": "Correct option",
        "explanation": "The correct choice follows from the stated biological mechanism.",
        "difficulty": difficulty,
        "topic": topic,
    }


class FakeModels:
    def __init__(self, response_text):
        self.response_text = response_text
        self.call = None

    def generate_content(self, **kwargs):
        self.call = kwargs
        return SimpleNamespace(text=self.response_text)


class RetryableGeminiError(Exception):
    code = 503


def test_generate_structured_quiz_uses_user_topic_difficulty_and_count():
    topic = "Cell biology"
    models = FakeModels(json.dumps([make_mcq(1, topic), make_mcq(2, topic)]))
    client = GeminiLLMClient(api_key="test-key")
    client._client = SimpleNamespace(models=models)

    questions = anyio.run(
        client.generate_structured_quiz,
        topic,
        2,
        "Hard",
    )

    assert len(questions) == 2
    assert all(question["topic"] == topic for question in questions)
    assert all(question["difficulty"] == "Hard" for question in questions)
    assert [question["correctAnswer"] for question in questions] == [1, 1]
    assert "exactly 2" in models.call["contents"]
    assert "Hard difficulty" in models.call["contents"]


def test_generate_structured_quiz_uses_fallback_model_when_primary_is_unavailable():
    calls = []

    class ModelsWithFallback:
        def generate_content(self, **kwargs):
            calls.append(kwargs["model"])
            if kwargs["model"] == "gemini-primary":
                raise RetryableGeminiError("temporarily unavailable")
            return SimpleNamespace(text=json.dumps([make_mcq()]))

    client = GeminiLLMClient(api_key="test-key")
    client.fast_model_name = "gemini-primary"
    client.quiz_fallback_model_names = ["gemini-fallback"]
    client._client = SimpleNamespace(models=ModelsWithFallback())

    questions = anyio.run(
        client.generate_structured_quiz,
        "Cell biology",
        1,
        "Hard",
    )

    assert calls == ["gemini-primary", "gemini-fallback"]
    assert len(questions) == 1


def test_generate_structured_quiz_rejects_missing_gemini_client():
    client = GeminiLLMClient()
    client._client = None

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        anyio.run(client.generate_structured_quiz, "Cell biology", 2, "Easy")


def test_generate_structured_quiz_rejects_incomplete_gemini_response():
    models = FakeModels(json.dumps([make_mcq()]))
    client = GeminiLLMClient(api_key="test-key")
    client._client = SimpleNamespace(models=models)

    with pytest.raises(RuntimeError, match="valid quiz"):
        anyio.run(client.generate_structured_quiz, "Cell biology", 2, "Hard")
