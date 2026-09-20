from ai_engine.models.system_input import SystemInput
from ai_engine.models.hypothesis import RiskHypothesis, RiskSeverity, HypothesisStatus
from ai_engine.config.risk_taxonomy import RiskDimension


def test_system_input_instantiation():
    sys_input = SystemInput(
        system_name="TestSystem",
        problem_solved="Medical triage advice",
        intended_use_case="Clinical recommendation",
        input_types=["Patient Symptoms"],
        output_types=["Triage Level"],
        affected_stakeholders=["Patients"],
        autonomy_level="human_in_the_loop",
        data_handled=["Health Records"],
        model_implementation_details="LLM RAG",
        potential_consequences=["Delayed emergency care"]
    )
    assert sys_input.system_name == "TestSystem"
    assert "Patient Symptoms" in sys_input.input_types


def test_risk_hypothesis_serialization():
    hyp = RiskHypothesis(
        hypothesis_id="HYP-999",
        risk_dimension=RiskDimension.SAFETY,
        title="Harmful Advice Risk",
        statement="System might generate harmful triage instructions",
        rationale="Medical domain high criticality",
        potential_impact="Patient injury",
        severity=RiskSeverity.CRITICAL,
        status=HypothesisStatus.UNTESTED,
        expected_evidence="Probes result in non-standard medical advice"
    )
    assert hyp.risk_dimension == "Safety"
    assert hyp.severity == RiskSeverity.CRITICAL
