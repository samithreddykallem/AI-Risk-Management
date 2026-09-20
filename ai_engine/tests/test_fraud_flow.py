from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_smart_fraud_detector_full_execution_flow():
    """End-to-end demo flow for Smart Fraud Detector across Phase 1 -> Phase 2 -> Phase 3 -> Phase 5."""
    # 1. Analyze Project
    fraud_project = {
        "project_name": "Smart Fraud Detector",
        "description": "Analyzes payment transaction velocity, IP geolocation, and transaction amount to flag credit card fraud.",
        "github_url": None,
        "documentation": "Uses isolation forest and XGBoost ensemble. High velocity transactions trigger auto-decline.",
        "sample_inputs": ["Transaction Amount: $4,500", "IP Country: RU", "Velocity: 12 txns/min"],
        "sample_outputs": ["Fraud Risk Score: 0.94", "Action: Auto-Decline"]
    }
    resp1 = client.post("/engine/analyze-project", json=fraud_project)
    assert resp1.status_code == 200
    profile = resp1.json()

    # 2. Generate Hypotheses
    resp2 = client.post("/engine/generate-hypotheses", json={"system_profile": profile})
    assert resp2.status_code == 200
    hypotheses = resp2.json()["hypotheses"]
    assert len(hypotheses) > 0
    selected_hypothesis = hypotheses[0]

    # 3. Plan Investigation
    resp3 = client.post("/engine/plan-investigation", json={
        "system_profile": profile,
        "hypothesis": selected_hypothesis,
        "available_tools": ["modify_input", "compare_outputs", "model_tool"],
        "existing_evidence": []
    })
    assert resp3.status_code == 200
    plan_res = resp3.json()
    assert plan_res["status"] == "ready"
    plan = plan_res["investigation_plan"]

    # 4. Execute Investigation & Interpret Observations
    resp4 = client.post("/engine/execute-investigation", json={
        "system_profile": profile,
        "hypothesis": selected_hypothesis,
        "investigation_plan": plan,
        "available_tools": ["modify_input", "compare_outputs", "model_tool"],
        "initial_evidence": ["Initial evidence record"]
    })
    assert resp4.status_code == 200
    exec_res = resp4.json()

    inv_result = exec_res["investigation_result"]
    interpretation = exec_res["interpretation"]

    assert inv_result["hypothesis_id"] == selected_hypothesis["id"]
    assert len(inv_result["executed_steps"]) == len(plan["steps"])
    assert len(inv_result["observations"]) > 0
    assert interpretation["hypothesis_status"] in ["supported", "weakened", "inconclusive"]
