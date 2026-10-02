"""Quiz JSON Response Repair Middleware for EduMate.

Robustly sanitizes, repairs, and parses LLM-generated JSON strings, fixing markdown code fences,
trailing commas, conversational text wrappers, and missing braces.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
from services.ai_rag.schemas.quiz_schemas import QuizQuestionModel

logger = logging.getLogger(__name__)


class JsonRepairMiddleware:
    """Repairs malformed or fenced JSON strings output by generative models."""

    def clean_markdown_fences(self, text: str) -> str:
        """Strip markdown ```json and ``` wrapping blocks."""
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
        return cleaned.strip()

    def extract_json_block(self, text: str) -> str:
        """Locate and extract the primary JSON array or object substring."""
        cleaned = self.clean_markdown_fences(text)

        # Look for [ ... ] array
        array_match = re.search(r"(\[[\s\S]*\])", cleaned)
        if array_match:
            return array_match.group(1).strip()

        # Look for { ... } object
        obj_match = re.search(r"(\{[\s\S]*\})", cleaned)
        if obj_match:
            return obj_match.group(1).strip()

        return cleaned

    def fix_trailing_commas(self, json_str: str) -> str:
        """Remove trailing commas preceding closing brackets/braces."""
        fixed = re.sub(r",\s*([\]}])", r"\1", json_str)
        return fixed

    def repair_and_parse(self, raw_text: str) -> List[Dict[str, Any]]:
        """Attempt progressive repair strategies to extract structured quiz items.

        Args:
            raw_text: Raw string response from LLM.

        Returns:
            List of parsed dictionary objects.
        """
        if not raw_text or not raw_text.strip():
            return []

        # Strategy 1: Direct JSON parse
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return [parsed]
        except Exception:
            pass

        # Strategy 2: Clean markdown fences & extract block
        block = self.extract_json_block(raw_text)
        try:
            parsed = json.loads(block)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return [parsed]
        except Exception:
            pass

        # Strategy 3: Fix trailing commas
        fixed = self.fix_trailing_commas(block)
        try:
            parsed = json.loads(fixed)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return [parsed]
        except Exception:
            pass

        # Strategy 4: Regex item extraction fallback
        items: List[Dict[str, Any]] = []
        item_matches = re.finditer(r"\{[^{}]*\"question\"[^{}]*\}", raw_text)
        for m in item_matches:
            try:
                candidate = json.loads(self.fix_trailing_commas(m.group(0)))
                items.append(candidate)
            except Exception:
                continue

        return items


json_repair_middleware = JsonRepairMiddleware()
