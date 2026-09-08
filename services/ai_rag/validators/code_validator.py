"""Code Block Syntax Formatting Validator and Snippet Extractor for EduMate LLM Responses.

Validates, auto-detects language tags, auto-repairs unclosed fences, and extracts
code snippets from markdown response text for syntax rendering in the frontend.
"""

import logging
import re
from typing import List
from pydantic import BaseModel, Field

from services.ai_rag.schemas.tutor_schemas import CodeSnippet

logger = logging.getLogger(__name__)

# Regex pattern matching code blocks delimited by triple backticks
CODE_BLOCK_PATTERN = re.compile(r"```([a-zA-Z0-9_\-\+#]*)\n?(.*?)```", re.DOTALL)


class CodeValidationReport(BaseModel):
    """Report container for code block formatting validation."""

    is_valid: bool = Field(..., description="True if no code block formatting errors were found")
    code_blocks_count: int = Field(0, description="Number of detected code blocks")
    issues: List[str] = Field(default_factory=list, description="List of detected formatting issues")
    fixed_text: str = Field(..., description="Auto-corrected text content")
    snippets: List[CodeSnippet] = Field(default_factory=list, description="Extracted code snippets")


class CodeBlockValidator:
    """Validates code blocks formatted with triple backticks in Gemini LLM outputs.

    Ensures language tags are specified, repairs unclosed backticks, and extracts
    CodeSnippet objects for frontend rendering.
    """

    def validate_and_fix(self, text: str) -> CodeValidationReport:
        """Validate code block syntax, auto-repair fences, and extract snippets.

        Args:
            text: Markdown response text from LLM.

        Returns:
            CodeValidationReport containing validation status, issues, fixed text, and snippets.
        """
        if not text:
            return CodeValidationReport(
                is_valid=True,
                code_blocks_count=0,
                issues=[],
                fixed_text="",
                snippets=[],
            )

        issues: List[str] = []
        fixed_text = text

        # Issue 1: Unclosed triple backtick code fence
        backtick_count = text.count("```")
        if backtick_count % 2 != 0:
            issues.append("Unclosed code block fence (```) detected")
            fixed_text = fixed_text + "\n```"

        # Issue 2: Untagged code blocks (``` without language specifier)
        matches = list(CODE_BLOCK_PATTERN.finditer(fixed_text))
        snippets: List[CodeSnippet] = []

        for match in matches:
            lang_tag = match.group(1).strip().lower()
            code_content = match.group(2).strip()

            if not lang_tag:
                issues.append("Untagged code block missing language tag; auto-detecting")
                lang_tag = self._guess_language(code_content)
                # Replace untagged block with tagged block in fixed_text
                original_block = match.group(0)
                replacement_block = f"```{lang_tag}\n{code_content}\n```"
                fixed_text = fixed_text.replace(original_block, replacement_block, 1)

            snippets.append(
                CodeSnippet(
                    language=lang_tag or "plaintext",
                    code=code_content,
                )
            )

        is_valid = len(issues) == 0

        if not is_valid:
            logger.info(f"CodeBlockValidator auto-corrected {len(issues)} formatting issue(s)")

        return CodeValidationReport(
            is_valid=is_valid,
            code_blocks_count=len(snippets),
            issues=issues,
            fixed_text=fixed_text,
            snippets=snippets,
        )

    def extract_snippets(self, text: str) -> List[CodeSnippet]:
        """Extract all code snippets from response text.

        Args:
            text: Text to extract code snippets from.

        Returns:
            List of CodeSnippet objects.
        """
        report = self.validate_and_fix(text)
        return report.snippets

    @staticmethod
    def _guess_language(code: str) -> str:
        """Heuristic language detector for untagged code snippets."""
        if "#include" in code or "std::" in code or "cout <<" in code or "nullptr" in code:
            return "cpp"
        elif "def " in code or "import " in code or "print(" in code or "self." in code:
            return "python"
        elif "public class " in code or "System.out.println" in code:
            return "java"
        elif "const " in code or "let " in code or "function(" in code or "console.log" in code:
            return "javascript"
        elif "SELECT " in code or "FROM " in code or "WHERE " in code or "JOIN " in code:
            return "sql"
        return "plaintext"


code_validator = CodeBlockValidator()
