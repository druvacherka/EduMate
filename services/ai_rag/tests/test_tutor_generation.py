from types import SimpleNamespace

import anyio
import pytest

from services.ai_rag.llm_client import GeminiLLMClient


class GeminiUnavailableError(Exception):
    code = 503


def test_generate_tutor_response_uses_fallback_when_primary_model_is_unavailable():
    attempted_models = []

    class Chats:
        def create(self, model, config, history):
            attempted_models.append(model)
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
        client.generate_tutor_response,
        "Be a tutor.",
        "Explain photosynthesis.",
    )

    assert response == "A generated tutor response."
    assert attempted_models == ["retired-primary", "working-fast-model"]


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
