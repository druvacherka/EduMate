"""Technical Domain Dictionary Mapping for Multilingual Explanations (Hindi & Telugu).

Preserves standard technical terms in English alongside vernacular conceptual equivalents,
ensuring students learn both conceptual intuition and academic terminology.
"""

from typing import Dict, Optional


TECHNICAL_DICTIONARY: Dict[str, Dict[str, str]] = {
    "binary search tree": {
        "Hindi": "द्वि-आधारी खोज वृक्ष (Binary Search Tree)",
        "Telugu": "బైనరీ సెర్చ్ ట్రీ (Binary Search Tree)",
    },
    "array": {
        "Hindi": "सरणी (Array)",
        "Telugu": "శ్రేణి (Array)",
    },
    "linked list": {
        "Hindi": "लिंक्ड सूची (Linked List)",
        "Telugu": "లింక్డ్ లిస్ట్ (Linked List)",
    },
    "stack": {
        "Hindi": "स्टैक (Stack - LIFO संरचना)",
        "Telugu": "స్టాక్ (Stack - LIFO అమరిక)",
    },
    "queue": {
        "Hindi": "पंक्ति (Queue - FIFO संरचना)",
        "Telugu": "క్యూ (Queue - FIFO అమరిక)",
    },
    "recursion": {
        "Hindi": "पुनरावर्तन (Recursion)",
        "Telugu": "పునరావృతం (Recursion)",
    },
    "time complexity": {
        "Hindi": "समय जटिलता (Time Complexity)",
        "Telugu": "సమయ సంక్లిష్టత (Time Complexity)",
    },
    "space complexity": {
        "Hindi": "स्थान जटिलता (Space Complexity)",
        "Telugu": "స్పేస్ కాంప్లెక్సిటీ (Space Complexity)",
    },
    "sorting": {
        "Hindi": "क्रमबद्ध करना (Sorting)",
        "Telugu": "క్రమబద్ధీకరణ (Sorting)",
    },
    "normalization": {
        "Hindi": "सामान्यीकरण (Normalization)",
        "Telugu": "సాధారణీకరణ (Normalization)",
    },
    "in-order traversal": {
        "Hindi": "इन-ऑर्डर ट्रैवर्सल (In-Order Traversal)",
        "Telugu": "ఇన్-ఆర్డర్ ట్రావర్సల్ (In-Order Traversal)",
    },
    "hash table": {
        "Hindi": "हैश तालिका (Hash Table)",
        "Telugu": "హాష్ టేబుల్ (Hash Table)",
    },
}


def get_technical_term(term: str, language: str) -> str:
    """Return bilingual term mapping for a technical concept.

    Args:
        term: English term in lowercase.
        language: 'Hindi' or 'Telugu'.

    Returns:
        Mapped bilingual string, or original term if not found.
    """
    clean_term = term.strip().lower()
    entry = TECHNICAL_DICTIONARY.get(clean_term)
    if entry and language in entry:
        return entry[language]
    return term


def enrich_with_technical_glossary(text: str, language: str) -> str:
    """Scan and annotate key technical terms in user text for multilingual context injection.

    Args:
        text: Query or explanation text.
        language: 'Hindi' or 'Telugu'.

    Returns:
        Text with glossary annotations if relevant terms appear.
    """
    if language not in ("Hindi", "Telugu"):
        return text

    detected_terms = []
    text_lower = text.lower()
    for term, mapping in TECHNICAL_DICTIONARY.items():
        if term in text_lower:
            detected_terms.append(f"- {term.title()}: {mapping[language]}")

    if not detected_terms:
        return text

    glossary_block = "\n\n[Bilingual Glossary Context]:\n" + "\n".join(detected_terms)
    return text + glossary_block
