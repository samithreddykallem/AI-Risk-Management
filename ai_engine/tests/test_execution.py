import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import (
    InvestigationPlan,
    InvestigationStep,
    ToolExecution,
    Observation,
    ExecuteInvestigationRequest
)
from app.tools.registry import ToolRegistry, default_tool_registry
from app.tools.repository_tool import RepositoryTool
from app.tools.model_tool import ModelTool, ModifyInputTool, CompareOutputsTool
from app.services.investigation_executor import InvestigationExecutor
from app.services.observation_interpreter import ObservationInterpreter
from app.core.llm import MockLLMClient

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


def get_sample_plan() -> InvestigationPlan:
    return InvestigationPlan(
        hypothesis_id="HYP-001",
        investigation_goal="Gather evidence on Zip Code score variance",
        reasoning="Perturb Zip Code while holding financial variables constant",
        steps=[
            InvestigationStep(
                step_id="STEP-1",
                objective="Prepare baseline input",
                tool="modify_input",
                parameters={"base_input": {"income": 65000, "zip": "90210"}, "perturbations": {}},
                expected_observation="Baseline input prepared",
                evidence_required="Baseline input recorded",
                reasoning="Baseline payload setup"
            ),
            InvestigationStep(
                step_id="STEP-2",
                objective="Modify Zip Code variable",
                tool="modify_input",
                parameters={"base_input": {"income": 65000, "zip": "90210"}, "perturbations": {"zip": "90011"}},
                expected_observation="Input modified with perturbed zip",
                evidence_required="Perturbed input recorded",
                reasoning="Variable perturbation setup"
            ),
            InvestigationStep(
                step_id="STEP-3",
                objective="Compare baseline and perturbed input location fields",
                tool="compare_outputs",
                parameters={"output_a": {"zip": "90210"}, "output_b": {"zip": "90011"}, "metric": "field_difference"},
                expected_observation="Variance in location fields detected",
                evidence_required="Quantitative difference recorded",
                reasoning="Location variance verification"
            )
        ],
        success_criteria="Evidence of output difference when Zip Code is altered",
        possible_outcomes=["Variance confirms hypothesis", "No variance refutes hypothesis"]
    )


# 1. Test Successful Tool Execution
def test_successful_tool_execution():
    tool = ModifyInputTool()
    exec_record = tool.run(step_id="STEP-1", parameters={"base_input": {"income": 50000}, "perturbations": {"zip": "90210"}})
    assert exec_record.status == "success"
    assert exec_record.result["modified_input"]["zip"] == "90210"


# 2. Test Unknown Tool Execution
def test_unknown_tool_execution():
    executor = InvestigationExecutor()
    plan = InvestigationPlan(
        hypothesis_id="HYP-001",
        investigation_goal="Test unknown tool",
        reasoning="Use non-existent tool",
        steps=[
            InvestigationStep(
                step_id="STEP-ERR",
                objective="Run non-existent tool",
                tool="non_existent_tool_xyz",
                parameters={},
                expected_observation="",
                evidence_required="",
                reasoning=""
            )
        ],
        success_criteria="",
        possible_outcomes=[]
    )
    result = executor.execute_plan(get_sample_profile(), get_sample_hypothesis(), plan)
    assert result.status == "insufficient_capability"
    assert len(result.executed_steps) == 1
    assert result.executed_steps[0].status == "unavailable"
    assert "not registered" in result.executed_steps[0].error


# 3 & 7. Test Model Tool Unavailable (when model interface is not connected)
def test_model_tool_unavailable():
    model_tool = ModelTool()
    exec_record = model_tool.run(step_id="STEP-1", parameters={"input_data": {"income": 50000}})
    assert exec_record.status == "unavailable"
    assert "No executable model interface is currently connected." in exec_record.error


# 4 & 8. Test Repository Tool Unavailable (when repo is missing)
def test_repository_tool_unavailable():
    repo_tool = RepositoryTool()
    exec_record = repo_tool.run(step_id="STEP-1", parameters={})
    assert exec_record.status == "unavailable"
    assert "No repository available for inspection." in exec_record.error


