import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import (
    InvestigationStep,
    InvestigationPlan,
    PlanInvestigationRequest,
    PlanInvestigationResponse
)
from app.services.investigation_planner import InvestigationPlanner
from app.tools import inspect_repository, run_model, modify_input, compare_outputs, analyze_evidence

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


def get_sample_hypothesis() -> Hypothesis:
    return Hypothesis(
        id="HYP-001",
        hypothesis="The scoring model may produce lower credit risk scores for applicants in certain zip codes.",
        why_it_is_plausible="System handles Zip Code as input parameter alongside financial metrics.",
        supporting_evidence=["Input includes Zip Code"],
        affected_part="Input processing and score calculation",
        potential_consequence="Disparate financial impact on applicants.",
        what_evidence_would_support_it=["Score drop when only Zip Code changes"],
        what_evidence_would_refute_it=["Identical score across zip codes"],
        priority="high",
        confidence=0.85
    )


def test_investigation_plan_schema_validation():
    step = InvestigationStep(
        step_id="STEP-1",
        objective="Establish baseline score",
        tool="run_model",
        parameters={"input_data": {"zip": "90210"}},
        expected_observation="Score returned",
        evidence_required="Score recorded",
        reasoning="Baseline measurement"
    )
    plan = InvestigationPlan(
        hypothesis_id="HYP-001",
        investigation_goal="Test zip code sensitivity",
        reasoning="Perturb zip code while holding income constant",
        steps=[step],
        success_criteria="Score variance observed",
        possible_outcomes=["Bias confirmed", "Bias refuted"]
    )
    assert plan.hypothesis_id == "HYP-001"
    assert len(plan.steps) == 1


def test_tool_abstraction_layer_executions():
    # Test safe tool execution records
    repo_rec = inspect_repository(file_path="src/model.py")
    assert repo_rec.tool == "repository_tool"
    assert repo_rec.status in ["success", "placeholder_simulation", "unavailable"]

    run_rec = run_model(input_data={"income": 50000})
    assert run_rec.tool == "model_tool"
    assert run_rec.status in ["placeholder_simulation", "unavailable"]

    mod_rec = modify_input(base_input={"income": 50000}, perturbations={"zip": "90210"})
    assert mod_rec.result["modified_input"]["zip"] == "90210"

    comp_rec = compare_outputs(output_a=800, output_b=600)
    assert comp_rec.result["variance_detected"] is True

    ana_rec = analyze_evidence(evidence_items=["Item 1"], focus_area="Fairness")
    assert ana_rec.result["evidence_count"] == 1


def test_investigation_planner_service():
    planner = InvestigationPlanner()
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()

    response = planner.plan_investigation(
        system_profile=profile,
        hypothesis=hypothesis,
        available_tools=["run_model", "modify_input", "compare_outputs"]
    )
    assert isinstance(response, PlanInvestigationResponse)
    assert response.status in ["ready", "insufficient_capability"]
    if response.status == "ready":
        assert response.investigation_plan is not None
        assert response.investigation_plan.hypothesis_id == "HYP-001"


def test_post_engine_plan_investigation_endpoint():
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()
    payload = {
        "system_profile": profile.model_dump(),
        "hypothesis": hypothesis.model_dump(),
        "available_tools": ["run_model", "modify_input", "compare_outputs"],
        "existing_evidence": ["Evidence string 1"]
    }
    response = client.post("/engine/plan-investigation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["ready", "insufficient_capability"]


def test_insufficient_investigation_capability():
    """Test investigation planner when available tools cannot investigate hypothesis."""
    from app.core.llm import MockLLMClient
    planner = InvestigationPlanner(llm_client=MockLLMClient())
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()
    
    response = planner.plan_investigation(
        system_profile=profile,
        hypothesis=hypothesis,
        available_tools=["insufficient_tools"]
    )
    assert response.status == "insufficient_capability"
    assert response.investigation_plan is None
    assert response.reason is not None


def test_invalid_llm_json_handling_investigation():
    """Test clean error handling when LLM returns invalid JSON during investigation planning."""
    class FailingLLMClient:
        def generate_structured(self, prompt, schema, system_prompt=None):
            raise RuntimeError("Failed to generate structured LLM response: Invalid JSON")

    planner = InvestigationPlanner(llm_client=FailingLLMClient())
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()
    
    with pytest.raises(RuntimeError) as exc_info:
        planner.plan_investigation(
            system_profile=profile,
            hypothesis=hypothesis,
            available_tools=["modify_input"]
        )
    
    assert "Investigation planning failed" in str(exc_info.value)

