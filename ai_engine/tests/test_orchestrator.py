from ai_engine.models.system_input import SystemInput
from ai_engine.workflows.audit_orchestrator import AuditOrchestrator
from ai_engine.llm.mock_provider import MockLLMProvider


def test_full_audit_orchestration_loop():
    mock_llm = MockLLMProvider()
    orchestrator = AuditOrchestrator(llm_provider=mock_llm)

    sys_input = SystemInput(
        system_name="AuditTest-Bot",
        problem_solved="Customer support automated responses",
        intended_use_case="E-commerce chat",
        input_types=["User Prompt"],
        output_types=["Bot Response"],
        affected_stakeholders=["Customers"],
        autonomy_level="human_in_the_loop",
        data_handled=["Customer Chat History"],
        model_implementation_details="LLM RAG system",
        potential_consequences=["Data leak", "Adversarial prompt injection"]
    )

    report = orchestrator.run_audit(sys_input)

    assert report.audit_id is not None
    assert report.system_name == "AuditTest-Bot"
    assert report.total_hypotheses_evaluated > 0
    assert len(orchestrator.state_tracker.history) > 0
