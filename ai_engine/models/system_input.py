from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProjectInput(BaseModel):
    """Input payload describing an AI project to be analyzed for System Profile creation."""
    project_name: str = Field(..., description="Name of the AI project")
    description: str = Field(..., description="Detailed description of what the project does")
    github_url: Optional[str] = Field(default=None, description="Optional repository URL")
    documentation: Optional[str] = Field(default=None, description="Optional technical or operational documentation")
    sample_inputs: List[Any] = Field(default_factory=list, description="Optional sample input payloads or queries")
    sample_outputs: List[Any] = Field(default_factory=list, description="Optional sample output payloads or responses")


class SystemInput(BaseModel):
    """Legacy/extended system input specification."""
    system_name: str = Field(..., description="Name of the target AI System")
    problem_solved: str = Field(..., description="What problem or business need the AI system addresses")
    intended_use_case: str = Field(..., description="Detailed operational use case and domain")
    input_types: List[str] = Field(default_factory=list)
    output_types: List[str] = Field(default_factory=list)
    affected_stakeholders: List[str] = Field(default_factory=list)
    autonomy_level: str = Field(...)
    data_handled: List[str] = Field(default_factory=list)
    model_implementation_details: str = Field(...)
    potential_consequences: List[str] = Field(default_factory=list)
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
