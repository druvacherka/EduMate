import json
from functools import partial
from types import SimpleNamespace

import anyio
import pytest

from services.ai_rag.llm_client import GeminiLLMClient


def make_plan(weeks=2):
    return {
        "weekly_breakdown": [
            {
                "week_number": week,
                "theme": f"Focused learning theme {week}",
                "focus_topics": [f"Specific goal topic {week}"],
                "target_milestone": f"Complete week {week} practice and review.",
            }
            for week in range(1, weeks + 1)
        ]
    }


class FakeModels:
    def __init__(self, response_text):
        self.response_text = response_text
        self.call = None

    def generate_content(self, **kwargs):
        self.call = kwargs
        return SimpleNamespace(text=self.response_text)


def test_generate_adaptive_study_plan_includes_learner_inputs():
    models = FakeModels(json.dumps(make_plan()))
    client = GeminiLLMClient(api_key="test-key")
    client._client = SimpleNamespace(models=models)

    weeks = anyio.run(partial(
        client.generate_adaptive_study_plan,
        goal_name="Engineering entrance",
        target_date="2027-03-01",
        available_hours_per_day=3.5,
        current_level="Beginner",
        target_level="Advanced",
        education_level="B.Tech",
        subject="Mathematics",
        weak_areas=["Linear algebra"],
        mastery_score=42.5,
        num_weeks=2,
    ))

    prompt = models.call["contents"]
    assert len(weeks) == 2
    assert "Engineering entrance" in prompt
    assert "3.5" in prompt
    assert "Linear algebra" in prompt
    assert "Mathematics" in prompt
    assert "exactly the requested number of weeks" in prompt


def test_generate_adaptive_study_plan_uses_fallback_when_model_is_unavailable():
    calls = []

    class UnavailableError(Exception):
        code = 503

    class ModelsWithFallback:
        def generate_content(self, **kwargs):
            calls.append(kwargs["model"])
            if kwargs["model"] == "primary-model":
                raise UnavailableError("temporarily unavailable")
            return SimpleNamespace(text=json.dumps(make_plan(weeks=1)))

    client = GeminiLLMClient(api_key="test-key")
    client.fast_model_name = "primary-model"
    client.quiz_fallback_model_names = ["fallback-model"]
    client._client = SimpleNamespace(models=ModelsWithFallback())

    weeks = anyio.run(partial(
        client.generate_adaptive_study_plan,
        goal_name="Calculus",
        target_date=None,
        available_hours_per_day=2,
        current_level="Beginner",
        target_level="Advanced",
        education_level="",
        subject="Mathematics",
        weak_areas=[],
        mastery_score=0,
        num_weeks=1,
    ))

    assert calls == ["primary-model", "fallback-model"]
    assert len(weeks) == 1


def test_generate_adaptive_study_plan_rejects_missing_gemini_client():
    client = GeminiLLMClient(api_key="test-key")
    client._client = None

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        anyio.run(partial(
            client.generate_adaptive_study_plan,
            goal_name="Calculus",
            target_date=None,
            available_hours_per_day=2,
            current_level="Beginner",
            target_level="Advanced",
            education_level="",
            subject="Mathematics",
            weak_areas=[],
            mastery_score=0,
            num_weeks=1,
        ))


def test_generate_adaptive_study_plan_rejects_invalid_gemini_shape():
    models = FakeModels(json.dumps({"weekly_breakdown": []}))
    client = GeminiLLMClient(api_key="test-key")
    client._client = SimpleNamespace(models=models)

    with pytest.raises(RuntimeError, match="invalid adaptive study plan"):
        anyio.run(partial(
            client.generate_adaptive_study_plan,
            goal_name="Calculus",
            target_date=None,
            available_hours_per_day=2,
            current_level="Beginner",
            target_level="Advanced",
            education_level="",
            subject="Mathematics",
            weak_areas=[],
            mastery_score=0,
            num_weeks=1,
        ))
