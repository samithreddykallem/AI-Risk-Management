from typing import List, Optional, Any
from pydantic import BaseModel, Field


class ProjectInput(BaseModel):
    """Payload schema describing an AI project to be analyzed."""
    project_name: str = Field(..., description="Name of the AI project")
    description: str = Field(..., description="Detailed description of what the project does")
    github_url: Optional[str] = Field(default=None, description="Optional repository URL")
    documentation: Optional[str] = Field(default=None, description="Optional technical documentation")
    dataset_path: Optional[str] = Field(default=None, description="File path to the uploaded dataset (CSV/XLSX/JSON)")
    dataset_name: Optional[str] = Field(default=None, description="Name of uploaded dataset file")
    dataset_description: Optional[str] = Field(default=None, description="Optional dataset description")
    target_column: Optional[str] = Field(default=None, description="Optional target/label column name")
    sensitive_attributes: List[str] = Field(default_factory=list, description="User specified or confirmed sensitive columns")
    predictions_path: Optional[str] = Field(default=None, description="Optional file path to model prediction outputs")
    model_artifact_path: Optional[str] = Field(default=None, description="Optional file path to model artifact")
    sample_inputs: List[Any] = Field(default_factory=list, description="Optional legacy sample input payloads")
    sample_outputs: List[Any] = Field(default_factory=list, description="Optional legacy sample output payloads")


class TestLLMRequest(BaseModel):
    """Request payload for /engine/test-llm."""
    message: str = Field(..., json_schema_extra={"example": "Say hello"}, description="Input query for the LLM")


class TestLLMResponse(BaseModel):
    """Response payload for /engine/test-llm."""
    response: str = Field(..., description="Text response from the LLM")


class AuditRequest(BaseModel):
    """Request payload for /engine/audit."""
    project: ProjectInput = Field(..., description="Target AI project specification")
    dataset_profile: Optional[Any] = Field(default=None, description="Pre-computed DatasetProfile if available")
    available_tools: List[Any] = Field(
        default_factory=lambda: [
            "dataset_profile_tool",
            "missingness_analysis_tool",
            "class_distribution_tool",
            "group_distribution_tool",
            "correlation_analysis_tool",
            "contingency_analysis_tool",
            "feature_association_tool",
            "proxy_analysis_tool",
            "group_performance_analysis_tool",
            "error_rate_analysis_tool",
            "controlled_subgroup_comparison_tool"
        ],
        description="List of available investigation tool names"
    )
    max_iterations: Optional[int] = Field(default=3, description="Maximum adaptive investigation iterations to execute")


class AuditResponse(BaseModel):
    """Response payload for /engine/audit."""
    audit_id: str = Field(..., description="Unique identifier for the audit session")
    system_profile: Any = Field(..., description="Generated System Profile")
    dataset_profile: Optional[Any] = Field(default=None, description="Dataset Profile generated during audit")
    hypotheses: List[Any] = Field(default_factory=list, description="System-specific risk hypotheses generated")
    investigation_trace: List[Any] = Field(default_factory=list, description="Complete iteration history trace")
    final_evidence: List[str] = Field(default_factory=list, description="Aggregated evidence collected across all iterations")
    unresolved_questions: List[str] = Field(default_factory=list, description="Remaining unanswered questions")
    limitations: List[str] = Field(default_factory=list, description="Known tool or environmental limitations encountered")
    audit_report_markdown: Optional[str] = Field(default=None, description="Human-readable final AI Audit Report in Markdown")
    status: str = Field(..., description="Overall status of audit ('completed', 'max_iterations_reached', 'insufficient_capability', 'failed')")


