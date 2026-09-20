from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SystemProfile(BaseModel):
    """
    Structured System Profile derived from individual project analysis.
    Uses 'unknown' when information is unavailable; strictly grounded in submitted evidence.
    """
    purpose: str = Field(..., description="Core purpose and problem solved by the AI system")
    intended_use: str = Field(..., description="Intended operational context and target use cases")
    ai_system_type: str = Field(..., description="High-level AI system categorization (e.g. Chatbot, Decision Support, Agent, Classifier)")
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
    deployment_context: str = Field(..., description="Where and how the system is deployed (e.g., internal tool, public web app, embedded system)")
    expected_benefits: List[str] = Field(default_factory=list, description="Stated or intended benefits of the AI project")
    potential_consequences: List[str] = Field(default_factory=list, description="Possible adverse real-world consequences of system failure or bias")
    important_unknowns: List[str] = Field(default_factory=list, description="Critical information missing from the submission that requires clarification")
    assumptions: List[str] = Field(default_factory=list, description="Explicit assumptions derived from the project description")
    observed_evidence: Dict[str, str] = Field(
        default_factory=dict,
        description="Traceability mapping key profile fields to specific quotes or evidence from submitted project inputs"
    )

    # Backwards compatibility attributes for orchestrator
    @property
    def system_name(self) -> str:
        return self.purpose[:50] if self.purpose else "Analyzed AI System"

    @property
    def primary_domain(self) -> str:
        return self.ai_system_type

    @property
    def key_capabilities(self) -> List[str]:
        return self.outputs

    @property
    def decision_impact_level(self) -> str:
        return self.decision_impact

    @property
    def autonomy_classification(self) -> str:
        return self.autonomy_level

    @property
    def sensitive_data_exposure(self) -> List[str]:
        return self.sensitive_data

    @property
    def vulnerable_populations(self) -> List[str]:
        return self.affected_users

    @property
    def technical_architecture_summary(self) -> str:
        return f"AI System Type: {self.ai_system_type}; Model: {self.model_type}; Decision Process: {self.decision_process}"

    @property
    def profile_summary(self) -> str:
        return f"Purpose: {self.purpose}. Intended Use: {self.intended_use}. Autonomy: {self.autonomy_level}."
