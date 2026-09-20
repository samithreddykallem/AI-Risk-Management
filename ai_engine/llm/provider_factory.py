import logging
from ai_engine.llm.base_provider import BaseLLMProvider
from ai_engine.llm.mock_provider import MockLLMProvider
from ai_engine.llm.openai_provider import OpenAILLMProvider
from ai_engine.config.settings import settings

logger = logging.getLogger("ai_engine.llm")


def get_llm_provider(provider_type: str = None, model_name: str = None) -> BaseLLMProvider:
    """
    Factory function to retrieve initialized LLM Provider instance.
    Defaults to OpenAILLMProvider if API key is present, or MockLLMProvider if mock is specified/no API key exists.
    """
    selected_provider = (provider_type or settings.provider_type).lower()

    if selected_provider == "openai" or (settings.api_key and selected_provider != "mock"):
        try:
            return OpenAILLMProvider(model_name=model_name)
        except Exception as e:
            logger.warning("Failed to initialize OpenAILLMProvider (%s). Falling back to MockLLMProvider.", str(e))
            return MockLLMProvider()

    return MockLLMProvider()
