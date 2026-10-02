"""Unit tests for Socratic prompt engines, quick action handlers, and clarification pipeline."""

import unittest
from services.ai_rag.prompts.level_builders import prompt_factory
from services.ai_rag.prompts.quick_actions import quick_action_engine
from services.ai_rag.prompts.clarification_pipeline import clarification_pipeline


class TestPromptFactory(unittest.TestCase):
    """Test suite for LevelPromptFactory."""

    def test_beginner_prompt_generation(self):
        prompt = prompt_factory.get_system_prompt(
            level="Beginner",
            subject="Computer Science",
            topic="Binary Search Trees",
            language="English",
            weak_areas=["BST Deletion"],
        )
        self.assertIn("BEGINNER STUDENT", prompt)
        self.assertIn("Binary Search Trees", prompt)
        self.assertIn("BST Deletion", prompt)
        self.assertIn("library catalog", prompt.lower())

    def test_intermediate_prompt_generation(self):
        prompt = prompt_factory.get_system_prompt(
            level="Intermediate",
            subject="Data Structures",
            topic="Recursion",
            language="English",
        )
        self.assertIn("INTERMEDIATE STUDENT", prompt)
        self.assertIn("Big-O notation", prompt)
        self.assertIn("Recursion", prompt)

    def test_advanced_prompt_generation(self):
        prompt = prompt_factory.get_system_prompt(
            level="Advanced",
            subject="Algorithms",
            topic="Dynamic Programming",
            language="English",
        )
        self.assertIn("ADVANCED SCHOLAR", prompt)
        self.assertIn("mathematical proofs", prompt.lower())
        self.assertIn("KaTeX", prompt)

    def test_multilingual_prompt_instructions(self):
        prompt_hi = prompt_factory.get_system_prompt(
            level="Beginner",
            language="Hindi",
        )
        self.assertIn("Hindi (Devanagari script)", prompt_hi)

        prompt_te = prompt_factory.get_system_prompt(
            level="Beginner",
            language="Telugu",
        )
        self.assertIn("Telugu (Telugu script)", prompt_te)


class TestQuickActions(unittest.TestCase):
    """Test suite for QuickActionEngine."""

    def test_simplify_action_prompt(self):
        prompt = quick_action_engine.build_action_prompt(
            action_type="simplify",
            previous_response="A Binary Search Tree maintains order property...",
            topic="Binary Search Trees",
            level="Beginner",
        )
        self.assertIn("SIMPLIFY EXPLANATION", prompt)
        self.assertIn("A Binary Search Tree maintains order property", prompt)

    def test_explain_deeper_action_prompt(self):
        prompt = quick_action_engine.build_action_prompt(
            action_type="explain_deeper",
            previous_response="Semaphores regulate access...",
            topic="Process Synchronization",
            level="Intermediate",
        )
        self.assertIn("EXPLAIN DEEPER", prompt)
        self.assertIn("Big-O", prompt)


class TestClarificationPipeline(unittest.TestCase):
    """Test suite for ClarificationPipeline."""

    def test_correct_response_guidance(self):
        prompt = clarification_pipeline.build_clarification_response_prompt(
            mastery_level="correct",
            student_response="The time complexity of search in balanced BST is O(log n).",
            topic="Binary Search Trees",
            level="Intermediate",
        )
        self.assertIn("REINFORCE & ADVANCE", prompt)
        self.assertIn("CORRECTLY", prompt)

    def test_confused_response_guidance(self):
        prompt = clarification_pipeline.build_clarification_response_prompt(
            mastery_level="confused",
            student_response="I don't understand how nodes get swapped during deletion.",
            topic="BST Deletion",
            level="Beginner",
        )
        self.assertIn("SUPPORTIVE RE-SCAFFOLDING", prompt)
        self.assertIn("CONFUSED", prompt)


if __name__ == "__main__":
    unittest.main()
