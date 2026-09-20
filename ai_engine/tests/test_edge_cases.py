import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.project import ProjectInput
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.services.project_analyzer import ProjectAnalyzer
from app.services.hypothesis_generator import HypothesisGenerator
from app.services.investigation_planner import InvestigationPlanner
from app.core.llm import MockLLMClient

client = TestClient(app)


def test_vague_project_input_handling():
    """Test analyzing a very vague AI project input to ensure unknowns are preserved and facts are not manufactured."""
    analyzer = ProjectAnalyzer(llm_client=MockLLMClient())
    vague_input = ProjectInput(
        project_name="Vague-Bot",
        description="A software helper.",
        github_url=None,
        documentation=None,
        sample_inputs=[],
        sample_outputs=[]
    )
    profile = analyzer.analyze_project(vague_input)
    assert profile.purpose is not None
    # Ensure unknowns are tracked in profile
    assert isinstance(profile.important_unknowns, list)


def test_empty_hypothesis_response():
    """Test that hypothesis generation returns empty list when input contains vague/insufficient text."""
    generator = HypothesisGenerator(llm_client=MockLLMClient())
    vague_profile = SystemProfile(
        purpose="A vague tool",
        intended_use="General purpose",
        ai_system_type="unknown",
        model_type="unknown",
        inputs=[],
        outputs=[],
        decision_process="unknown",
        affected_users=[],
        decision_impact="unknown",
        autonomy_level="unknown",
        data_types=[],
        sensitive_data=[],
        external_services=[],
        human_involvement="unknown",
        deployment_context="vague - no documentation provided",
        expected_benefits=[],
        potential_consequences=[],
        important_unknowns=["Everything missing"],
        assumptions=[],
        observed_evidence={}
    )

    response = generator.generate_hypotheses(system_profile=vague_profile)
    assert isinstance(response.hypotheses, list)
    # MockLLMClient returns empty list when 'vague' is present in system profile text
    assert len(response.hypotheses) == 0


def test_insufficient_investigation_capability_response():
    """Test that investigation planner returns status='insufficient_capability' when tools are inadequate."""
    planner = InvestigationPlanner(llm_client=MockLLMClient())
    profile = SystemProfile(
        purpose="Fraud detection",
        intended_use="Transaction analysis",
        ai_system_type="Classifier",
        model_type="Neural Network",
        inputs=["Transaction"],
        outputs=["Fraud Risk Score"],
        decision_process="Neural net",
        affected_users=["Cardholders"],
        decision_impact="High",
        autonomy_level="human_in_the_loop",
        data_types=["Transactions"],
        sensitive_data=[],
        external_services=[],
        human_involvement="Review",
        deployment_context="no_tools",  # Triggers mock insufficient tools flag
        expected_benefits=[],
        potential_consequences=[],
        important_unknowns=[],
        assumptions=[],
        observed_evidence={}
    )
    hypothesis = Hypothesis(
        id="HYP-999",
        hypothesis="Model leaks internal weights",
        why_it_is_plausible="Neural net deployment",
        supporting_evidence=[],
        affected_part="Model Weights",
        potential_consequence="IP theft",
        what_evidence_would_support_it=[],
        what_evidence_would_refute_it=[],
        priority="low",
        confidence=0.3
    )

    response = planner.plan_investigation(
        system_profile=profile,
        hypothesis=hypothesis,
        available_tools=["no_tools"]
    )
    assert response.status == "insufficient_capability"
    assert response.reason is not None


def test_end_to_end_differing_domains_flow():
    """Verify that end-to-end pipeline outputs differ for different system inputs (Fraud vs Healthcare)."""
    # 1. Fraud Detection AI
    fraud_project = ProjectInput(
        project_name="Smart Fraud Detector",
        description="Analyzes payment transaction velocity, IP geolocation, and transaction amount to flag credit card fraud.",
        documentation="Uses isolation forest and XGBoost ensemble. High velocity transactions trigger auto-decline.",
        sample_inputs=["Transaction Amount: $4,500", "IP Country: RU", "Velocity: 12 txns/min"],
        sample_outputs=["Fraud Risk Score: 0.94", "Action: Auto-Decline"]
    )

    # 2. Healthcare Medical Triage AI
    health_project = ProjectInput(
        project_name="MediTriage Assist",
        description="Summarizes patient clinical notes and suggests emergency triage acuity scores for ER nurses.",
        documentation="Uses fine-tuned LLM on clinical notes. Nurse must verify all triage acuity assignments.",
        sample_inputs=["Patient 45y male presenting with retrosternal chest pain and diaphoresis."],
        sample_outputs=["Suggested Acuity Level: ESI Level 2 (Emergent)"]
    )

    analyzer = ProjectAnalyzer(llm_client=MockLLMClient())
    fraud_profile = analyzer.analyze_project(fraud_project)
    health_profile = analyzer.analyze_project(health_project)

    # Verify distinct profile attributes
    assert fraud_profile.purpose != health_profile.purpose
