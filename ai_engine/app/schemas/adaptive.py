from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field, field_validator
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import InvestigationPlan, ToolExecution, Observation, Interpretation


class AdaptiveDecision(BaseModel):
    """Structured decision made by the adaptive agent after each investigation step."""
    action: Literal["continue", "stop"] = Field(..., description="Action to take: 'continue' or 'stop'")
    reasoning: str = Field(..., description="Detailed rationale for why the agent decided to continue or stop")
    evidence_summary: str = Field(..., description="Summary of evidence evaluated so far")
    remaining_uncertainties: List[str] = Field(default_factory=list, description="Key remaining uncertainties that require investigation")
    next_question: Optional[str] = Field(default=None, description="Target question to answer in next investigation if action='continue'")
    confidence: float = Field(..., description="Confidence rating between 0.0 and 1.0")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    @field_validator("next_question")
    @classmethod
    def validate_next_question(cls, v: Optional[str], info) -> Optional[str]:
        # Validate that next_question is provided if action is 'continue'
        action = info.data.get("action")
        if action == "continue" and not v:
            raise ValueError("next_question is required when action='continue'")
        return v


class CriticEvaluation(BaseModel):
    """Independent Evidence Critic review of an executed investigation."""
    supports_hypothesis: bool = Field(..., description="Whether empirical evidence supports the hypothesis")
    confounding_variables: List[str] = Field(default_factory=list, description="Other variables that could explain the result")
    sample_size_sufficient: bool = Field(default=True, description="Whether sample size is sufficient")
    statistically_meaningful: bool = Field(default=True, description="Whether result is statistically meaningful")
    missing_evidence: List[str] = Field(default_factory=list, description="Evidence still missing")
    decision: Literal["CONTINUE", "STOP"] = Field(..., description="Critic recommendation: CONTINUE or STOP")
    reasoning: str = Field(..., description="Detailed critic reasoning")


class EvidenceLineage(BaseModel):
    """Full causal lineage chain for an audit discovery."""
    dataset_name: str
    discovery_summary: str
    hypothesis_id: str
    hypothesis_text: str
    investigation_id: str
    tool_name: str
    actual_result_summary: str
    observation_text: str
    critic_interpretation: str
    adaptive_decision: str


class AdaptiveIteration(BaseModel):
    """Complete trace log of an individual adaptive iteration."""
    iteration: int = Field(..., description="Iteration index sequence number (1-based)")
    hypothesis: Hypothesis = Field(..., description="Target hypothesis being evaluated")
    investigation_plan: InvestigationPlan = Field(..., description="Investigation plan executed in this iteration")
    tool_executions: List[ToolExecution] = Field(default_factory=list, description="Logged tool execution records")
    observations: List[Observation] = Field(default_factory=list, description="Source-tracked observations derived")
    interpretation: Interpretation = Field(..., description="LLM evidence interpretation")
    critic_evaluation: Optional[CriticEvaluation] = Field(default=None, description="Independent critic evaluation")
    adaptive_decision: AdaptiveDecision = Field(..., description="Adaptive decision made at the end of iteration")
    lineage: Optional[EvidenceLineage] = Field(default=None, description="Lineage chain record")



class AdaptiveInvestigationResult(BaseModel):
    """Aggregated result of the complete adaptive investigation loop."""
    status: Literal["completed", "max_iterations_reached", "insufficient_capability", "failed"] = Field(..., description="Overall status")
    iterations: List[AdaptiveIteration] = Field(default_factory=list, description="Complete iteration history trace")
    final_evidence: List[str] = Field(default_factory=list, description="All aggregated evidence strings")
    unresolved_questions: List[str] = Field(default_factory=list, description="Remaining unanswered questions")
    limitations: List[str] = Field(default_factory=list, description="Tool or data limitations encountered")


class RunAdaptiveInvestigationRequest(BaseModel):
    """Request payload for /engine/run-adaptive-investigation."""
    system_profile: SystemProfile = Field(..., description="System Profile of the target AI system")
    hypotheses: List[Hypothesis] = Field(..., description="List of system-specific risk hypotheses")
    available_tools: List[Any] = Field(default_factory=list, description="List of available tools")
    initial_evidence: Optional[List[str]] = Field(default_factory=list, description="Optional initial evidence context")
    max_iterations: Optional[int] = Field(default=5, description="Maximum adaptive iterations to execute (default 5)")


class RunAdaptiveInvestigationResponse(BaseModel):
    """Response payload for /engine/run-adaptive-investigation."""
    status: Literal["completed", "max_iterations_reached", "insufficient_capability", "failed"] = Field(..., description="Overall status")
    iterations: List[AdaptiveIteration] = Field(default_factory=list, description="Complete iteration history trace")
    final_evidence: List[str] = Field(default_factory=list, description="All aggregated evidence strings")
    unresolved_questions: List[str] = Field(default_factory=list, description="Remaining unanswered questions")
    limitations: List[str] = Field(default_factory=list, description="Tool or data limitations encountered")
