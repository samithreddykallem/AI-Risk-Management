from fastapi.testclient import TestClient
from ai_engine.server import app

client = TestClient(app)


def test_post_engine_test_llm_endpoint():
    payload = {"message": "Say hello"}
    response = client.post("/engine/test-llm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_post_engine_test_llm_missing_message():
    response = client.post("/engine/test-llm", json={})
    assert response.status_code == 422


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

    profile = response.json()
    assert "purpose" in profile
    assert "intended_use" in profile
    assert "ai_system_type" in profile
    assert "model_type" in profile
    assert "inputs" in profile
    assert "outputs" in profile
    assert "decision_process" in profile
    assert "affected_users" in profile
    assert "decision_impact" in profile
    assert "autonomy_level" in profile
    assert "data_types" in profile
    assert "sensitive_data" in profile
    assert "external_services" in profile
    assert "human_involvement" in profile
    assert "deployment_context" in profile
    assert "expected_benefits" in profile
    assert "potential_consequences" in profile
    assert "important_unknowns" in profile
    assert "assumptions" in profile
    assert "observed_evidence" in profile
