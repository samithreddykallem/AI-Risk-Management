import os
import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

import openai
from openai import OpenAI, APITimeoutError, APIError, AuthenticationError, RateLimitError

from ai_engine.llm.base_provider import BaseLLMProvider
from ai_engine.config.settings import settings

logger = logging.getLogger("ai_engine.llm")
T = TypeVar("T", bound=BaseModel)


class OpenAILLMProvider(BaseLLMProvider):
    """
    Isolated OpenAI-compatible LLM client integration.
    Supports standard text generation and structured JSON response parsing.
    Includes timeout enforcement and safe error handling without leaking API keys.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        self.api_key = api_key or settings.api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "LLM_API_KEY is not set. Please set the LLM_API_KEY environment variable in .env or environment."
            )

        self.base_url = base_url or settings.base_url
        self.model_name = model_name or settings.model_name
        self.timeout = timeout or settings.timeout_seconds

        # Initialize isolated OpenAI client instance
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def _mask_key(self, key: str) -> str:
        """Helper to safely mask API key for logging purposes."""
        if not key or len(key) < 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text completion from OpenAI API with timeout and error handling."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                timeout=self.timeout
            )
            content = response.choices[0].message.content
            return content or ""

        except APITimeoutError as e:
            logger.error("LLM Request timed out after %s seconds.", self.timeout)
            raise RuntimeError(f"LLM API request timed out after {self.timeout}s.") from e

        except AuthenticationError as e:
            logger.error("LLM Authentication failed. Check your API key.")
            raise RuntimeError("LLM API Authentication failed. Please verify LLM_API_KEY.") from e

        except RateLimitError as e:
            logger.error("LLM Rate limit exceeded.")
            raise RuntimeError("LLM API rate limit exceeded.") from e

        except APIError as e:
            # Clean error string ensuring key is never leaked
            logger.error("LLM API error occurred: %s", getattr(e, "message", str(e)))
            raise RuntimeError(f"LLM API error: {getattr(e, 'message', str(e))}") from e

        except Exception as e:
            logger.error("Unexpected error during LLM text generation.")
            raise RuntimeError("An unexpected error occurred during LLM text generation.") from e

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: Optional[str] = None) -> T:
        """
        Generate structured response matching the specified Pydantic schema.
        Uses json_object response format with schema instructions.
        """
        schema_json = schema.model_json_schema()
        system_instruction = (
            f"{system_prompt or ''}\n"
            "You MUST respond ONLY with valid JSON matching the following JSON schema:\n"
            f"{json.dumps(schema_json, indent=2)}\n"
            "Do not include markdown formatting or backticks around the JSON."
        ).strip()

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                timeout=self.timeout
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM returned empty output for structured schema.")

            # Parse JSON content into Pydantic model
            data = json.loads(content)
            return schema.model_validate(data)

        except APITimeoutError as e:
            logger.error("LLM Request timed out during structured output generation.")
            raise RuntimeError(f"LLM request timed out after {self.timeout}s.") from e

        except (APIError, json.JSONDecodeError) as e:
            logger.error("Error generating or parsing structured LLM output.")
            raise RuntimeError(f"Failed to generate structured LLM response: {str(e)}") from e
