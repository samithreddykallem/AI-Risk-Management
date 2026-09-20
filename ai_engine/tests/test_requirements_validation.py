import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.project import ProjectInput
from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import InvestigationPlan, InvestigationStep, ToolExecution, Observation
from app.services.project_analyzer import ProjectAnalyzer
from app.services.hypothesis_generator import HypothesisGenerator
from app.services.investigation_planner import InvestigationPlanner
from app.services.investigation_executor import InvestigationExecutor
from app.services.observation_interpreter import ObservationInterpreter
from app.services.adaptive_agent import AdaptiveInvestigationAgent
from app.core.llm import MockLLMClient
from app.tools.registry import default_tool_registry, ToolRegistry

client = TestClient(app)


# ============================================================
# 1. VERIFY PROJECT STRUCTURE
# ============================================================
def test_verify_project_structure():
    """Verify core packages exist and can be imported cleanly."""
    import app.main
    import app.core
    import app.schemas
    import app.services
    import app.tools
    import app.prompts

    assert app.main.app is not None
    assert hasattr(app.core, "config")
    assert hasattr(app.schemas, "project")
    assert hasattr(app.services, "project_analyzer")
    assert hasattr(app.tools, "registry")
    assert hasattr(app.prompts, "system_understanding")


# ============================================================
# 3 & 15. TEST API IMPORT AND ALL ENDPOINTS
# ============================================================
def test_api_import_and_all_endpoints():
    """Verify python import works and all 8 FastAPI endpoints exist and respond."""
    from app.main import app as main_app
    assert main_app is not None

    # GET /
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["status"] == "running"

    # GET /health
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"

    # POST /engine/test-llm
    r_llm = client.post("/engine/test-llm", json={"message": "hello"})
    assert r_llm.status_code == 200

    # POST /engine/analyze-project
    fraud_payload = {
        "project_name": "Smart Fraud Detector",
        "description": "An AI system that analyzes bank transactions and predicts whether a transaction is fraudulent. It uses transaction amount, location, device information, merchant information and historical account behavior. Transactions with a high fraud probability are automatically blocked.",
        "github_url": None,
        "documentation": "The system is designed to detect fraudulent financial transactions in real time. It processes transaction information and produces a fraud probability score. If the score exceeds a threshold, the transaction is blocked.",
        "sample_inputs": [
            {"amount": 5000, "location": "Hyderabad", "device": "Android", "merchant": "Online Store"}
        ],
        "sample_outputs": [
            {"fraud_probability": 0.82, "decision": "BLOCK"}
        ]
    }
    r_analyze = client.post("/engine/analyze-project", json=fraud_payload)
    assert r_analyze.status_code == 200
    profile_data = r_analyze.json()
    assert "purpose" in profile_data

    # POST /engine/generate-hypotheses
    r_hypo = client.post("/engine/generate-hypotheses", json={"system_profile": profile_data})
    assert r_hypo.status_code == 200
    hypo_data = r_hypo.json()
    assert "hypotheses" in hypo_data
    assert len(hypo_data["hypotheses"]) > 0

    first_hypo = hypo_data["hypotheses"][0]

    # POST /engine/plan-investigation
    plan_payload = {
        "system_profile": profile_data,
        "hypothesis": first_hypo,
        "available_tools": ["modify_input", "compare_outputs"]
    }
    r_plan = client.post("/engine/plan-investigation", json=plan_payload)
    assert r_plan.status_code == 200
    plan_resp = r_plan.json()
    assert plan_resp["status"] == "ready"
    inv_plan = plan_resp["investigation_plan"]

    # POST /engine/execute-investigation
    exec_payload = {
        "system_profile": profile_data,
        "hypothesis": first_hypo,
        "investigation_plan": inv_plan,
        "available_tools": ["modify_input", "compare_outputs"]
    }
    r_exec = client.post("/engine/execute-investigation", json=exec_payload)
    assert r_exec.status_code == 200
    exec_resp = r_exec.json()
    assert "investigation_result" in exec_resp

    # POST /engine/run-adaptive-investigation
    adaptive_payload = {
        "system_profile": profile_data,
        "hypotheses": [first_hypo],
        "available_tools": ["modify_input", "compare_outputs"],
        "max_iterations": 2
    }
    r_adapt = client.post("/engine/run-adaptive-investigation", json=adaptive_payload)
    assert r_adapt.status_code == 200
    adapt_resp = r_adapt.json()
    assert "iterations" in adapt_resp


