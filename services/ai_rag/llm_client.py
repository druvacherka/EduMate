import os
import json
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from services.ai_rag.config import settings

logger = logging.getLogger(__name__)

class GeminiLLMClient:
    """Google Gemini 1.5 Pro/Flash LLM Client Wrapper for EduMate Tutor Engine."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.default_model_name = settings.default_model
        self.fast_model_name = settings.fast_model
        self._is_configured = False

        if self.api_key and self.api_key != "demo_gemini_key":
            try:
                genai.configure(api_key=self.api_key)
                self._is_configured = True
                logger.info("Google Gemini SDK successfully configured with API Key.")
            except Exception as e:
                logger.warning(f"Failed to configure Gemini SDK: {e}. Falling back to simulation mode.")

    async def generate_tutor_response(
        self, 
        system_prompt: str, 
        user_query: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_fast_model: bool = False
    ) -> str:
        """Generate pedagogical tutor response using Gemini 1.5 Pro or Flash."""
        model_name = self.fast_model_name if use_fast_model else self.default_model_name
        
        logger.info(f"Generating LLM response using model={model_name} (configured={self._is_configured})")

        if self._is_configured:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt
                )
                
                # Format conversation history if available
                chat_history = []
                if conversation_history:
                    for msg in conversation_history:
                        role = "user" if msg.get("sender") == "student" else "model"
                        chat_history.append({"role": role, "parts": [msg.get("text", "")]})

                chat = model.start_chat(history=chat_history)
                response = chat.send_message(
                    user_query,
                    generation_config=genai.types.GenerationConfig(
                        temperature=settings.temperature,
                        max_output_tokens=settings.max_output_tokens,
                    )
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Falling back to simulation mode.")

        # Fallback simulation response for offline / baseline testing
        return self._simulate_socratic_response(user_query)

    async def generate_structured_quiz(
        self,
        topic: str,
        num_questions: int = 3,
        difficulty: str = "Medium"
    ) -> List[Dict[str, Any]]:
        """Generate structured quiz JSON for MCQs, True/False, and Short Answer questions."""
        prompt = (
            f"Generate a {difficulty} difficulty quiz on '{topic}' with {num_questions} questions.\n"
            "Return ONLY a JSON array of objects with keys:\n"
            "- id: string\n"
            "- type: 'mcq' | 'tf' | 'short'\n"
            "- question: string\n"
            "- options: list of strings (for mcq type)\n"
            "- correctAnswer: string or number\n"
            "- explanation: detailed step-by-step corrective explanation\n"
            "- difficulty: string\n"
            "- topic: string\n"
        )
        if self._is_configured:
            try:
                model = genai.GenerativeModel(
                    model_name=self.fast_model_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                res = model.generate_content(prompt)
                return json.loads(res.text)
            except Exception as e:
                logger.error(f"Structured quiz generation failed: {e}")

        # Fallback structured quiz JSON
        return [
            {
                "id": "q1",
                "type": "mcq",
                "question": f"What is the primary characteristic of {topic}?",
                "options": [
                    "O(1) dynamic access",
                    "Recursive divide and conquer approach",
                    "Sequential traversal only",
                    "Constant space complexity"
                ],
                "correctAnswer": 1,
                "explanation": f"{topic} relies on dividing the problem domain into smaller sub-problems recursively to optimize step complexity.",
                "difficulty": difficulty,
                "topic": topic
            },
            {
                "id": "q2",
                "type": "tf",
                "question": f"{topic} guarantees logarithmic search performance in all scenarios.",
                "options": ["True", "False"],
                "correctAnswer": "False",
                "explanation": "If the underlying collection or tree is unbalanced, performance can degrade to linear O(N).",
                "difficulty": difficulty,
                "topic": topic
            }
        ]

    def _simulate_socratic_response(self, user_query: str) -> str:
        return (
            f"Hello! I understand you are asking about '{user_query}'.\n\n"
            "### 💡 Core Concept\n"
            "Let's break this down step by step so you master the underlying principle.\n\n"
            "### 🏢 Real-World Analogy\n"
            "Imagine a library system where books are organized by call numbers. Searching a sorted structure reduces search steps exponentially!\n\n"
            "Would you like me to simplify this further or provide an interactive practice question?"
        )

llm_client = GeminiLLMClient()

