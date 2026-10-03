"""KaTeX Math Formatting Validator and Syntax Fixer for EduMate LLM Responses.

Validates and auto-corrects mathematical formatting in generated responses to ensure
proper rendering with KaTeX in the React frontend.
"""

import logging
import re
from typing import List, Tuple
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Regex patterns for math block extraction and detection
DISPLAY_MATH_PATTERN = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
INLINE_MATH_PATTERN = re.compile(r"(?<!\$)\$([^\$\n]+)\$(?!\$)")
SINGLE_DOLLAR_STANDALONE = re.compile(r"^\s*\$([^\$\n]+)\$\s*$", re.MULTILINE)


class ValidationReport(BaseModel):
    """Report container for math formatting validation."""

    is_valid: bool = Field(..., description="True if no formatting errors were found")
    display_formulas_count: int = Field(0, description="Count of valid $$...$$ display math blocks")
    inline_formulas_count: int = Field(0, description="Count of valid $...$ inline math blocks")
    issues: List[str] = Field(default_factory=list, description="List of detected formatting issues")
    fixed_text: str = Field(..., description="Auto-corrected text content")


class LaTeXValidator:
    """Validates and fixes KaTeX display math formatting in LLM tutor outputs.

    Mandates display math blocks formatted as $$<formula>$$ and converts
    malformed single-dollar lines to display blocks.
    """

    def validate_and_fix(self, text: str) -> ValidationReport:
        """Validate math formatting and produce auto-corrected text.

        Args:
            text: Markdown response text from Gemini LLM.

        Returns:
            ValidationReport with issue list, formula counts, and fixed text.
        """
        if not text:
            return ValidationReport(
                is_valid=True,
                display_formulas_count=0,
                inline_formulas_count=0,
                issues=[],
                fixed_text="",
            )

        issues: List[str] = []
        fixed_text = text

        # Issue 1: Unclosed $$ display math tags
        double_dollar_count = text.count("$$")
        if double_dollar_count % 2 != 0:
            issues.append("Unclosed display math delimiter ($$) detected")
            # Append closing $$ at the end of the text
            fixed_text = fixed_text + "\n$$"

        # Issue 2: Standalone single-dollar formulas (e.g., $O(n)$ on its own line) -> convert to $$...$$
        standalone_matches = list(SINGLE_DOLLAR_STANDALONE.finditer(fixed_text))
        if standalone_matches:
            issues.append(f"Found {len(standalone_matches)} standalone single-dollar formula(s); converting to $$...$$")
            fixed_text = SINGLE_DOLLAR_STANDALONE.sub(r"$$\1$$", fixed_text)

        # Issue 3: Empty math blocks ($$ $$)
        if "$$\n$$" in fixed_text or "$$$$" in fixed_text:
            issues.append("Empty display math block detected")
            fixed_text = fixed_text.replace("$$\n$$", "").replace("$$$$", "")

        # Count valid formulas in fixed text
        display_formulas = DISPLAY_MATH_PATTERN.findall(fixed_text)
        inline_formulas = INLINE_MATH_PATTERN.findall(fixed_text)

        is_valid = len(issues) == 0

        if not is_valid:
            logger.info(f"LaTeXValidator auto-corrected {len(issues)} math formatting issue(s)")

        return ValidationReport(
            is_valid=is_valid,
            display_formulas_count=len(display_formulas),
            inline_formulas_count=len(inline_formulas),
            issues=issues,
            fixed_text=fixed_text,
        )

    def extract_formulas(self, text: str) -> List[Tuple[str, str]]:
        """Extract all formulas with their type ('display' or 'inline').

        Args:
            text: Text to extract formulas from.

        Returns:
            List of tuples (formula_type, formula_content).
        """
        results: List[Tuple[str, str]] = []

        for match in DISPLAY_MATH_PATTERN.finditer(text):
            results.append(("display", match.group(1).strip()))

        for match in INLINE_MATH_PATTERN.finditer(text):
            results.append(("inline", match.group(1).strip()))

        return results


latex_validator = LaTeXValidator()
