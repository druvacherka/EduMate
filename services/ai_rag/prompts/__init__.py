"""Prompts package for EduMate AI & RAG service.

Exporting level-based Socratic prompt engines, prompt factory, quick action engine,
and clarification pipeline.
"""

from services.ai_rag.prompts.beginner_prompts import BeginnerSocraticEngine, beginner_engine
from services.ai_rag.prompts.clarification_pipeline import (
    ClarificationEvaluation,
    ClarificationPipeline,
    clarification_pipeline,
)
from services.ai_rag.prompts.level_builders import (
    AdvancedPromptEngine,
    IntermediatePromptEngine,
    LevelPromptFactory,
    prompt_factory,
)
from services.ai_rag.prompts.quick_actions import QuickActionEngine, quick_action_engine
from services.ai_rag.prompts.socratic_prompts import build_system_prompt

__all__ = [
    "BeginnerSocraticEngine",
    "beginner_engine",
    "IntermediatePromptEngine",
    "AdvancedPromptEngine",
    "LevelPromptFactory",
    "prompt_factory",
    "build_system_prompt",
    "QuickActionEngine",
    "quick_action_engine",
    "ClarificationPipeline",
    "ClarificationEvaluation",
    "clarification_pipeline",
]
