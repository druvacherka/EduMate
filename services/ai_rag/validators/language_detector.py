"""Multilingual Query Language Detector and Code-Mixing Classifier for EduMate.

Detects Devanagari script (Hindi), Telugu script, and English/Latin script queries,
including common transliterated academic code-switching patterns (Hinglish/Tenglish).
"""

import re
from typing import Dict, Literal, Tuple

LanguageType = Literal["English", "Hindi", "Telugu"]


class MultilingualDetector:
    """Detects primary language of student prompts and determines pedagogical language strategy."""

    # Unicode ranges
    DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")
    TELUGU_REGEX = re.compile(r"[\u0C00-\u0C7F]")

    # Common transliteration marker words
    HINGLISH_KEYWORDS = {
        "kya", "kaise", "samjhao", "batao", "hai", "hota", "hoti", "kyun",
        "matlab", "udaharan", "achha", "karein", "chahiye", "samajh"
    }
    TENGLISH_KEYWORDS = {
        "enti", "ela", "cheppandi", "undi", "vuntundi", "enduku",
        "ardham", "chesukovali", "udaharana", "cheyali", "kani"
    }

    def detect_language(self, text: str, fallback_language: LanguageType = "English") -> Tuple[LanguageType, float]:
        """Detect the language of text with confidence score.

        Args:
            text: Input student query.
            fallback_language: Default language if text is purely alphanumeric without strong markers.

        Returns:
            Tuple of (detected_language, confidence_score: 0.0 - 1.0).
        """
        if not text or not text.strip():
            return fallback_language, 1.0

        clean_text = text.strip()
        total_chars = len(clean_text)

        # 1. Native script detection
        devanagari_chars = len(self.DEVANAGARI_REGEX.findall(clean_text))
        telugu_chars = len(self.TELUGU_REGEX.findall(clean_text))

        if devanagari_chars > 0 and devanagari_chars / total_chars >= 0.15:
            confidence = min(1.0, (devanagari_chars / total_chars) * 2.0)
            return "Hindi", round(confidence, 2)

        if telugu_chars > 0 and telugu_chars / total_chars >= 0.15:
            confidence = min(1.0, (telugu_chars / total_chars) * 2.0)
            return "Telugu", round(confidence, 2)

        # 2. Latin script transliteration keywords check (Hinglish / Tenglish)
        words = re.findall(r"\b\w+\b", clean_text.lower())
        if words:
            hinglish_matches = sum(1 for w in words if w in self.HINGLISH_KEYWORDS)
            tenglish_matches = sum(1 for w in words if w in self.TENGLISH_KEYWORDS)

            if hinglish_matches > 0 and hinglish_matches >= tenglish_matches:
                conf = min(0.95, (hinglish_matches / len(words)) * 2.5 + 0.3)
                return "Hindi", round(conf, 2)

            if tenglish_matches > 0 and tenglish_matches > hinglish_matches:
                conf = min(0.95, (tenglish_matches / len(words)) * 2.5 + 0.3)
                return "Telugu", round(conf, 2)

        # Default to English
        return fallback_language, 0.9


multilingual_detector = MultilingualDetector()
