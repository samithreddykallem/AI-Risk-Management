from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from app.schemas.system_profile import SystemProfile


class Hypothesis(BaseModel):
    """Pydantic model representing a system-specific risk hypothesis."""
    id: str = Field(..., description="Unique identifier for the hypothesis (e.g. HYP-001)")
    hypothesis: str = Field(..., description="Statement of what might be happening")
    why_it_is_plausible: str = Field(..., description="Explanation of why this is plausible for this specific system")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence from System Profile currently supporting the hypothesis")
    affected_part: str = Field(..., description="Part of the AI system affected (e.g., input processing, scoring, output generation)")
    potential_consequence: str = Field(..., description="Potential real-world adverse consequence if true")
    what_evidence_would_support_it: List[str] = Field(default_factory=list, description="Future observations that would strengthen the hypothesis")
    what_evidence_would_refute_it: List[str] = Field(default_factory=list, description="Future observations that would weaken or refute the hypothesis")
    priority: Literal["low", "medium", "high"] = Field(..., description="Priority rating: 'low', 'medium', or 'high'")
    confidence: float = Field(..., description="Confidence level between 0.0 and 1.0")
    status: Literal["OPEN", "SUPPORTED", "WEAKENED", "UNRESOLVED", "INSUFFICIENT_EVIDENCE"] = Field(
        default="OPEN",
        description="Hypothesis state: OPEN, SUPPORTED, WEAKENED, UNRESOLVED, INSUFFICIENT_EVIDENCE"
    )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class HypothesisGenerationRequest(BaseModel):
    """Request payload for /engine/generate-hypotheses."""
    system_profile: SystemProfile = Field(..., description="System Profile of the target AI system")
    available_evidence: Optional[List[str]] = Field(default_factory=list, description="Optional additional observed evidence")
    important_unknowns: Optional[List[str]] = Field(default_factory=list, description="Optional key missing parameters")


class HypothesisGenerationResponse(BaseModel):
    """Response payload for /engine/generate-hypotheses."""
    hypotheses: List[Hypothesis] = Field(default_factory=list, description="List of generated system-specific risk hypotheses")