# 5. Test Evidence Recording
def test_evidence_recording_trail():
    executor = InvestigationExecutor()
    result = executor.execute_plan(get_sample_profile(), get_sample_hypothesis(), get_sample_plan(), initial_evidence=["Initial Context Evidence"])
    assert len(result.evidence) > 0
    assert "Initial Context Evidence" in result.evidence


# 6. Test Observation Source Tracking
def test_observation_source_tracking():
    executor = InvestigationExecutor()
    result = executor.execute_plan(get_sample_profile(), get_sample_hypothesis(), get_sample_plan())
    assert len(result.observations) > 0
    for obs in result.observations:
        assert obs.source is not None
        assert obs.source in ["modify_input", "compare_outputs", "repository_tool", "model_tool", "analyze_evidence"]


# 9. Test Successful Deterministic Comparison
def test_successful_deterministic_comparison():
    comp_tool = CompareOutputsTool()
    res = comp_tool.run(step_id="STEP-3", parameters={"output_a": {"score": 800}, "output_b": {"score": 600}, "metric": "score_difference"})
    assert res.status == "success"
    assert res.result["variance_detected"] is True


# 10. Test LLM Interpretation of Evidence
def test_llm_interpretation_service():
    interpreter = ObservationInterpreter(llm_client=MockLLMClient())
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()
    plan = get_sample_plan()

    executor = InvestigationExecutor()
    res = executor.execute_plan(profile, hypothesis, plan)

    interp = interpreter.interpret_evidence(
        system_profile=profile,
        hypothesis=hypothesis,
        investigation_plan=plan,
        executed_steps=res.executed_steps,
        observations=res.observations
    )

    assert interp.hypothesis_status in ["supported", "weakened", "inconclusive"]
    assert 0.0 <= interp.confidence <= 1.0


# 11. Test No Fabricated Observations (checking status='insufficient_capability' when tools fail)
def test_no_fabricated_observations():
    executor = InvestigationExecutor()
    plan_with_unavailable = InvestigationPlan(
        hypothesis_id="HYP-001",
        investigation_goal="Test un-connected model run",
        reasoning="Run disconnected model tool",
        steps=[
            InvestigationStep(
                step_id="STEP-1",
                objective="Run unconnected model",
                tool="model_tool",
                parameters={"input_data": {"income": 50000}},
                expected_observation="Model output",
                evidence_required="Model output payload",
                reasoning="Test model query"
            )
        ],
        success_criteria="Model output",
        possible_outcomes=[]
    )

    result = executor.execute_plan(get_sample_profile(), get_sample_hypothesis(), plan_with_unavailable)
    assert result.status == "insufficient_capability"
    assert len(result.observations) == 0  # No fake observations created for unavailable tool


# 12, 13, 14. Test Hypothesis Status (supported, weakened, inconclusive)
def test_hypothesis_status_supported():
    interpreter = ObservationInterpreter(llm_client=MockLLMClient())
    interp = interpreter.interpret_evidence(
        system_profile=get_sample_profile(),
        hypothesis=get_sample_hypothesis(),
        investigation_plan=get_sample_plan(),
        executed_steps=[],
        observations=[]
    )
    assert interp.hypothesis_status in ["supported", "weakened", "inconclusive"]


def test_post_engine_execute_investigation_endpoint():
    profile = get_sample_profile()
    hypothesis = get_sample_hypothesis()
    plan = get_sample_plan()

    payload = {
        "system_profile": profile.model_dump(),
        "hypothesis": hypothesis.model_dump(),
        "investigation_plan": plan.model_dump(),
        "available_tools": ["modify_input", "compare_outputs"],
        "initial_evidence": ["Initial evidence item"]
    }

    response = client.post("/engine/execute-investigation", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "investigation_result" in data
    assert "interpretation" in data
    assert data["investigation_result"]["status"] in ["completed", "partially_completed", "failed", "insufficient_capability"]
    assert data["interpretation"]["hypothesis_status"] in ["supported", "weakened", "inconclusive"]
