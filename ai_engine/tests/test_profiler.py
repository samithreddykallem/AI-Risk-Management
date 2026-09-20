from ai_engine.models.system_input import ProjectInput
from ai_engine.services.project_service import analyze_project_service
from ai_engine.llm.mock_provider import MockLLMProvider


def test_analyze_project_service():
    mock_llm = MockLLMProvider()
    project_input = ProjectInput(
        project_name="MedBot-Diagnostic",
        description="Assists doctors by summarizing patient symptoms and suggesting differential diagnoses.",
        github_url="https://github.com/example/medbot",
        documentation="Uses LLM fine-tuned on medical abstracts. Requires clinician sign-off.",
        sample_inputs=["Patient presenting with acute chest pain and dyspnea."],
        sample_outputs=["Suggested differential diagnosis: 1. Acute Coronary Syndrome, 2. Pulmonary Embolism."]
    )

    profile = analyze_project_service(project_input, llm_provider=mock_llm)

    assert profile.purpose is not None
    assert profile.intended_use is not None
    assert profile.ai_system_type is not None
    assert profile.autonomy_level is not None
    assert isinstance(profile.inputs, list)
    assert isinstance(profile.outputs, list)
    assert isinstance(profile.sensitive_data, list)
    assert isinstance(profile.observed_evidence, dict)