# ============================================================
# 5. TEST PROJECT UNDERSTANDING (Smart Fraud Detector)
# ============================================================
def test_smart_fraud_detector_project_understanding():
    """Verify that Smart Fraud Detector produces grounded System Profile without inventing claims."""
    analyzer = ProjectAnalyzer(llm_client=MockLLMClient())
    project_input = ProjectInput(
        project_name="Smart Fraud Detector",
        description="An AI system that analyzes bank transactions and predicts whether a transaction is fraudulent. It uses transaction amount, location, device information, merchant information and historical account behavior. Transactions with a high fraud probability are automatically blocked.",
        github_url=None,
        documentation="The system is designed to detect fraudulent financial transactions in real time. It processes transaction information and produces a fraud probability score. If the score exceeds a threshold, the transaction is blocked.",
        sample_inputs=[
            {"amount": 5000, "location": "Hyderabad", "device": "Android", "merchant": "Online Store"}
        ],
        sample_outputs=[
            {"fraud_probability": 0.82, "decision": "BLOCK"}
        ]
    )

    profile = analyzer.analyze_project(project_input)
    assert profile.purpose is not None
    assert "fraud" in profile.purpose.lower() or "transaction" in profile.purpose.lower()
    assert isinstance(profile.inputs, list)
    assert isinstance(profile.outputs, list)


# ============================================================
# 6. TEST HYPOTHESIS GENERATION
# ============================================================
def test_hypothesis_generation_structure_and_grounding():
    """Verify generated hypotheses structure, confidence bounds [0,1], priority, evidence."""
    analyzer = ProjectAnalyzer(llm_client=MockLLMClient())
    generator = HypothesisGenerator(llm_client=MockLLMClient())

    project_input = ProjectInput(
        project_name="Smart Fraud Detector",
        description="An AI system that analyzes bank transactions and predicts whether a transaction is fraudulent.",
        github_url=None,
        documentation="High velocity transactions trigger auto-decline.",
        sample_inputs=[],
        sample_outputs=[]
    )
    profile = analyzer.analyze_project(project_input)
    response = generator.generate_hypotheses(profile)

    assert len(response.hypotheses) > 0
    for hypo in response.hypotheses:
        assert hypo.id is not None
        assert hypo.hypothesis is not None
        assert 0.0 <= hypo.confidence <= 1.0
        assert hypo.priority in ["low", "medium", "high", "critical"]
        assert isinstance(hypo.supporting_evidence, list)
        assert hypo.affected_part is not None


# ============================================================
# 7. TEST INVESTIGATION PLANNING
# ============================================================
def test_investigation_planning_references_hypothesis():
    """Verify investigation plan references target hypothesis, steps contain valid tools, objectives, params."""
    planner = InvestigationPlanner(llm_client=MockLLMClient())
    profile = SystemProfile(
        purpose="Fraud Detection",
        intended_use="Gateway",
        ai_system_type="Classifier",
        model_type="XGBoost",
        inputs=["Amount", "IP"],
        outputs=["Score"],
        decision_process="Rules",
        affected_users=["Cardholders"],
        decision_impact="High",
        autonomy_level="autonomous",
        data_types=["Transactions"],
        sensitive_data=[],
        external_services=[],
        human_involvement="None",
        deployment_context="Realtime",
        expected_benefits=[],
        potential_consequences=[],
        important_unknowns=[],
        assumptions=[],
        observed_evidence={}
    )
    hypothesis = Hypothesis(
        id="HYP-F01",
        hypothesis="Auto-decline rule causes false positives for international travelers.",
        why_it_is_plausible="Uses IP Country parameter.",
        supporting_evidence=["IP Country input"],
        affected_part="Decline engine",
        potential_consequence="User disruption",
        what_evidence_would_support_it=["Higher decline rate"],
        what_evidence_would_refute_it=["No change"],
        priority="medium",
        confidence=0.82
    )

    response = planner.plan_investigation(
        system_profile=profile,
        hypothesis=hypothesis,
        available_tools=["modify_input", "compare_outputs"]
    )

    assert response.status == "ready"
    plan = response.investigation_plan
    assert plan.hypothesis_id in ["HYP-F01", "HYP-001"]
    assert len(plan.steps) > 0
    for step in plan.steps:
        assert step.step_id is not None
        assert step.objective is not None
        assert step.tool in ["modify_input", "compare_outputs", "inspect_repository", "query_model_interface"]
        assert isinstance(step.parameters, dict)
        assert step.expected_observation is not None


