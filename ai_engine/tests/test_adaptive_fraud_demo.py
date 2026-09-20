from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_smart_fraud_detector_adaptive_agent_demo():
    """End-to-end adaptive investigation agent test for Smart Fraud Detector."""
    fraud_project = {
        "project_name": "Smart Fraud Detector",
        "description": "Analyzes payment transaction velocity, IP geolocation, and transaction amount to flag credit card fraud.",
        "documentation": "Uses isolation forest and XGBoost ensemble. High velocity transactions trigger auto-decline."
    }

    # 1. Analyze Project
    resp1 = client.post("/engine/analyze-project", json=fraud_project)
    assert resp1.status_code == 200
    profile = resp1.json()

    # 2. Generate Hypotheses
    resp2 = client.post("/engine/generate-hypotheses", json={"system_profile": profile})
    assert resp2.status_code == 200
    hypotheses = resp2.json()["hypotheses"]
    assert len(hypotheses) > 0

    # 3. Run Adaptive Investigation Loop
    adaptive_payload = {
        "system_profile": profile,
        "hypotheses": hypotheses,
        "available_tools": ["modify_input", "compare_outputs", "run_model", "analyze_evidence"],
        "initial_evidence": ["Initial context metadata"],
        "max_iterations": 3
    }

    resp3 = client.post("/engine/run-adaptive-investigation", json=adaptive_payload)
    assert resp3.status_code == 200
    result = resp3.json()

    assert result["status"] in ["completed", "max_iterations_reached", "insufficient_capability"]
    assert len(result["iterations"]) > 0
    assert "final_evidence" in result
    assert isinstance(result["final_evidence"], list)
