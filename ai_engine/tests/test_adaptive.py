import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.adaptive import AdaptiveDecision, AdaptiveIteration, RunAdaptiveInvestigationRequest
from app.services.adaptive_agent import AdaptiveInvestigationAgent
from app.core.llm import MockLLMClient

client = TestClient(app)


def get_sample_profile() -> SystemProfile:
    return SystemProfile(
        purpose="Analyze payment transaction velocity, IP geolocation, and amount to flag credit card fraud",
        intended_use="Automated fraud detection in payment processing gateway",
        ai_system_type="Automated Fraud Detection Classifier",
        model_type="Isolation Forest and XGBoost Ensemble",
        inputs=["Transaction Amount", "IP Country", "Transaction Velocity"],
        outputs=["Fraud Risk Score (0-1)", "Automated Action"],
        decision_process="Calculates risk score based on anomaly metrics",
        affected_users=["Cardholders", "Merchant Risk Analysts"],
        decision_impact="High - Immediate block of payment capability",
        autonomy_level="fully_autonomous_for_high_risk",
        data_types=["Payment Transaction Data", "IP Address"],
        sensitive_data=["Payment Card Identifiers", "Location Data"],
        external_services=["Payment Gateway API"],
        human_involvement="Asynchronous review of flagged transactions",
        deployment_context="Real-time payment transaction pipeline",
        expected_benefits=["Prevent real-time fraudulent charge loss"],
        potential_consequences=["Legitimate cardholder false decline during travel"],
        important_unknowns=["Threshold for auto-decline vs manual queue"],
        assumptions=["GeoIP database accuracy"],
        observed_evidence={"purpose": "Extracted from project description"}
    )


def get_sample_hypothesis() -> Hypothesis:
    return Hypothesis(
        id="HYP-F01",
        hypothesis="The transaction velocity auto-decline rule may falsely block legitimate cardholders traveling internationally.",
        why_it_is_plausible="System uses IP Country and Velocity to trigger fully autonomous auto-declines.",
        supporting_evidence=["Documentation states high velocity triggers auto-decline"],
        affected_part="Auto-decline decision engine",
        potential_consequence="Legitimate user disruption during international travel.",
        what_evidence_would_support_it=["Increased false decline rate when IP Country differs."],
        what_evidence_would_refute_it=["No change in decline rates for verified traveling users."],
        priority="medium",
        confidence=0.82
    )


# 1. Test Adaptive Decision Schema Validation
def test_adaptive_decision_schema_valid():
    decision = AdaptiveDecision(
        action="continue",
        reasoning="Initial observation showed slight variance.",
        evidence_summary="Baseline payload recorded.",
        remaining_uncertainties=["Does variance persist across amounts?"],
        next_question="Does the observed difference persist across multiple otherwise identical transactions?",
        confidence=0.75
    )
    assert decision.action == "continue"
    assert decision.next_question is not None


def test_adaptive_decision_schema_missing_next_question():
    with pytest.raises(ValueError):
        AdaptiveDecision(
            action="continue",
            reasoning="Test reasoning",
            evidence_summary="Evidence summary",
            remaining_uncertainties=[],
            next_question=None,  # Required when action='continue'
            confidence=0.5
        )


# 2 & 3. Test Adaptive Agent Loop Execution (Continue -> Step 2 -> Stop)
def test_adaptive_agent_loop_execution():
    agent = AdaptiveInvestigationAgent(llm_client=MockLLMClient())
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()

    result = agent.run_adaptive_loop(
        system_profile=profile,
        hypotheses=[hypothesis],
        available_tools=["modify_input", "compare_outputs"],
        max_iterations=5
    )

    assert result.status in ["completed", "max_iterations_reached", "insufficient_capability"]
    assert len(result.iterations) > 0
    first_iter = result.iterations[0]
    assert first_iter.iteration == 1
    assert first_iter.adaptive_decision is not None
    assert first_iter.adaptive_decision.action in ["continue", "stop"]


# 4. Test Max Iteration Enforcement
def test_max_iteration_limit_enforcement():
    agent = AdaptiveInvestigationAgent(llm_client=MockLLMClient())
    result = agent.run_adaptive_loop(
        system_profile=get_sample_profile(),
        hypotheses=[get_sample_hypothesis()],
        available_tools=["modify_input", "compare_outputs"],
        max_iterations=1
    )
    assert len(result.iterations) <= 1


# 5. Test Tool Unavailable Handling in Adaptive Agent
def test_unavailable_tool_in_adaptive_agent():
    agent = AdaptiveInvestigationAgent(llm_client=MockLLMClient())
    result = agent.run_adaptive_loop(
        system_profile=get_sample_profile(),
        hypotheses=[get_sample_hypothesis()],
        available_tools=["no_tools"],
        max_iterations=3
    )
    assert result.status in ["completed", "insufficient_capability"]
    assert len(result.limitations) > 0 or result.status == "insufficient_capability"


# 6. Test Evidence and Observation Trace Preservation
def test_evidence_and_observation_preservation():
    agent = AdaptiveInvestigationAgent(llm_client=MockLLMClient())
    result = agent.run_adaptive_loop(
        system_profile=get_sample_profile(),
        hypotheses=[get_sample_hypothesis()],
        available_tools=["modify_input", "compare_outputs"],
        initial_evidence=["Initial context evidence record"]
    )
    assert "Initial context evidence record" in result.final_evidence
    for iter_record in result.iterations:
        assert isinstance(iter_record.observations, list)
        assert iter_record.interpretation.hypothesis_status in ["supported", "weakened", "inconclusive"]


# 7. Test POST /engine/run-adaptive-investigation API Endpoint
def test_post_engine_run_adaptive_investigation_endpoint():
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()

    payload = {
        "system_profile": profile.model_dump(),
        "hypotheses": [hypothesis.model_dump()],
        "available_tools": ["modify_input", "compare_outputs"],
        "initial_evidence": ["Initial payload evidence"],
        "max_iterations": 3
    }

    response = client.post("/engine/run-adaptive-investigation", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "iterations" in data
    assert "final_evidence" in data
    assert isinstance(data["iterations"], list)
    assert len(data["iterations"]) > 0
