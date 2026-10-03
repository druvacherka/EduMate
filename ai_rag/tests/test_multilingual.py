"""Unit tests for Multilingual Language Detection, Technical Dictionary, and System Prompts."""

import pytest
from ai_rag.prompts.multilingual_prompts import multilingual_prompt_factory
from ai_rag.prompts.technical_dictionary import (
    TECHNICAL_DICTIONARY,
    enrich_with_technical_glossary,
    get_technical_term,
)
from ai_rag.validators.language_detector import multilingual_detector


def test_language_detection_native_scripts():
    # Hindi Devanagari
    lang_hi, conf_hi = multilingual_detector.detect_language("बाइनरी सर्च ट्री कैसे काम करता है?")
    assert lang_hi == "Hindi"
    assert conf_hi > 0.5

    # Telugu script
    lang_te, conf_te = multilingual_detector.detect_language("బైనరీ సెర్చ్ ట్రీ ఎలా పనిచేస్తుంది?")
    assert lang_te == "Telugu"
    assert conf_te > 0.5

    # English
    lang_en, conf_en = multilingual_detector.detect_language("How does a binary search tree work?")
    assert lang_en == "English"
    assert conf_en > 0.7


def test_language_detection_transliterated_code_mixing():
    # Hinglish
    lang_hinglish, _ = multilingual_detector.detect_language("Binary search tree kaise kaam karta hai samjhao")
    assert lang_hinglish == "Hindi"

    # Tenglish
    lang_tenglish, _ = multilingual_detector.detect_language("Binary search tree ela pani chestundi cheppandi")
    assert lang_tenglish == "Telugu"


def test_technical_dictionary_lookup():
    bst_hi = get_technical_term("binary search tree", "Hindi")
    assert "द्वि-आधारी खोज वृक्ष" in bst_hi
    assert "Binary Search Tree" in bst_hi

    bst_te = get_technical_term("binary search tree", "Telugu")
    assert "బైనరీ సెర్చ్ ట్రీ" in bst_te

    # Enrich glossary
    enriched_hi = enrich_with_technical_glossary("Explain recursion and time complexity", "Hindi")
    assert "Bilingual Glossary Context" in enriched_hi
    assert "Recursion" in enriched_hi
    assert "Time Complexity" in enriched_hi


def test_multilingual_prompt_factory():
    prompt_hi = multilingual_prompt_factory.get_system_prompt(language="Hindi", level="Beginner")
    assert "EduMate" in prompt_hi
    assert "सुकराती पद्धति" in prompt_hi
    assert "Student Learning Level: Beginner" in prompt_hi

    prompt_te = multilingual_prompt_factory.get_system_prompt(language="Telugu", level="Advanced")
    assert "EduMate" in prompt_te
    assert "సోక్రటీస్ పద్ధతి" in prompt_te
    assert "Student Learning Level: Advanced" in prompt_te
