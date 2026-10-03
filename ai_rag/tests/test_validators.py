"""Unit tests for KaTeX math and code block formatting validators."""

import unittest
from ai_rag.validators.latex_validator import latex_validator
from ai_rag.validators.code_validator import code_validator


class TestLaTeXValidator(unittest.TestCase):
    """Test suite for LaTeXValidator."""

    def test_valid_display_math(self):
        text = "The time complexity is $$\\mathcal{O}(n \\log n)$$ for Merge Sort."
        report = latex_validator.validate_and_fix(text)
        self.assertTrue(report.is_valid)
        self.assertEqual(report.display_formulas_count, 1)
        self.assertEqual(len(report.issues), 0)

    def test_unclosed_double_dollar_repair(self):
        text = "Complexity formula: $$\\mathcal{O}(n^2)"
        report = latex_validator.validate_and_fix(text)
        self.assertFalse(report.is_valid)
        self.assertTrue(report.fixed_text.endswith("$$"))
        self.assertIn("Unclosed display math delimiter", report.issues[0])

    def test_standalone_single_dollar_conversion(self):
        text = "Here is the equation:\n$E = mc^2$\nWhich is fundamental."
        report = latex_validator.validate_and_fix(text)
        self.assertFalse(report.is_valid)
        self.assertIn("$$E = mc^2$$", report.fixed_text)
        self.assertEqual(report.display_formulas_count, 1)

    def test_formula_extraction(self):
        text = "Given $x = 1$ and $$\\sum_{i=0}^n i = \\frac{n(n+1)}{2}$$ calculate sum."
        formulas = latex_validator.extract_formulas(text)
        self.assertEqual(len(formulas), 2)
        self.assertEqual(formulas[0][0], "display")
        self.assertEqual(formulas[1][0], "inline")


class TestCodeBlockValidator(unittest.TestCase):
    """Test suite for CodeBlockValidator."""

    def test_valid_tagged_code_block(self):
        text = "```python\ndef solve():\n    return 42\n```"
        report = code_validator.validate_and_fix(text)
        self.assertTrue(report.is_valid)
        self.assertEqual(report.code_blocks_count, 1)
        self.assertEqual(report.snippets[0].language, "python")
        self.assertEqual(report.snippets[0].code, "def solve():\n    return 42")

    def test_unclosed_code_fence_repair(self):
        text = "Here is C++ code:\n```cpp\nint x = 10;"
        report = code_validator.validate_and_fix(text)
        self.assertFalse(report.is_valid)
        self.assertTrue(report.fixed_text.endswith("```"))
        self.assertIn("Unclosed code block fence", report.issues[0])

    def test_untagged_language_auto_detection(self):
        text = "```\n#include <iostream>\nint main() { std::cout << 10; }\n```"
        report = code_validator.validate_and_fix(text)
        self.assertFalse(report.is_valid)
        self.assertEqual(report.snippets[0].language, "cpp")
        self.assertIn("```cpp", report.fixed_text)


if __name__ == "__main__":
    unittest.main()
