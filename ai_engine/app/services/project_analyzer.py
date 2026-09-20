import json
from typing import Optional

from app.schemas.project import ProjectInput
from app.schemas.system_profile import SystemProfile
from app.core.llm import LLMClient, get_llm_client
from app.prompts.system_understanding import SYSTEM_UNDERSTANDING_PROMPT, SYSTEM_UNDERSTANDING_SYSTEM_PROMPT


class ProjectAnalyzer:
    """
    Decoupled service executing Project Understanding system profiling.
    Analyzes an individual AI project specification and builds a structured SystemProfile.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    def analyze_project(self, project_input: ProjectInput) -> SystemProfile:
        prompt = SYSTEM_UNDERSTANDING_PROMPT.format(
            project_name=project_input.project_name,
            description=project_input.description,
            github_url=project_input.github_url or "unknown",
            documentation=project_input.documentation or "unknown",
            sample_inputs=json.dumps(project_input.sample_inputs) if project_input.sample_inputs else "unknown",
            sample_outputs=json.dumps(project_input.sample_outputs) if project_input.sample_outputs else "unknown"
        )

        return self.llm.generate_structured(
            prompt=prompt,
            schema=SystemProfile,
            system_prompt=SYSTEM_UNDERSTANDING_SYSTEM_PROMPT
        )