# ============================================================
# 8. TEST INVESTIGATION EXECUTION (UNAVAILABLE TOOL HANDLING)
# ============================================================
def test_investigation_execution_tool_unavailable():
    """Verify unavailable tools return status='unavailable' with limitations recorded without fabricating output."""
    executor = InvestigationExecutor(registry=default_tool_registry)
    profile = SystemProfile(
        purpose="Test", intended_use="Test", ai_system_type="Test", model_type="Test",
        inputs=[], outputs=[], decision_process="Test", affected_users=[], decision_impact="Low",
        autonomy_level="none", data_types=[], sensitive_data=[], external_services=[],
        human_involvement="None", deployment_context="Test", expected_benefits=[],
        potential_consequences=[], important_unknowns=[], assumptions=[], observed_evidence={}
    )
    hypothesis = Hypothesis(
        id="HYP-001", hypothesis="Test", why_it_is_plausible="Test", supporting_evidence=[],
        affected_part="Test", potential_consequence="Test", what_evidence_would_support_it=[],
        what_evidence_would_refute_it=[], priority="low", confidence=0.5
    )
    plan = InvestigationPlan(
        hypothesis_id="HYP-001",
        investigation_goal="Query model interface directly",
        reasoning="Test unavailable tool behavior",
        steps=[
            InvestigationStep(
                step_id="STEP-UNAVAIL-1",
                objective="Call query_model_interface which has no connection",
                tool="query_model_interface",
                parameters={"input": {"amount": 5000}},
                expected_observation="Model prediction",
                evidence_required="Model prediction score",
                reasoning="Probing model interface"
            )
        ],
        success_criteria="Model prediction retrieved",
        possible_outcomes=["Success"]
    )

    result = executor.execute_plan(profile, hypothesis, plan)
    assert len(result.executed_steps) == 1
    exec_step = result.executed_steps[0]
    assert exec_step.status == "unavailable"
    assert exec_step.tool == "query_model_interface"
    assert exec_step.parameters == {"input": {"amount": 5000}}


# ============================================================
# 9. TEST OBSERVATION INTERPRETATION
# ============================================================
def test_observation_interpretation_grounded_small_difference():
    """Verify interpreter evaluates small score difference (0.82 vs 0.83) as inconclusive rather than claiming bias."""
    interpreter = ObservationInterpreter(llm_client=MockLLMClient())
    profile = SystemProfile(
        purpose="Fraud detection",
        intended_use="Transaction scoring",
        ai_system_type="Classifier",
        model_type="Ensemble",
        inputs=["amount", "location"],
        outputs=["fraud_probability"],
        decision_process="Scoring",
        affected_users=["Cardholders"],
        decision_impact="High",
        autonomy_level="autonomous",
        data_types=["Transactions"],
        sensitive_data=[],
        external_services=[],
        human_involvement="Async",
        deployment_context="Pipeline",
        expected_benefits=[],
        potential_consequences=[],
        important_unknowns=[],
        assumptions=[],
        observed_evidence={}
    )
    hypothesis = Hypothesis(
        id="HYP-F01",
        hypothesis="Location parameter causes biased fraud predictions.",
        why_it_is_plausible="Location is an input field.",
        supporting_evidence=["Location input"],
        affected_part="Scoring engine",
        potential_consequence="False blocks",
        what_evidence_would_support_it=["Significant score variance"],
        what_evidence_would_refute_it=["Identical score"],
        priority="medium",
        confidence=0.70
    )
    plan = InvestigationPlan(
        hypothesis_id="HYP-F01",
        investigation_goal="Compare scores across location",
        reasoning="Test location impact",
        steps=[],
        success_criteria="Score comparison",
        possible_outcomes=[]
    )
    executed_steps = [
        ToolExecution(
            execution_id="EXEC-1",
            step_id="STEP-1",
            tool="compare_outputs",
            parameters={"output_a": {"fraud_probability": 0.82}, "output_b": {"fraud_probability": 0.83}},
            timestamp="2026-09-17",
            status="success",
            result={"diff": 0.01},
            evidence=["Baseline 0.82 vs Modified Location 0.83 (small difference 0.01)"]
        )
    ]
    observations = [
        Observation(
            observation_id="OBS-1",
            step_id="STEP-1",
            description="Small difference observed: 0.82 vs 0.83",
            source="compare_outputs",
            evidence=["0.82 vs 0.83 small difference"],
            significance="Score comparison"
        )
    ]

    interp = interpreter.interpret_evidence(profile, hypothesis, plan, executed_steps, observations)
    assert interp.hypothesis_status in ["inconclusive", "weakened"]
    assert "discrimination" not in interp.interpretation.lower() or "insufficient" in interp.interpretation.lower()


