from fastapi.testclient import TestClient
from app.main import app
from app.schemas.project import ProjectInput
from app.services.project_analyzer import ProjectAnalyzer

client = TestClient(app)


def test_project_analyzer_service():
    analyzer = ProjectAnalyzer()
    project_input = ProjectInput(
        project_name="CreditRisk-Predictor",
        description="Automates credit risk evaluation and loan approval recommendations for banking applicants.",
        github_url=None,
        documentation="Gradient Boosting classifier combined with LLM prompt wrapper.",
        sample_inputs=["Applicant Income: $65,000", "Zip Code: 90210"],
        sample_outputs=["Risk Score: 810", "Recommendation: Approved"]
    )
    profile = analyzer.analyze_project(project_input)
    assert profile.purpose is not None
    assert profile.intended_use is not None
    assert profile.ai_system_type is not None


def test_post_engine_analyze_project_endpoint():
    payload = {
        "project_name": "CreditRisk-Predictor",
        "description": "Automates credit risk evaluation and loan approval recommendations for banking applicants.",
        "github_url": None,
        "documentation": "Gradient Boosting classifier combined with LLM prompt wrapper.",
        "sample_inputs": ["Applicant Income: $65,000", "Zip Code: 90210"],
        "sample_outputs": ["Risk Score: 810", "Recommendation: Approved"]
    }
    response = client.post("/engine/analyze-project", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "purpose" in data
    assert "intended_use" in data
    assert "ai_system_type" in data
    assert "model_type" in data
    assert "inputs" in data
    assert "outputs" in data
    assert "decision_process" in data
    assert "affected_users" in data
    assert "decision_impact" in data
    assert "autonomy_level" in data
    assert "data_types" in data
    assert "sensitive_data" in data
    assert "external_services" in data
    assert "human_involvement" in data
    assert "deployment_context" in data
    assert "expected_benefits" in data
    assert "potential_consequences" in data
    assert "important_unknowns" in data
    assert "assumptions" in data
    assert "observed_evidence" in data
