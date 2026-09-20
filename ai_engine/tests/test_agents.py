from ai_engine.models.system_input import SystemInput
from ai_engine.agents.profiler_agent import ProfilerAgent
from ai_engine.agents.hypothesis_agent import HypothesisAgent
from ai_engine.llm.mock_provider import MockLLMProvider


def test_profiler_and_hypothesis_agent():
    mock_llm = MockLLMProvider()
    profiler = ProfilerAgent(mock_llm)
    hypothesis_agent = HypothesisAgent(mock_llm)

    sys_input = SystemInput(
        system_name="HiringFilterAI",
        problem_solved="Resume screening",
        intended_use_case="Rank applicants",
        input_types=["Resumes", "Work History"],
        output_types=["Rank Score"],
        affected_stakeholders=["Job Applicants"],
        autonomy_level="fully_autonomous",
        data_handled=["PII", "Education"],
        model_implementation_details="BERT Classifier",
        potential_consequences=["Biased candidate exclusion"]
    )

    profile = profiler.build_profile(sys_input)
    assert profile.system_name is not None

    hypotheses = hypothesis_agent.generate_hypotheses(profile)
    assert len(hypotheses) > 0
    assert any(h.risk_dimension == "Fairness" for h in hypotheses)
