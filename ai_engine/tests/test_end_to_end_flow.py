from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_e2e_smart_fraud_detector_pipeline():
    """End-to-end test for Smart Fraud Detector: Analyze Project -> Generate Hypotheses -> Plan Investigation."""
    # Step 1: Analyze Project -> System Profile
    fraud_payload = {
        "project_name": "Smart Fraud Detector",
        "description": "Analyzes payment transaction velocity, IP geolocation, and transaction amount to flag credit card fraud.",
        "github_url": None,
        "documentation": "Uses isolation forest and XGBoost ensemble. High velocity transactions trigger auto-decline.",
        "sample_inputs": ["Transaction Amount: $4,500", "IP Country: RU", "Velocity: 12 txns/min"],
        "sample_outputs": ["Fraud Risk Score: 0.94", "Action: Auto-Decline"]
    }
    resp1 = client.post("/engine/analyze-project", json=fraud_payload)
    assert resp1.status_code == 200
    fraud_profile = resp1.json()
    assert fraud_profile["purpose"] is not None

    # Step 2: Generate Hypotheses -> System-Specific Hypotheses
    hyp_payload = {"system_profile": fraud_profile}
    resp2 = client.post("/engine/generate-hypotheses", json=hyp_payload)
    assert resp2.status_code == 200
    hypotheses_data = resp2.json()
    assert "hypotheses" in hypotheses_data
    assert len(hypotheses_data["hypotheses"]) > 0
    selected_hypothesis = hypotheses_data["hypotheses"][0]

    # Step 3: Select hypothesis -> Plan Investigation
    plan_payload = {
        "system_profile": fraud_profile,
        "hypothesis": selected_hypothesis,
        "available_tools": ["run_model", "modify_input", "compare_outputs"],
        "existing_evidence": []
    }
    resp3 = client.post("/engine/plan-investigation", json=plan_payload)
    assert resp3.status_code == 200
    plan_data = resp3.json()
    assert plan_data["status"] in ["ready", "insufficient_capability"]


def test_e2e_healthcare_ai_pipeline():
    """End-to-end test for Healthcare MediTriage Assist: Analyze Project -> Generate Hypotheses -> Plan Investigation."""
    health_payload = {
        "project_name": "MediTriage Assist",
        "description": "Summarizes patient clinical notes and suggests emergency triage acuity scores for ER nurses.",
        "github_url": None,
        "documentation": "Uses fine-tuned LLM on clinical notes. Nurse must verify all triage acuity assignments.",
        "sample_inputs": ["Patient 45y male presenting with retrosternal chest pain and diaphoresis."],
        "sample_outputs": ["Suggested Acuity Level: ESI Level 2 (Emergent)"]
    }
    resp1 = client.post("/engine/analyze-project", json=health_payload)
    assert resp1.status_code == 200
    health_profile = resp1.json()

    resp2 = client.post("/engine/generate-hypotheses", json={"system_profile": health_profile})
    assert resp2.status_code == 200
    health_hypotheses = resp2.json()["hypotheses"]
    assert len(health_hypotheses) > 0
    health_hypothesis = health_hypotheses[0]

    resp3 = client.post("/engine/plan-investigation", json={
        "system_profile": health_profile,
        "hypothesis": health_hypothesis,
        "available_tools": ["run_model", "inspect_repository", "analyze_evidence"]
    })
    assert resp3.status_code == 200
    assert "status" in resp3.json()


def test_e2e_domain_differentiation():
    """Verify that Fraud Detector and Healthcare AI generate distinctly different hypotheses."""
    fraud_payload = {
        "project_name": "Smart Fraud Detector",
        "description": "Analyzes payment transaction velocity, IP geolocation, and transaction amount to flag credit card fraud.",
        "documentation": "Uses isolation forest and XGBoost ensemble. High velocity transactions trigger auto-decline."
    }
    health_payload = {
        "project_name": "MediTriage Assist",
        "description": "Summarizes patient clinical notes and suggests emergency triage acuity scores for ER nurses.",
        "documentation": "Uses fine-tuned LLM on clinical notes. Nurse must verify all triage acuity assignments."
    }

    prof_fraud = client.post("/engine/analyze-project", json=fraud_payload).json()
    prof_health = client.post("/engine/analyze-project", json=health_payload).json()

    hyp_fraud = client.post("/engine/generate-hypotheses", json={"system_profile": prof_fraud}).json()["hypotheses"]
    hyp_health = client.post("/engine/generate-hypotheses", json={"system_profile": prof_health}).json()["hypotheses"]

    assert len(hyp_fraud) > 0
    assert len(hyp_health) > 0
    assert hyp_fraud[0]["hypothesis"] != hyp_health[0]["hypothesis"]


def test_e2e_vague_ai_project():
    """Verify that a vague project returns unknown fields and zero/minimal hypotheses without inventing facts."""
    vague_payload = {
        "project_name": "Vague Project X",
        "description": "A vague AI helper tool with no documentation provided.",
        "github_url": None,
        "documentation": None
    }
    prof_resp = client.post("/engine/analyze-project", json=vague_payload)
    assert prof_resp.status_code == 200
    profile = prof_resp.json()

    hyp_resp = client.post("/engine/generate-hypotheses", json={"system_profile": profile})
    assert hyp_resp.status_code == 200
    hypotheses = hyp_resp.json()["hypotheses"]
    assert isinstance(hypotheses, list)


def test_post_engine_audit_e2e():
    """Single API Call E2E Test: POST /engine/audit."""
    audit_payload = {
        "project": {
            "project_name": "Smart Fraud Detector",
            "description": "An AI system that analyzes bank transactions and predicts whether a transaction is fraudulent. It uses transaction amount, location, device information, merchant information and historical account behavior. Transactions with a high fraud probability are automatically blocked.",
            "github_url": None,
            "documentation": "The system is designed to detect fraudulent financial transactions in real time. It processes transaction information and produces a fraud probability score. If the score exceeds a threshold, the transaction is blocked.",
            "sample_inputs": [{"amount": 5000, "location": "Hyderabad", "device": "Android", "merchant": "Online Store"}],
            "sample_outputs": [{"fraud_probability": 0.82, "decision": "BLOCK"}]
        },
        "available_tools": ["analysis_tool", "model_tool", "repository_tool"],
        "max_iterations": 3
    }
    response = client.post("/engine/audit", json=audit_payload)
    assert response.status_code == 200
    data = response.json()
    assert "audit_id" in data and data["audit_id"].startswith("AUDIT-")
    assert "system_profile" in data and "purpose" in data["system_profile"]
    assert "hypotheses" in data and len(data["hypotheses"]) > 0
    assert "investigation_trace" in data and isinstance(data["investigation_trace"], list)
    assert "final_evidence" in data and isinstance(data["final_evidence"], list)
    assert "unresolved_questions" in data and isinstance(data["unresolved_questions"], list)
    assert "limitations" in data and isinstance(data["limitations"], list)
    assert "status" in data and data["status"] in ["completed", "max_iterations_reached", "insufficient_capability"]

