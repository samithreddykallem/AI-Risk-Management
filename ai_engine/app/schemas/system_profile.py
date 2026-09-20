from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class SystemProfile(BaseModel):
    """
    Structured System Profile derived from individual project analysis.
    Contains 'unknown' when information is unavailable; strictly grounded in submitted evidence.
    """
    purpose: str = Field(..., description="Core purpose and problem solved by the AI system")
    intended_use: str = Field(..., description="Intended operational context and target use cases")
    ai_system_type: str = Field(..., description="High-level AI system categorization (e.g., Chatbot, Decision Support, Agent, Classifier)")
    model_type: str = Field(..., description="Underlying model architecture or algorithm type if stated, or 'unknown'")
    inputs: List[str] = Field(default_factory=list, description="Data inputs used or processed by the system")
    outputs: List[str] = Field(default_factory=list, description="Outputs, scores, text, or actions produced by the system")
    decision_process: str = Field(..., description="Explanation of how inputs are transformed into decisions/outputs")
    affected_users: List[str] = Field(default_factory=list, description="Individuals, groups, or stakeholders impacted by the system")
    decision_impact: str = Field(..., description="Criticality and real-world severity of decisions made")
    autonomy_level: str = Field(..., description="Degree of automated decision-making and operational autonomy")
    data_types: List[str] = Field(default_factory=list, description="Categories of data handled")
    sensitive_data: List[str] = Field(default_factory=list, description="Sensitive, confidential, or PII data elements involved")
    external_services: List[str] = Field(default_factory=list, description="Third-party APIs, databases, or external integrations used")
    human_involvement: str = Field(..., description="Role and mechanism of human review, oversight, or intervention")
    deployment_context: str = Field(..., description="Where and how the system is deployed")
    expected_benefits: List[str] = Field(default_factory=list, description="Stated or intended benefits of the AI project")
    potential_consequences: List[str] = Field(default_factory=list, description="Possible adverse real-world consequences of system failure or bias")
    important_unknowns: List[str] = Field(default_factory=list, description="Critical information missing from the submission")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions derived from the project description")
    primary_domain: str = Field(default="general_ai", description="Primary application domain (e.g. credit_risk, healthcare, fraud)")
    system_type: str = Field(default="classification_model", description="Categorization of AI system")
    intended_purpose: str = Field(default="general assessment", description="Short statement of intended purpose")
    dataset_path: Optional[str] = Field(default=None, description="Optional path to uploaded dataset")
    dataset_name: Optional[str] = Field(default=None, description="Optional dataset file name")
    target_candidate: Optional[str] = Field(default=None, description="Target column candidate")
    sensitive_candidates: List[Any] = Field(default_factory=list, description="Sensitive attribute candidates")
    profile_summary: Optional[str] = Field(default=None, description="Summary of system profile")
    observed_evidence: Dict[str, str] = Field(
        default_factory=dict,
        description="Traceability mapping key profile fields to specific quotes or evidence from submitted project inputs"
    )

