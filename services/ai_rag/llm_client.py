import logging
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types

from services.ai_rag.config import settings
from services.ai_rag.schemas.quiz_schemas import QuizQuestionModel
from services.ai_rag.schemas.study_plan_schemas import GeneratedStudyPlan
from services.ai_rag.validators.json_repair import json_repair_middleware

logger = logging.getLogger(__name__)


class GeminiLLMClient:
    """Google Gemini 2.x LLM Client Wrapper for EduMate Tutor Engine.

    Uses the google.genai SDK (v2+) with a Client-based API.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.default_model_name = settings.default_model
        self.fast_model_name = settings.fast_model
        self.quiz_fallback_model_names = [
            model_name.strip()
            for model_name in settings.quiz_fallback_models.split(",")
            if model_name.strip()
        ]
        self._client: Optional[genai.Client] = None

        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Google Gemini SDK (google.genai) successfully configured with API Key.")
            except Exception as e:
                logger.exception("Failed to configure Gemini SDK.")

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    async def generate_tutor_response(
        self,
        system_prompt: str,
        user_query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_fast_model: bool = False,
    ) -> str:
        """Generate a tutor response with Gemini; never substitute simulated content."""
        if self._client is None:
            raise RuntimeError("Socratic tutoring requires a configured GEMINI_API_KEY.")

        chat_history: List[types.Content] = []
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg.get("sender") == "student" else "model"
                chat_history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg.get("text", ""))],
                    )
                )

        preferred_model = self.fast_model_name if use_fast_model else self.default_model_name
        model_names = list(dict.fromkeys(
            (preferred_model, self.fast_model_name, *self.quiz_fallback_model_names)
        ))
        fallback_statuses = (404, 429, 500, 502, 503, 504)

        for model_index, model_name in enumerate(model_names):
            try:
                chat = self._client.chats.create(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=settings.temperature,
                        max_output_tokens=settings.max_output_tokens,
                    ),
                    history=chat_history,
                )
                response = chat.send_message(user_query)
                response_text = (response.text or "").strip()
                if not response_text:
                    raise RuntimeError("Gemini returned an empty tutor response.")
                return response_text
            except Exception as exc:
                status_code = getattr(exc, "code", None) or getattr(
                    exc, "status_code", None
                )
                if status_code not in fallback_statuses or model_index == len(model_names) - 1:
                    logger.exception("Gemini tutor response generation failed.")
                    raise RuntimeError(
                        "Gemini could not generate a tutor response. Check API access and try again."
                    ) from exc
                logger.warning(
                    "Gemini tutor model %s unavailable (HTTP %s); trying the next configured model.",
                    model_name,
                    status_code,
                )

        raise RuntimeError("Gemini could not generate a tutor response.")

    async def generate_structured_quiz(
        self,
        topic: str,
        num_questions: int = 3,
        difficulty: str = "Medium",
    ) -> List[Dict[str, Any]]:
        """Generate and validate a quiz using Gemini; never substitute hardcoded questions."""
        if self._client is None:
            raise RuntimeError("Gemini quiz generation requires a configured GEMINI_API_KEY.")

        prompt = (
            f"Create exactly {num_questions} original quiz questions about {topic!r}. "
            f"Every question must be {difficulty} difficulty.\n"
            "Return only a JSON array. Each item must have: id, type, question, options, "
            "correctAnswer, explanation, difficulty, topic, rubric_keywords.\n"
            "Use type 'mcq', 'tf', or 'short'. For mcq, provide 4 distinct options and "
            "set correctAnswer to the zero-based integer index of the correct option. "
            "For tf, options must be [\"True\", \"False\"] and correctAnswer must be 0 "
            "for True or 1 for False. For short, correctAnswer must be a concise reference "
            "answer string and rubric_keywords must list key concepts required in a good "
            "answer. Explanations must justify the correct answer. Questions must genuinely "
            "test the requested topic and difficulty."
        )
        try:
            response = None
            model_names = list(dict.fromkeys(
                (self.fast_model_name, *self.quiz_fallback_model_names)
            ))
            fallback_statuses = (404, 429, 500, 502, 503, 504)
            for model_index, model_name in enumerate(model_names):
                try:
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        ),
                    )
                    break
                except Exception as exc:
                    status_code = getattr(exc, "code", None) or getattr(
                        exc, "status_code", None
                    )
                    if status_code not in fallback_statuses or model_index == len(model_names) - 1:
                        raise
                    logger.warning(
                        "Gemini quiz model %s unavailable (HTTP %s); "
                        "trying the next configured model.",
                        model_name,
                        status_code,
                    )

            if response is None:
                raise RuntimeError("Gemini quiz generation failed for all configured models.")

            generated_items = json_repair_middleware.repair_and_parse(response.text or "")
            if len(generated_items) != num_questions:
                raise ValueError(
                    f"Gemini returned {len(generated_items)} questions; expected {num_questions}."
                )

            questions = []
            for index, item in enumerate(generated_items):
                if not isinstance(item, dict):
                    raise ValueError(f"Generated question {index + 1} is not an object.")
                item = dict(item)
                question_type = item.get("type")
                if question_type == "tf":
                    item["options"] = ["True", "False"]
                    answer = item.get("correctAnswer", item.get("correct_answer"))
                    if isinstance(answer, bool):
                        item["correctAnswer"] = 0 if answer else 1
                    elif isinstance(answer, str) and answer.strip().lower() in ("true", "false"):
                        item["correctAnswer"] = 0 if answer.strip().lower() == "true" else 1
                elif question_type == "mcq":
                    options = item.get("options")
                    answer = item.get("correctAnswer", item.get("correct_answer"))
                    if isinstance(options, list) and isinstance(answer, str):
                        matches = [
                            option_index
                            for option_index, option in enumerate(options)
                            if isinstance(option, str)
                            and option.strip().casefold() == answer.strip().casefold()
                        ]
                        if len(matches) == 1:
                            item["correctAnswer"] = matches[0]
                        elif answer.strip().isdigit():
                            item["correctAnswer"] = int(answer.strip())
                        elif len(answer.strip()) == 1 and answer.strip().upper() in "ABCD":
                            item["correctAnswer"] = ord(answer.strip().upper()) - ord("A")

                item["id"] = f"q{index + 1}"
                item["topic"] = topic
                item["difficulty"] = difficulty
                validated = QuizQuestionModel.model_validate(item)
                question = validated.model_dump(by_alias=True, exclude_none=True)

                options = question.get("options")
                answer = question["correctAnswer"]
                if question["type"] == "mcq":
                    if (
                        not isinstance(options, list)
                        or len(options) != 4
                        or any(not isinstance(option, str) or not option.strip() for option in options)
                        or len({option.strip().casefold() for option in options}) != 4
                        or isinstance(answer, bool)
                        or not isinstance(answer, int)
                        or not 0 <= answer < len(options)
                    ):
                        raise ValueError(f"Generated multiple-choice question {index + 1} is invalid.")
                elif question["type"] == "tf":
                    if isinstance(answer, str) and answer.strip() in ("0", "1"):
                        answer = int(answer.strip())
                    if isinstance(answer, bool) or not isinstance(answer, int) or answer not in (0, 1):
                        raise ValueError(f"Generated true/false question {index + 1} has an invalid answer.")
                    question["correctAnswer"] = answer
                elif question["type"] == "short":
                    keywords = question.get("rubric_keywords")
                    if (
                        not isinstance(answer, str)
                        or not answer.strip()
                        or not isinstance(keywords, list)
                        or not keywords
                        or any(not isinstance(keyword, str) or not keyword.strip() for keyword in keywords)
                    ):
                        raise ValueError(f"Generated short-answer question {index + 1} is invalid.")

                questions.append(question)

            if len({question["question"].strip().casefold() for question in questions}) != num_questions:
                raise ValueError("Gemini returned duplicate quiz questions.")
            return questions
        except Exception as exc:
            logger.exception("Gemini structured quiz generation failed.")
            raise RuntimeError("Gemini could not generate a valid quiz. Please try again.") from exc

    async def generate_adaptive_study_plan(
        self,
        *,
        goal_name: str,
        target_date: Optional[str],
        available_hours_per_day: float,
        current_level: str,
        target_level: str,
        education_level: str,
        subject: str,
        weak_areas: List[str],
        mastery_score: float,
        num_weeks: int,
    ) -> List[Dict[str, Any]]:
        """Generate week themes and study focus using Gemini, without sample plans."""
        if self._client is None:
            raise RuntimeError("Adaptive plan generation requires a configured GEMINI_API_KEY.")

        prompt = (
            "Create an adaptive study plan using only the learner and goal details below. "
            "Return one JSON object with a weekly_breakdown array. Each array item must have "
            "week_number (1-based), theme, focus_topics (1 to 5 specific topics), and "
            "target_milestone. Generate exactly the requested number of weeks. Make the plan "
            "progressive, specific to the target goal and subject, and prioritize the learner's "
            "weak areas. Do not use generic placeholder themes or repeat topics.\n\n"
            f"Goal: {goal_name}\n"
            f"Target date: {target_date or 'Not specified'}\n"
            f"Available hours per day: {available_hours_per_day}\n"
            f"Current level: {current_level}\n"
            f"Target level: {target_level}\n"
            f"Education level: {education_level or 'Not specified'}\n"
            f"Subject: {subject or 'Not specified'}\n"
            f"Mastery score: {mastery_score}\n"
            f"Weak areas to prioritize: {', '.join(weak_areas) if weak_areas else 'No recorded weak areas'}\n"
            f"Number of weeks: {num_weeks}\n"
            "JSON shape: {\"weekly_breakdown\":[{\"week_number\":1,\"theme\":\"...\","
            "\"focus_topics\":[\"...\"],\"target_milestone\":\"...\"}]}"
        )

        model_names = list(dict.fromkeys(
            (self.fast_model_name, *self.quiz_fallback_model_names)
        ))
        fallback_statuses = (404, 429, 500, 502, 503, 504)
        response = None

        for model_index, model_name in enumerate(model_names):
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                break
            except Exception as exc:
                status_code = getattr(exc, "code", None) or getattr(
                    exc, "status_code", None
                )
                if status_code not in fallback_statuses or model_index == len(model_names) - 1:
                    logger.exception("Gemini adaptive study plan generation failed.")
                    raise RuntimeError(
                        "Gemini could not generate an adaptive study plan. Check API access and try again."
                    ) from exc
                logger.warning(
                    "Gemini plan model %s unavailable (HTTP %s); trying the next configured model.",
                    model_name,
                    status_code,
                )

        if response is None or not response.text:
            raise RuntimeError("Gemini returned an empty adaptive study plan.")

        try:
            parsed = json_repair_middleware.repair_and_parse(response.text)
            if len(parsed) != 1:
                raise ValueError("Gemini must return one plan object.")
            return GeneratedStudyPlan.model_validate(parsed[0]).model_dump()["weekly_breakdown"]
        except Exception as exc:
            logger.exception("Gemini returned an invalid adaptive study plan.")
            raise RuntimeError(
                "Gemini returned an invalid adaptive study plan. Please recalculate."
            ) from exc

llm_client = GeminiLLMClient()
