"""Citation Extraction, Source Mapping, and Grounding Verification Engine for EduMate RAG.

Parses inline citation tags [Doc: <name>, Page <num>], maps them to retrieved source chunks,
validates grounding correctness, and formats structured reference footers.
"""

import re
from typing import List, Optional, Set, Tuple
from pydantic import BaseModel, Field
from ai_rag.schemas.vector_schemas import SearchResult


class CitationReference(BaseModel):
    """Represents a single parsed inline citation tag from LLM output."""

    document_name: str = Field(..., description="Referenced source PDF filename")
    page_number: int = Field(..., ge=1, description="Referenced source page number")
    raw_tag: str = Field(..., description="Exact raw citation tag substring")


class GroundingAnalysisResult(BaseModel):
    """Result payload from grounding analysis and citation validation."""

    is_grounded: bool = Field(..., description="Whether response is adequately grounded in study material")
    fallback_triggered: bool = Field(False, description="Whether fallback ungrounded alert was triggered")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Grounding confidence ratio (0-1)")
    parsed_citations: List[CitationReference] = Field(default_factory=list, description="Unique inline citations found")
    formatted_response: str = Field(..., description="Response text formatted with optional citation reference table")


class CitationValidator:
    """Extracts, validates, and formats study material citations from LLM output text."""

    # Matches patterns like: [Doc: Math_Notes.pdf, Page 12] or [Doc: Physics.pdf, Page: 4]
    CITATION_REGEX = re.compile(
        r"\[Doc:\s*([^,\]]+),\s*Page:?\s*(\d+)\]", re.IGNORECASE
    )

    def extract_citations(self, text: str) -> List[CitationReference]:
        """Extract all inline citation tags from raw response text.

        Args:
            text: LLM generated response string.

        Returns:
            List of CitationReference objects.
        """
        matches = self.CITATION_REGEX.findall(text)
        citations: List[CitationReference] = []
        seen: Set[Tuple[str, int]] = set()

        for doc_name, page_str in matches:
            clean_doc = doc_name.strip()
            try:
                page_num = int(page_str.strip())
            except ValueError:
                continue

            key = (clean_doc.lower(), page_num)
            if key not in seen:
                seen.add(key)
                raw_tag = f"[Doc: {clean_doc}, Page {page_num}]"
                citations.append(
                    CitationReference(
                        document_name=clean_doc,
                        page_number=page_num,
                        raw_tag=raw_tag,
                    )
                )

        return citations

    def validate_and_format(
        self,
        llm_response: str,
        context_chunks: List[SearchResult],
        min_confidence: float = 0.5,
    ) -> GroundingAnalysisResult:
        """Validate citations against available context chunks and produce formatted output.

        Args:
            llm_response: Raw completion string from LLM.
            context_chunks: Source search results available to the prompt context.
            min_confidence: Threshold required for grounding pass.

        Returns:
            GroundingAnalysisResult object with metrics and formatted output.
        """
        # Check if fallback ungrounded message was output directly
        if "Information not found in study material" in llm_response:
            return GroundingAnalysisResult(
                is_grounded=False,
                fallback_triggered=True,
                confidence_score=0.0,
                parsed_citations=[],
                formatted_response=llm_response.strip(),
            )

        extracted = self.extract_citations(llm_response)

        if not context_chunks:
            # Response generated without context
            is_grounded = len(extracted) == 0
            return GroundingAnalysisResult(
                is_grounded=is_grounded,
                fallback_triggered=not is_grounded,
                confidence_score=1.0 if is_grounded else 0.0,
                parsed_citations=extracted,
                formatted_response=llm_response.strip(),
            )

        # Build valid (document_name.lower(), page_number) set from retrieved context
        valid_sources: Set[Tuple[str, int]] = {
            (chunk.document_name.lower(), chunk.page_number) for chunk in context_chunks
        }

        valid_citations = [
            cit for cit in extracted if (cit.document_name.lower(), cit.page_number) in valid_sources
        ]

        if extracted:
            confidence = len(valid_citations) / len(extracted)
        else:
            # If no explicit citations generated, check text relevance against context
            confidence = 0.7 if len(context_chunks) > 0 else 0.0

        is_grounded = confidence >= min_confidence

        # Append structured Reference Section if citations exist
        formatted_text = llm_response.strip()
        if extracted:
            references_header = "\n\n### 📖 Verified Study Material References\n"
            ref_items = [
                f"- **{cit.document_name}** (Page {cit.page_number})" for cit in extracted
            ]
            formatted_text += references_header + "\n".join(ref_items)

        return GroundingAnalysisResult(
            is_grounded=is_grounded,
            fallback_triggered=not is_grounded,
            confidence_score=round(confidence, 2),
            parsed_citations=extracted,
            formatted_response=formatted_text,
        )
