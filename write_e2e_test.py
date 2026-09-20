import os
import sys
from fastapi.testclient import TestClient

# Ensure ai_engine directory is on sys.path
ai_engine_dir = r"c:\Users\yerra\OneDrive\Desktop\ai-risk-manager\ai_engine"
if ai_engine_dir not in sys.path:
    sys.path.insert(0, ai_engine_dir)

from app.main import app as ai_engine_app


def main():
    print("==========================================================================")
    print("   DATASET-DRIVEN ADAPTIVE AI AUDITOR - MASTER E2E INTEGRATION SUITE")
    print("==========================================================================")

    client = TestClient(ai_engine_app)

    # 1. Test Health & Root
    print("\n--- 1. VERIFYING SERVICE HEALTH & IDENTIFICATION ---")
    r_root = client.get("/")
    assert r_root.status_code == 200
    print("[OK] GET / ->", r_root.json())

    r_health = client.get("/health")
    assert r_health.status_code == 200
    print("[OK] GET /health ->", r_health.json())

    # 2. Test Dataset Upload & Profiling
    print("\n--- 2. VERIFYING DATASET UPLOAD & PROFILING ---")
    dataset_path = os.path.join(ai_engine_dir, "tests", "loan_data.csv")
    assert os.path.exists(dataset_path), f"Test dataset missing at: {dataset_path}"

    with open(dataset_path, "rb") as f:
        r_upload = client.post("/engine/upload-dataset", files={"file": ("loan_data.csv", f, "text/csv")})
    assert r_upload.status_code == 200
    upload_res = r_upload.json()
    print("[OK] POST /engine/upload-dataset ->", upload_res)
    uploaded_path = upload_res["dataset_path"]

    # 3. Test Full Dataset-Driven Audit Execution
    print("\n--- 3. VERIFYING ADAPTIVE DATASET-DRIVEN AUDIT EXECUTION ---")
    audit_payload = {
        "project": {
            "project_name": "Smart Credit Decision System",
            "description": "An automated credit risk decisioning engine evaluating consumer loan applications.",
            "github_url": "https://github.com/example/credit-decision-system",
            "documentation": "Evaluates applicant income, credit score, zip code, and employment status to issue loan recommendations.",
            "dataset_path": uploaded_path,
            "dataset_name": "loan_data.csv",
            "target_column": "Loan_Status",
            "sensitive_attributes": ["Gender"]
        },
        "max_iterations": 3
    }

    r_audit = client.post("/engine/audit", json=audit_payload)
    assert r_audit.status_code == 200
    audit_res = r_audit.json()

    print("[OK] POST /engine/audit -> Audit ID:", audit_res.get("audit_id"), "Status:", audit_res.get("status"))
    assert audit_res.get("dataset_profile") is not None
    assert len(audit_res.get("hypotheses", [])) > 0
    assert len(audit_res.get("investigation_trace", [])) > 0
    assert audit_res.get("audit_report_markdown") is not None

    # 4. Verify Dataset Discoveries & Sensitive/Proxy Detection
    print("\n--- 4. VERIFYING DISCOVERIES & SENSITIVE/PROXY CANDIDATES ---")
    ds_prof = audit_res["dataset_profile"]
    print(f"[OK] Rows: {ds_prof['row_count']}, Cols: {ds_prof['column_count']}, Target: '{ds_prof['target_candidate']}'")
    sens_candidates = [s["column_name"] for s in ds_prof["sensitive_candidates"]]
    print(f"[OK] Potentially Sensitive Attributes Identified: {sens_candidates}")
    proxy_candidates = [p["proxy_column"] for p in ds_prof["proxy_candidates"]]
    print(f"[OK] Proxy Feature Candidates Identified: {proxy_candidates}")

    # 5. Verify Adaptive Trace & Evidence Lineage Chain
    print("\n--- 5. VERIFYING ADAPTIVE TRACE & EVIDENCE LINEAGE ---")
    trace = audit_res["investigation_trace"]
    print(f"[OK] Total Adaptive Iterations Executed: {len(trace)}")
    for step in trace:
        print(f"  - Iteration {step['iteration']}:")
        print(f"    Goal: {step['investigation_plan']['investigation_goal']}")
        if step.get("critic_evaluation"):
            print(f"    Critic Verdict: Supports = {step['critic_evaluation']['supports_hypothesis']}, Reasoning = {step['critic_evaluation']['reasoning'][:120]}...")
        print(f"    Adaptive Decision: {step['adaptive_decision']['action'].upper()} -> {step['adaptive_decision']['reasoning']}")

    # 6. Verify Human-Readable Markdown Report
    print("\n--- 6. VERIFYING HUMAN-READABLE MARKDOWN AUDIT REPORT ---")
    report_md = audit_res["audit_report_markdown"]
    assert "# AI Audit Report" in report_md
    assert "## What this AI system does" in report_md
    assert "## What the auditor discovered" in report_md
    print("[OK] Markdown Audit Report generated successfully! Length:", len(report_md), "chars")

    print("\n==========================================================================")
    print("      ALL MASTER E2E INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================================================")


if __name__ == "__main__":
    main()
