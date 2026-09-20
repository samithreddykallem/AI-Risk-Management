from typing import Optional
from ai_engine.models.system_input import ProjectInput
from ai_engine.models.system_profile import SystemProfile
from ai_engine.agents.profiler_agent import ProfilerAgent
from ai_engine.llm.base_provider import BaseLLMProvider


def analyze_project_service(
    project_input: ProjectInput,
    llm_provider: Optional[BaseLLMProvider] = None
) -> SystemProfile:
    """
    Decoupled service function executing Project Understanding profiling.
    Analyzes an individual AI project and returns a structured SystemProfile.
    """
    profiler = ProfilerAgent(llm_provider=llm_provider)
    return profiler.analyze_project(project_input)
