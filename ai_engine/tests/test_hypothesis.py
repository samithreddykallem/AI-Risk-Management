import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis, HypothesisGenerationRequest, HypothesisGenerationResponse
from app.services.hypothesis_generator import HypothesisGenerator

client = TestClient(app)


def get_sample_profile() -> SystemProfile:
    return SystemProfile(
        purpose="Automate credit risk scoring",
        intended_use="Evaluating consumer loan applications",
        ai_system_type="Decision Support System",
        model_type="Gradient Boosting Classifier",
        inputs=["Income", "Credit History", "Zip Code"],
        outputs=["Credit Risk Score"],
        decision_process="Calculates risk score using GBDT",
        affected_users=["Loan Applicants"],
        decision_impact="High - financial access",
        autonomy_level="human_in_the_loop",
        data_types=["Financial History", "PII"],
        sensitive_data=["Zip Code (Proxy)"],
        external_services=["Credit Bureau API"],
        human_involvement="Loan officer review",
        deployment_context="Internal portal",
        expected_benefits=["Faster loan decisioning"],
        potential_consequences=["Demographic proxy discrimination"],
        important_unknowns=["Training data demographic breakdown"],
        assumptions=["Credit bureau data is accurate"],
        observed_evidence={"purpose": "Extracted from project description"}
    )


def test_hypothesis_schema_validation_valid():
    hyp = Hypothesis(
        id="HYP-101",
        hypothesis="Zip code variable causes proxy demographic discrimination.",
        why_it_is_plausible="System handles Zip Code as input alongside financial variables.",
        supporting_evidence=["Input contains Zip Code"],
        affected_part="Input processing",
        potential_consequence="Wrongful loan denial",
        what_evidence_would_support_it=["Score drop when only Zip Code changes"],
        what_evidence_would_refute_it=["Identical score across zip codes"],
        priority="high",
        confidence=0.85
    )
    assert hyp.priority == "high"
    assert hyp.confidence == 0.85


def test_hypothesis_schema_validation_invalid_confidence():
    with pytest.raises(ValidationError):
        Hypothesis(
            id="HYP-102",
            hypothesis="Test invalid confidence",
            why_it_is_plausible="Test",
            supporting_evidence=[],
            affected_part="Input",
            potential_consequence="None",
            what_evidence_would_support_it=[],
            what_evidence_would_refute_it=[],
            priority="medium",
            confidence=1.5  # Invalid: > 1.0
        )


def test_hypothesis_schema_validation_invalid_priority():
    with pytest.raises(ValidationError):
        Hypothesis(
            id="HYP-103",
            hypothesis="Test invalid priority",
            why_it_is_plausible="Test",
            supporting_evidence=[],
            affected_part="Input",
            potential_consequence="None",
            what_evidence_would_support_it=[],
            what_evidence_would_refute_it=[],
            priority="critical",  # Invalid: must be low, medium, high
            confidence=0.5
        )


def test_hypothesis_generator_service():
    generator = HypothesisGenerator()
    profile = get_sample_profile()
    response = generator.generate_hypotheses(system_profile=profile)
    assert isinstance(response, HypothesisGenerationResponse)
    assert len(response.hypotheses) > 0
    assert response.hypotheses[0].priority in ["low", "medium", "high"]


def test_post_engine_generate_hypotheses_endpoint():
    profile = get_sample_profile()
    payload = {
        "system_profile": profile.model_dump(),
        "available_evidence": ["Evidence string 1"],
        "important_unknowns": ["Unknown item 1"]
    }
    response = client.post("/engine/generate-hypotheses", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "hypotheses" in data
    assert isinstance(data["hypotheses"], list)


def test_empty_hypothesis_response():
    """Test that hypothesis generator returns an empty list when LLM justifies no hypotheses."""
    from app.core.llm import MockLLMClient
    generator = HypothesisGenerator(llm_client=MockLLMClient())
    vague_profile = get_sample_profile()
    vague_profile.deployment_context = "vague - no documentation provided"
    
    response = generator.generate_hypotheses(system_profile=vague_profile)
    assert isinstance(response, HypothesisGenerationResponse)
    assert response.hypotheses == []


def test_invalid_llm_json_handling_hypothesis():
    """Test clean error handling when LLM returns invalid JSON or fails generation."""
    class FailingLLMClient:
        def generate_structured(self, prompt, schema, system_prompt=None):
            raise RuntimeError("Failed to generate structured LLM response: Invalid JSON")

    generator = HypothesisGenerator(llm_client=FailingLLMClient())
    profile = get_sample_profile()
    
    with pytest.raises(RuntimeError) as exc_info:
        generator.generate_hypotheses(system_profile=profile)
    
    assert "Hypothesis generation failed" in str(exc_info.value)

