from functools import partial
from types import SimpleNamespace

import anyio
import pytest

from ai_rag.llm_client import GeminiLLMClient


class GeminiUnavailableError(Exception):
    code = 503


def test_generate_tutor_response_uses_fallback_when_primary_model_is_unavailable():
    attempted_models = []
    generation_configurations = []

    class Chats:
        def create(self, model, config, history):
            attempted_models.append(model)
            generation_configurations.append(config)
            if model == "retired-primary":
                raise GeminiUnavailableError("model unavailable")
            return SimpleNamespace(
                send_message=lambda _message: SimpleNamespace(
                    text="A generated tutor response."
                )
            )

    client = GeminiLLMClient(api_key="test-key")
    client.default_model_name = "retired-primary"
    client.fast_model_name = "working-fast-model"
    client.quiz_fallback_model_names = ["working-fallback-model"]
    client._client = SimpleNamespace(chats=Chats())

    response = anyio.run(
        partial(
            client.generate_tutor_response,
            generation_temperature=0.1,
        ),
        "Be a tutor.",
        "Explain photosynthesis.",
    )

    assert response == "A generated tutor response."
    assert attempted_models == ["retired-primary", "working-fast-model"]
    assert generation_configurations[-1].temperature == 0.1


def test_generate_tutor_response_rejects_missing_gemini_client():
    client = GeminiLLMClient(api_key="test-key")
    client._client = None

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        anyio.run(
            client.generate_tutor_response,
            "Be a tutor.",
            "Explain photosynthesis.",
        )


def test_generate_tutor_response_rejects_empty_gemini_response():
    class Chats:
        def create(self, model, config, history):
            return SimpleNamespace(
                send_message=lambda _message: SimpleNamespace(text=" ")
            )

    client = GeminiLLMClient(api_key="test-key")
    client.default_model_name = "working-model"
    client.fast_model_name = "working-model"
    client.quiz_fallback_model_names = []
    client._client = SimpleNamespace(chats=Chats())

    with pytest.raises(RuntimeError, match="Gemini could not generate"):
        anyio.run(
            client.generate_tutor_response,
            "Be a tutor.",
            "Explain photosynthesis.",
        )


def test_document_answer_sends_source_passages_and_question_to_gemini():
    calls = []

    class Models:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                text="The source gives the answer as 42 [Doc: Source.pdf, Page 2]."
            )

    client = GeminiLLMClient(api_key="test-key")
    client.fast_model_name = "document-model"
    client.default_model_name = "document-model"
    client.quiz_fallback_model_names = []
    client._client = SimpleNamespace(models=Models())

    response = anyio.run(
        client.generate_grounded_document_answer,
        "Answer only from the retrieved document.",
        "SOURCE: The source gives the answer as 42.\n"
        "QUESTION: What answer does the source give?",
    )

    assert response.startswith("The source gives the answer as 42")
    assert calls[0]["model"] == "document-model"
    assert "The source gives the answer as 42." in calls[0]["contents"]
    assert "What answer does the source give?" in calls[0]["contents"]
    assert calls[0]["config"].system_instruction == "Answer only from the retrieved document."
    assert calls[0]["config"].temperature == 0.1


def test_document_answer_uses_fallback_model_on_rate_limit():
    attempted_models = []

    class Models:
        def generate_content(self, model, **_kwargs):
            attempted_models.append(model)
            if model == "busy-model":
                raise GeminiUnavailableError("rate limited")
            return SimpleNamespace(text="Answer from the source.")

    client = GeminiLLMClient(api_key="test-key")
    client.fast_model_name = "busy-model"
    client.default_model_name = "available-model"
    client.quiz_fallback_model_names = []
    client._client = SimpleNamespace(models=Models())

    response = anyio.run(
        client.generate_grounded_document_answer,
        "Grounded system instructions.",
        "Retrieved source and question.",
    )

    assert response == "Answer from the source."
    assert attempted_models == ["busy-model", "available-model"]


@pytest.mark.parametrize("mode", ["Beginner", "Intermediate", "Advanced"])
def test_generate_tutor_response_passes_pedagogical_mode_to_gemini(mode):
    captured_config = {}

    class Chats:
        def create(self, model, config, history):
            captured_config["config"] = config
            return SimpleNamespace(
                send_message=lambda _msg: SimpleNamespace(
                    text=f"Tutoring in {mode} mode."
                )
            )

    client = GeminiLLMClient(api_key="test-key")
    client.default_model_name = "test-model"
    client.fast_model_name = "test-model"
    client._client = SimpleNamespace(chats=Chats())

    res = anyio.run(
        client.generate_tutor_response,
        "You are EduMate AI tutor.",
        "How do arrays work?",
        None,
        False,
        None,
        mode,
    )

    assert res == f"Tutoring in {mode} mode."
    assert f"PEDAGOGICAL MODE: {mode.upper()}" in captured_config["config"].system_instruction

