from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis


class InvestigationStep(BaseModel):
    """An individual test step within an investigation plan."""
    step_id: str = Field(..., description="Unique step identifier (e.g., STEP-1)")
    objective: str = Field(..., description="Specific objective of this investigation step")
    tool: str = Field(..., description="Name of the investigation tool to use")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool execution")
    expected_observation: str = Field(..., description="What observation is expected if hypothesis is active")
    evidence_required: str = Field(..., description="Criteria for evidence collection")
    reasoning: str = Field(..., description="Why this specific step is required for testing the hypothesis")


class InvestigationPlan(BaseModel):
    """Actionable investigation plan for a selected hypothesis."""
    hypothesis_id: str = Field(..., description="ID of the hypothesis being investigated")
    investigation_goal: str = Field(..., description="Overarching goal of the investigation")
    reasoning: str = Field(..., description="Rationale for the sequence of investigation steps")
    steps: List[InvestigationStep] = Field(default_factory=list, description="Ordered list of investigation steps")
    success_criteria: str = Field(..., description="Criteria defining a successful evidence collection run")
    possible_outcomes: List[str] = Field(default_factory=list, description="Potential conclusions based on investigation findings")


class PlanInvestigationRequest(BaseModel):
    """Request payload for /engine/plan-investigation."""
    system_profile: SystemProfile = Field(..., description="System Profile of the target AI system")
    hypothesis: Hypothesis = Field(..., description="Selected hypothesis to design an investigation for")
    available_tools: List[Any] = Field(default_factory=list, description="Available tools or tool specifications")
    existing_evidence: List[str] = Field(default_factory=list, description="Existing evidence collected so far")


class PlanInvestigationResponse(BaseModel):
    """Response payload for /engine/plan-investigation."""
    status: Literal["ready", "insufficient_capability"] = Field(..., description="Status: 'ready' or 'insufficient_capability'")
    investigation_plan: Optional[InvestigationPlan] = Field(default=None, description="Generated plan if status is 'ready'")
    reason: Optional[str] = Field(default=None, description="Explanation if status is 'insufficient_capability'")


# Phase 5 Schemas

class ToolExecution(BaseModel):
    """Record of a tool execution for an investigation step."""
    execution_id: str = Field(..., description="Unique execution identifier")
    step_id: str = Field(..., description="ID of the investigation step executed")
    tool: str = Field(..., description="Name of the tool executed")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters passed to the tool")
    timestamp: str = Field(..., description="Execution timestamp")
    status: Literal["success", "failed", "unavailable"] = Field(..., description="Execution status")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Structured result dictionary if available")
    evidence: List[str] = Field(default_factory=list, description="Evidence items extracted from execution")
    error: Optional[str] = Field(default=None, description="Error message if failed or unavailable")


class Observation(BaseModel):
    """Structured observation derived from a tool execution."""
    observation_id: str = Field(..., description="Unique observation identifier")
    step_id: str = Field(..., description="ID of the investigation step")
    description: str = Field(..., description="Narrative description of what was observed")
    source: str = Field(..., description="Tool or component source of observation (e.g. 'model_tool', 'repository_tool', 'analysis_tool')")
    evidence: List[str] = Field(default_factory=list, description="Raw evidence supporting this observation")
    significance: str = Field(..., description="Explanation of why this observation matters for the hypothesis")


class InvestigationResult(BaseModel):
    """Aggregated results of executing an InvestigationPlan."""
    hypothesis_id: str = Field(..., description="Target hypothesis ID")
    investigation_goal: str = Field(..., description="Goal of the executed investigation")
    status: Literal["completed", "partially_completed", "failed", "insufficient_capability"] = Field(..., description="Overall execution status")
    executed_steps: List[ToolExecution] = Field(default_factory=list, description="List of recorded tool execution logs")
    observations: List[Observation] = Field(default_factory=list, description="List of source-tracked observations")
    evidence: List[str] = Field(default_factory=list, description="All aggregated evidence strings")
    limitations: List[str] = Field(default_factory=list, description="Known limitations or unavailable capabilities encountered during run")


class Interpretation(BaseModel):
    """LLM evidence interpretation evaluating observations relative to a specific hypothesis."""
    interpretation: str = Field(..., description="Detailed explanation of what the evidence demonstrates")
    hypothesis_status: Literal["supported", "weakened", "inconclusive"] = Field(..., description="Evaluation: 'supported', 'weakened', or 'inconclusive'")
    confidence: float = Field(..., description="Confidence rating between 0.0 and 1.0")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence items supporting the hypothesis")
    contradicting_evidence: List[str] = Field(default_factory=list, description="Evidence items weakening the hypothesis")
    remaining_unknowns: List[str] = Field(default_factory=list, description="Unresolved questions or missing evidence")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class ExecuteInvestigationRequest(BaseModel):
    """Request payload for /engine/execute-investigation."""
    system_profile: SystemProfile = Field(..., description="System Profile of the target AI system")
    hypothesis: Hypothesis = Field(..., description="Hypothesis being investigated")
    investigation_plan: InvestigationPlan = Field(..., description="Investigation Plan to execute")
    available_tools: List[Any] = Field(default_factory=list, description="List of available tools")
    initial_evidence: Optional[List[str]] = Field(default_factory=list, description="Optional initial evidence context")


class ExecuteInvestigationResponse(BaseModel):
    """Response payload for /engine/execute-investigation."""
    investigation_result: InvestigationResult = Field(..., description="Execution logs and observations")
    interpretation: Interpretation = Field(..., description="LLM interpretation of the evidence")
