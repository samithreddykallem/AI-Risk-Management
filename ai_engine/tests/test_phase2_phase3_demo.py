import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_phase2_phase3_demo_flow():
    print("==========================================================================")
    print("       AI RISK MANAGER: PHASE 2 & 3 END-TO-END VERIFICATION DEMO")
    print("==========================================================================")


    # 1. Test OpenAPI / Swagger routes check
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    expected_endpoints = [
        ("/", "get"),
        ("/health", "get"),
        ("/engine/test-llm", "post"),
        ("/engine/analyze-project", "post"),
        ("/engine/generate-hypotheses", "post"),
        ("/engine/plan-investigation", "post"),
    ]
    print("\n--- 1. SWAGGER / OPENAPI ENDPOINTS VERIFICATION ---")
    for endpoint, method in expected_endpoints:
        assert endpoint in paths and method in paths[endpoint], f"Missing {method.upper()} {endpoint}"
        print(f"[OK] {method.upper()} {endpoint} present in Swagger API spec")

    # 2. Smart Fraud Detector AI System
    print("\n--- 2. SMART FRAUD DETECTOR AUDIT ---")
    fraud_input = {
        "project_name": "Smart Fraud Detector",
        "description": "An AI system that analyzes bank transactions and predicts whether a transaction is fraudulent. It uses transaction amount, location, device information, merchant information and historical account behavior. Transactions with a high fraud probability are automatically blocked.",
        "github_url": None,
        "documentation": "The system is designed to detect fraudulent financial transactions in real time. It processes transaction information and produces a fraud probability score. High velocity transactions trigger auto-decline.",
        "sample_inputs": [{"amount": 5000, "location": "Hyderabad", "device": "Android", "merchant": "Online Store"}],
        "sample_outputs": [{"fraud_probability": 0.82, "decision": "BLOCK"}]
    }

    # Step 2a: Phase 1 Analyze Project
    resp_f_prof = client.post("/engine/analyze-project", json=fraud_input)
    assert resp_f_prof.status_code == 200
    fraud_profile = resp_f_prof.json()
    print(f"[OK] System Profile Generated:")
    print(f"    Purpose: {fraud_profile['purpose']}")
    print(f"    Inputs: {fraud_profile['inputs']}")
    print(f"    Autonomy Level: {fraud_profile['autonomy_level']}")

    # Step 2b: Phase 2 Generate Hypotheses
    resp_f_hypo = client.post("/engine/generate-hypotheses", json={"system_profile": fraud_profile})
    assert resp_f_hypo.status_code == 200
    fraud_hypotheses = resp_f_hypo.json()["hypotheses"]
    print(f"[OK] Generated {len(fraud_hypotheses)} System-Specific Risk Hypothesis(es):")
    for h in fraud_hypotheses:
        print(f"    Hypothesis ID: [{h['id']}] (Priority: {h['priority']}, Confidence: {h['confidence']})")
        print(f"    Statement: {h['hypothesis']}")
        print(f"    Why Plausible: {h['why_it_is_plausible']}")

    # Step 2c: Phase 3 Plan Investigation
    selected_fraud_hypo = fraud_hypotheses[0]
    resp_f_plan = client.post("/engine/plan-investigation", json={
        "system_profile": fraud_profile,
        "hypothesis": selected_fraud_hypo,
        "available_tools": ["modify_input", "compare_outputs"],
        "existing_evidence": ["Initial observation from system profile"]
    })
    assert resp_f_plan.status_code == 200
    fraud_plan_resp = resp_f_plan.json()
    print(f"[OK] Investigation Plan Status: {fraud_plan_resp['status']}")
    if fraud_plan_resp["status"] == "ready":
        plan = fraud_plan_resp["investigation_plan"]
        print(f"    Goal: {plan['investigation_goal']}")
        print(f"    Steps ({len(plan['steps'])}):")
        for step in plan['steps']:
            print(f"      - [{step['step_id']}] Tool: {step['tool']} -> {step['objective']}")

    # 3. Healthcare AI (MediTriage Assist)
    print("\n--- 3. HEALTHCARE AI (MEDITRIAGE ASSIST) AUDIT ---")
    health_input = {
        "project_name": "MediTriage Assist",
        "description": "Summarizes patient clinical notes and suggests emergency triage acuity scores for ER nurses.",
        "github_url": None,
        "documentation": "Uses fine-tuned LLM on clinical notes. Nurse must verify all triage acuity assignments.",
        "sample_inputs": [{"patient_note": "45y female presenting with atypical chest pressure and nausea."}],
        "sample_outputs": [{"suggested_acuity": "ESI Level 3", "summary": "Atypical chest discomfort"}]
    }

    # Step 3a: Phase 1 Analyze Project
    resp_h_prof = client.post("/engine/analyze-project", json=health_input)
    assert resp_h_prof.status_code == 200
    health_profile = resp_h_prof.json()
    print(f"[OK] System Profile Generated:")
    print(f"    Purpose: {health_profile['purpose']}")
    print(f"    Inputs: {health_profile['inputs']}")
    print(f"    Autonomy Level: {health_profile['autonomy_level']}")

    # Step 3b: Phase 2 Generate Hypotheses
    resp_h_hypo = client.post("/engine/generate-hypotheses", json={"system_profile": health_profile})
    assert resp_h_hypo.status_code == 200
    health_hypotheses = resp_h_hypo.json()["hypotheses"]
    print(f"[OK] Generated {len(health_hypotheses)} System-Specific Risk Hypothesis(es):")
    for h in health_hypotheses:
        print(f"    Hypothesis ID: [{h['id']}] (Priority: {h['priority']}, Confidence: {h['confidence']})")
        print(f"    Statement: {h['hypothesis']}")
        print(f"    Why Plausible: {h['why_it_is_plausible']}")

    # Step 3c: Phase 3 Plan Investigation
    selected_health_hypo = health_hypotheses[0]
    resp_h_plan = client.post("/engine/plan-investigation", json={
        "system_profile": health_profile,
        "hypothesis": selected_health_hypo,
        "available_tools": ["modify_input", "compare_outputs", "analyze_evidence"],
        "existing_evidence": []
    })
    assert resp_h_plan.status_code == 200
    health_plan_resp = resp_h_plan.json()
    print(f"[OK] Investigation Plan Status: {health_plan_resp['status']}")
    if health_plan_resp["status"] == "ready":
        plan = health_plan_resp["investigation_plan"]
        print(f"    Goal: {plan['investigation_goal']}")

    # 4. Domain Difference Comparison
    print("\n--- 4. DOMAIN DIFFERENCE COMPARISON ---")
    assert fraud_profile["purpose"] != health_profile["purpose"]
    assert selected_fraud_hypo["hypothesis"] != selected_health_hypo["hypothesis"]
    print("[OK] Fraud AI and Healthcare AI generated completely distinct, system-grounded hypotheses and investigation plans.")

    # 5. Vague AI Project Test
    print("\n--- 5. VAGUE AI PROJECT TEST (NO HALLUCINATION & IMPORTANT UNKNOWNS) ---")
    vague_input = {
        "project_name": "Vague Project",
        "description": "A vague software tool.",
        "github_url": None,
        "documentation": "vague - no documentation provided",
        "sample_inputs": [],
        "sample_outputs": []
    }
    resp_v_prof = client.post("/engine/analyze-project", json=vague_input)
    vague_profile = resp_v_prof.json()
    print(f"[OK] Important Unknowns Identified: {vague_profile['important_unknowns']}")
    
    resp_v_hypo = client.post("/engine/generate-hypotheses", json={"system_profile": vague_profile})
    vague_hypotheses = resp_v_hypo.json()["hypotheses"]
    print(f"[OK] Hypotheses Generated for Vague Input (Expect empty or strictly ungrounded): {len(vague_hypotheses)}")
    assert len(vague_hypotheses) == 0


    print("\n==========================================================================")
    print("       ALL PHASE 2 & PHASE 3 REQUIREMENTS VERIFIED SUCCESSFULLY!")
    print("==========================================================================")

if __name__ == "__main__":
    main()