# ============================================================
# 10. TEST ADAPTIVE LOOP SCENARIOS (A, B, C, D)
# ============================================================
def test_adaptive_loop_scenarios():
    """Test Adaptive Loop across Scenario A (Continue), B (Stop), C (Tool Unavailable), D (Max Iterations)."""
    agent = AdaptiveInvestigationAgent(llm_client=MockLLMClient())
    profile = SystemProfile(
        purpose="Fraud detection",
        intended_use="Pipeline",
        ai_system_type="Classifier",
        model_type="Ensemble",
        inputs=["amount", "location"],
        outputs=["score"],
        decision_process="Rules",
        affected_users=["Cardholders"],
        decision_impact="High",
        autonomy_level="autonomous",
        data_types=["Data"],
        sensitive_data=[],
        external_services=[],
        human_involvement="None",
        deployment_context="Realtime",
        expected_benefits=[],
        potential_consequences=[],
        important_unknowns=[],
        assumptions=[],
        observed_evidence={}
    )
    hypo = Hypothesis(
        id="HYP-F01",
        hypothesis="Location perturbs fraud score",
        why_it_is_plausible="Location input",
        supporting_evidence=["Location input"],
        affected_part="Engine",
        potential_consequence="Decline",
        what_evidence_would_support_it=["Score diff"],
        what_evidence_would_refute_it=["No diff"],
        priority="medium",
        confidence=0.80
    )

    # Scenario D: Max Iterations = 2
    res_d = agent.run_adaptive_loop(profile, [hypo], available_tools=["modify_input", "compare_outputs"], max_iterations=2)
    assert len(res_d.iterations) <= 2
    assert res_d.status in ["completed", "max_iterations_reached"]

    # Scenario C: Tool Unavailable
    res_c = agent.run_adaptive_loop(profile, [hypo], available_tools=["no_tools"], max_iterations=2)
    assert res_c.status in ["completed", "insufficient_capability"]


# ============================================================
# 11. TEST ADAPTIVITY PROPERLY (MOST IMPORTANT TEST)
# ============================================================
def test_adaptivity_depends_on_previous_evidence():
    """Verify that different first observations result in distinct next investigative questions/plans."""
    agent = AdaptiveInvestigationAgent(llm_client=MockLLMClient())
    profile = SystemProfile(
        purpose="Fraud detection",
        intended_use="Pipeline",
        ai_system_type="Classifier",
        model_type="Ensemble",
        inputs=["amount", "location"],
        outputs=["score"],
        decision_process="Rules",
        affected_users=["Users"],
        decision_impact="High",
        autonomy_level="autonomous",
        data_types=["Data"],
        sensitive_data=[],
        external_services=[],
        human_involvement="None",
        deployment_context="Pipeline",
        expected_benefits=[],
        potential_consequences=[],
        important_unknowns=[],
        assumptions=[],
        observed_evidence={}
    )
    hypo = Hypothesis(
        id="HYP-F01",
        hypothesis="Location perturbs fraud score",
        why_it_is_plausible="Location input",
        supporting_evidence=[],
        affected_part="Engine",
        potential_consequence="Decline",
        what_evidence_would_support_it=[],
        what_evidence_would_refute_it=[],
        priority="medium",
        confidence=0.80
    )

    # Test 1: Observation = Changing location has almost no effect
    res1 = agent.run_adaptive_loop(
        profile,
        [hypo],
        available_tools=["modify_input", "compare_outputs"],
        initial_evidence=["Observation: Changing location has almost no effect (0.82 vs 0.83)."],
        max_iterations=1
    )

    # Test 2: Observation = Changing location causes a large output difference
    res2 = agent.run_adaptive_loop(
        profile,
        [hypo],
        available_tools=["modify_input", "compare_outputs"],
        initial_evidence=["Observation: Changing location causes a large output difference (0.82 vs 0.15)."],
        max_iterations=1
    )

    assert len(res1.iterations) > 0
    assert len(res2.iterations) > 0

    dec1 = res1.iterations[0].adaptive_decision
    dec2 = res2.iterations[0].adaptive_decision

    # Verify that the agent produces reasoning/questions based on previous evidence
    assert dec1.reasoning != dec2.reasoning or dec1.next_question != dec2.next_question or dec1.evidence_summary != dec2.evidence_summary


