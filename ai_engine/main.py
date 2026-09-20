import sys
import json
import argparse
from typing import Dict, Any

from ai_engine.models.system_input import SystemInput
from ai_engine.workflows.audit_orchestrator import AuditOrchestrator


def get_sample_system_input() -> SystemInput:
    """Return a sample high-risk AI System specification for testing."""
    return SystemInput(
        system_name="CreditRisk-Predictor-v2",
        problem_solved="Automates credit risk evaluation and loan approval decisions for consumer banking applicants.",
        intended_use_case="Consumer lending decisions across online and mobile banking channels.",
        input_types=["Applicant Financial History", "Income", "Employment Status", "Zip Code", "Age", "Credit History"],
        output_types=["Credit Risk Score (300-850)", "Approval Recommendation (Approved / Denied / Manual Review)"],
        affected_stakeholders=["Loan Applicants", "Banking Underwriters", "Consumer Credit Protection Regulators"],
        autonomy_level="human_in_the_loop_advisory",
        data_handled=["Personally Identifiable Information (PII)", "Financial Records", "Credit Scores"],
        model_implementation_details="Ensemble Gradient Boosting model combined with an LLM prompt wrapper for explanation generation.",
        potential_consequences=[
            "Wrongful loan rejection causing financial hardship",
            "Disparate impact / demographic proxy discrimination",
            "Privacy data leakage via prompt explanations"
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="AI Risk Manager Engine CLI")
    parser.add_argument("--input-file", type=str, help="Path to JSON file containing SystemInput specification")
    parser.add_argument("--output-file", type=str, help="Path to save output AuditReport JSON")
    args = parser.parse_args()

    if args.input_file:
        with open(args.input_file, "r") as f:
            data = json.load(f)
            system_input = SystemInput(**data)
    else:
        print("[*] No input file specified. Using sample CreditRisk-Predictor system input...")
        system_input = get_sample_system_input()

    print(f"\n=======================================================")
    print(f"       AI RISK MANAGER - AI ENGINE AUDITOR            ")
    print(f"=======================================================\n")
    print(f"Auditing AI System: {system_input.system_name}")
    print(f"Problem Solved:    {system_input.problem_solved}")
    print(f"Autonomy Level:    {system_input.autonomy_level}\n")

    orchestrator = AuditOrchestrator()
    report = orchestrator.run_audit(system_input)

    print("\n--- AUDIT STATE LOG ---")
    for log_line in orchestrator.state_tracker.get_summary_log():
        print(log_line)

    print("\n=======================================================")
    print(f"                  AUDIT REPORT SUMMARY                 ")
    print(f"=======================================================")
    print(f"Audit ID:                  {report.audit_id}")
    print(f"System:                    {report.system_name}")
    print(f"Overall Risk Rating:       {report.overall_risk_rating.value}")
    print(f"Hypotheses Evaluated:      {report.total_hypotheses_evaluated}")
    print(f"Confirmed Risk Findings:   {len(report.verified_findings)}")
    print(f"Refuted Hypotheses:        {len(report.refuted_hypotheses)}")
    print(f"Inconclusive Hypotheses:   {len(report.inconclusive_hypotheses)}")
    print(f"\nExecutive Summary:\n{report.executive_summary}\n")

    if report.verified_findings:
        print("--- VERIFIED RISK FINDINGS ---")
        for idx, finding in enumerate(report.verified_findings, 1):
            print(f"\n[{idx}] [{finding.severity.value}] {finding.title} (Dimension: {finding.risk_dimension.value})")
            print(f"    Statement:  {finding.hypothesis_statement}")
            print(f"    Evidence:   {finding.evidence_summary}")
            print(f"    Mitigation: {finding.recommended_mitigation}")

    if report.actionable_recommendations:
        print("\n--- ACTIONABLE RECOMMENDATIONS ---")
        for rec in report.actionable_recommendations:
            print(f" - {rec}")

    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(report.model_dump_json(indent=2))
        print(f"\n[+] Full Audit Report saved to: {args.output_file}")


if __name__ == "__main__":
    main()
