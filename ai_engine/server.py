import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from ai_engine.models.system_input import ProjectInput
from ai_engine.models.system_profile import SystemProfile
from ai_engine.services.project_service import analyze_project_service
from ai_engine.llm.provider_factory import get_llm_provider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_engine.server")

app = FastAPI(
    title="AI Risk Manager - AI Engine API",
    description="Adaptive Ethical Auditor for AI Systems API",
    version="0.1.0"
)


class TestLLMRequest(BaseModel):
    message: str = Field(..., json_schema_extra={"example": "Say hello"}, description="Input message query for the LLM")


class TestLLMResponse(BaseModel):
    response: str = Field(..., description="Response text returned from the LLM")


@app.post(
    "/engine/test-llm",
    response_model=TestLLMResponse,
    status_code=status.HTTP_200_OK,
    summary="Test LLM Provider Connectivity"
)
async def test_llm_endpoint(payload: TestLLMRequest):
    """
    Test endpoint to verify LLM client integration and connectivity.
    Reads API key securely from environment variables. Never exposes API keys.
    """
    try:
        logger.info("Processing /engine/test-llm request...")
        llm = get_llm_provider()
        
        system_prompt = "You are a helpful assistant. Keep your response clear and concise."
        output_text = llm.generate_text(prompt=payload.message, system_prompt=system_prompt)
        
        return TestLLMResponse(response=output_text)

    except Exception as e:
        logger.error("Error processing test-llm request: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM request processing failed: {str(e)}"
        )


@app.post(
    "/engine/analyze-project",
    response_model=SystemProfile,
    status_code=status.HTTP_200_OK,
    summary="Analyze AI Project and Generate System Profile"
)
async def analyze_project_endpoint(payload: ProjectInput):
    """
    Analyzes an individual AI project specification and builds a structured System Profile.
    Does not use fixed domain checklists; reasons directly from submitted project evidence.
    Returns 'unknown' for unstated information.
    """
    try:
        logger.info("Processing /engine/analyze-project request for project: %s", payload.project_name)
        profile = analyze_project_service(payload)
        return profile

    except Exception as e:
        logger.error("Error analyzing project '%s': %s", payload.project_name, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze project: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