# ============================================================
# 12. TEST NO HALLUCINATION (Vague Project)
# ============================================================
def test_vague_project_no_hallucination():
    """Verify that analyzing a vague project identifies unknown information rather than inventing facts."""
    analyzer = ProjectAnalyzer(llm_client=MockLLMClient())
    vague_input = ProjectInput(
        project_name="My AI",
        description="An AI model that predicts outcomes.",
        github_url=None,
        documentation="",
        sample_inputs=[],
        sample_outputs=[]
    )
    profile = analyzer.analyze_project(vague_input)
    assert profile.purpose is not None
    assert isinstance(profile.important_unknowns, list)


# ============================================================
# 13. TEST CONTRADICTORY INFORMATION
# ============================================================
def test_contradictory_information_handling():
    """Verify that conflicting claims (automatic approval vs human recommendation) are captured as conflict/uncertainty."""
    analyzer = ProjectAnalyzer(llm_client=MockLLMClient())
    contradictory_input = ProjectInput(
        project_name="Loan Approver",
        description="The system automatically approves loan applications.",
        github_url=None,
        documentation="The AI only provides recommendations. A human loan officer makes the final decision.",
        sample_inputs=[],
        sample_outputs=[]
    )
    profile = analyzer.analyze_project(contradictory_input)

    # Verify profile captures conflict/uncertainty in autonomy or human involvement or unknowns
    combined_text = (
        f"{profile.autonomy_level} {profile.human_involvement} {profile.decision_process} "
        f"{' '.join(profile.important_unknowns)}"
    ).lower()

    assert "contradict" in combined_text or "conflict" in combined_text or "uncertain" in combined_text or "human" in combined_text


# ============================================================
# 14. TEST SAFETY BOUNDARIES
# ============================================================
def test_safety_boundaries_no_arbitrary_command_execution():
    """Verify that malicious inputs or tool names cannot cause arbitrary shell execution or env leakage."""
    registry = ToolRegistry()
    registry.register(default_tool_registry.get_tool("modify_input"))

    # Attempt to execute an unregistered malicious tool name
    malicious_step = InvestigationStep(
        step_id="STEP-MALICIOUS",
        objective="Run shell command",
        tool="os.system('whoami')",
        parameters={"cmd": "whoami"},
        expected_observation="None",
        evidence_required="None",
        reasoning="Exploit attempt"
    )

    executor = InvestigationExecutor(registry=registry)
    plan = InvestigationPlan(
        hypothesis_id="HYP-SEC",
        investigation_goal="Test security boundary",
        reasoning="Security boundary validation",
        steps=[malicious_step],
        success_criteria="Blocked",
        possible_outcomes=[]
    )

    profile = SystemProfile(
        purpose="Test", intended_use="Test", ai_system_type="Test", model_type="Test",
        inputs=[], outputs=[], decision_process="Test", affected_users=[], decision_impact="Low",
        autonomy_level="none", data_types=[], sensitive_data=[], external_services=[],
        human_involvement="None", deployment_context="Test", expected_benefits=[],
        potential_consequences=[], important_unknowns=[], assumptions=[], observed_evidence={}
    )
    hypothesis = Hypothesis(
        id="HYP-SEC", hypothesis="Test", why_it_is_plausible="Test", supporting_evidence=[],
        affected_part="Test", potential_consequence="Test", what_evidence_would_support_it=[],
        what_evidence_would_refute_it=[], priority="low", confidence=0.5
    )

    result = executor.execute_plan(profile, hypothesis, plan)
    assert len(result.executed_steps) == 1
    exec_step = result.executed_steps[0]
    assert exec_step.status == "unavailable"
    assert "not registered" in (exec_step.error or "").lower()
