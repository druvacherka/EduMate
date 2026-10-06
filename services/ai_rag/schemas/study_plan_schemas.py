"""Validation models for Gemini-generated adaptive study plans."""

from pydantic import BaseModel, ConfigDict, Field


class GeneratedStudyPlanWeek(BaseModel):
    model_config = ConfigDict(extra="forbid")

    week_number: int = Field(..., ge=1, le=16)
    theme: str = Field(..., min_length=3, max_length=160)
    focus_topics: list[str] = Field(..., min_length=1, max_length=5)
    target_milestone: str = Field(..., min_length=5, max_length=240)


class GeneratedStudyPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weekly_breakdown: list[GeneratedStudyPlanWeek] = Field(..., min_length=1, max_length=16)
