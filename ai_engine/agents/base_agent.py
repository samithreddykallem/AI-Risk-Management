from typing import Optional
from ai_engine.llm.base_provider import BaseLLMProvider
from ai_engine.llm.provider_factory import get_llm_provider


class BaseAgent:
    """Base class for all AI Engine Auditor Agents."""

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()
