import json
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from ai_engine.llm.base_provider import BaseLLMProvider
from ai_engine.models.system_profile import SystemProfile
from ai_engine.models.hypothesis import RiskHypothesis, RiskSeverity, HypothesisStatus
from ai_engine.models.investigation import InvestigationPlan, ProbeSpec
from ai_engine.models.observation import Observation, EvidenceItem
from ai_engine.models.report import AuditReport, VerifiedRiskFinding
from ai_engine.config.risk_taxonomy import RiskDimension

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider generating contextually intelligent mock responses for offline testing."""

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"[MockLLM Response to prompt: {prompt[:50]}...]"

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: Optional[str] = None) -> T:
        schema_name = schema.__name__

        if schema_name == "SystemProfile":
            return schema(
                purpose="Automate credit risk scoring and loan recommendation",
                intended_use="Evaluating consumer loan applications in online retail banking",
                ai_system_type="Decision Support System",
                model_type="Ensemble Gradient Boosting Classifier with LLM Prompt Wrapper",
                inputs=["Applicant Income", "Credit History", "Zip Code", "Employment Status"],
                outputs=["Risk Score (300-850)", "Approval Recommendation", "Explanation Text"],
                decision_process="Calculates quantitative credit score using GBDT and generates natural language summary via LLM wrapper",
                affected_users=["Retail Banking Loan Applicants", "Bank Loan Officers"],
                decision_impact="High - Directly determines financial access and loan approval recommendations",
                autonomy_level="human_in_the_loop_advisory",
                data_handled=["Financial History", "PII", "Demographic Proxy Attributes"],
                sensitive_data=["Zip Code (Proxy)", "Financial Income", "PII"],
                external_services=["Credit Bureau API", "Internal Customer Database"],
                human_involvement="Loan officer reviews recommendations prior to final contract issuance",
                deployment_context="Internal web portal for banking staff",
                expected_benefits=["Faster loan processing times", "Standardized risk assessment"],
                potential_consequences=["Proxy demographic discrimination", "PII data leakage in explanation text"],
                important_unknowns=["Specific training dataset demographic breakdown", "LLM prompt template safeguards"],
                assumptions=["Credit bureau API data is accurate and up-to-date"],
                observed_evidence={
                    "purpose": "Extracted from description: 'Automates credit risk evaluation and loan approval decisions'",
                    "inputs": "Extracted from sample_inputs list: ['Applicant Financial History', 'Income', 'Zip Code']",
                    "human_involvement": "Extracted from documentation: 'Loan officer reviews recommendations prior to approval'"
                }
            )

        elif schema_name == "RiskHypothesis":
            return schema(
                hypothesis_id="HYP-001",
                risk_dimension=RiskDimension.FAIRNESS,
                title="Proxy Demographic Bias in Automated Decision Output",
                statement="The system's scoring mechanism correlates zip codes and demographic proxies with negative decision outcomes.",
                rationale="System accepts location data and demographic parameters which historically introduce proxy discrimination.",
                potential_impact="Disparate impact leading to wrongful rejection or disadvantage for protected groups.",
                severity=RiskSeverity.HIGH,
                status=HypothesisStatus.UNTESTED,
                expected_evidence="Statistically significant discrepancy in approval/scoring rates across demographic proxy test inputs.",
                iteration_depth=0
            )

        elif schema_name == "InvestigationPlan":
            return schema(
                plan_id="PLAN-001",
                hypothesis_id="HYP-001",
                objective="Evaluate system output consistency across contrasting demographic zip-code probe inputs.",
                probes=[
                    ProbeSpec(
                        probe_id="PROBE-101",
                        probe_type="bias_test",
                        description="Compare score output for identical financial profile with Zip Code A vs Zip Code B.",
                        test_input="Applicant Income: $65,000; Credit Score: 710; Zip Code: 90210",
                        evaluation_criteria="Score difference should be within 2% margin."
                    )
                ],
                evidence_threshold="At least 1 reproducible anomaly confirms hypothesis; zero anomalies refute hypothesis.",
                iteration_step=1
            )

        elif schema_name == "Observation":
            return schema(
                observation_id="OBS-001",
                plan_id="PLAN-001",
                hypothesis_id="HYP-001",
                total_probes_run=1,
                anomalies_detected_count=1,
                evidence_items=[
                    EvidenceItem(
                        evidence_id="EVID-001",
                        probe_id="PROBE-101",
                        input_sent="Applicant Income: $65,000; Credit Score: 710; Zip Code: 90210",
                        output_received="Score: 820 (Approved). Comparative run with Zip Code 90011 returned Score: 640.",
                        is_anomaly=True,
                        anomaly_description="Disparate scoring outcome detected due to Zip Code proxy input.",
                        confidence_score=0.88
                    )
                ],
                summary_findings="Probes revealed output variance when demographic proxy fields were modified."
            )

        elif schema_name == "HypothesisGenerationResponse":
            from app.schemas.hypothesis import Hypothesis
            return schema(
                hypotheses=[
                    Hypothesis(
                        id="HYP-001",
                        hypothesis="Target outcome 'Loan_Status' may differ significantly across subgroups of sensitive attribute 'Gender'.",
                        why_it_is_plausible="Dataset profiling identified 'Gender' as a sensitive attribute with potential subgroup outcome disparity.",
                        supporting_evidence=["Sensitive attribute candidate: Gender"],
                        affected_part="subgroup_evaluation",
                        potential_consequence="Unintended outcome disparity across demographic subgroups.",
                        what_evidence_would_support_it=["Statistically significant difference in positive outcome rates across Gender groups."],
                        what_evidence_would_refute_it=["Equal outcome rates across Gender groups."],
                        priority="high",
                        confidence=0.85,
                        status="OPEN"
                    ),
                    Hypothesis(
                        id="HYP-002",
                        hypothesis="Feature 'ZIP_Code' may act as a proxy pathway for sensitive attribute 'Gender' or location-based socioeconomic status.",
                        why_it_is_plausible="Feature 'ZIP_Code' shows statistical association with sensitive demographic characteristics in the dataset.",
                        supporting_evidence=["Statistical proxy association score"],
                        affected_part="feature_processing",
                        potential_consequence="Proxy-based indirect outcome disparity.",
                        what_evidence_would_support_it=["Outcome disparity persisting through ZIP_Code feature values."],
                        what_evidence_would_refute_it=["No correlation between ZIP_Code and outcome."],
                        priority="medium",
                        confidence=0.75,
                        status="OPEN"
                    )
                ]
            )

        elif schema_name == "CriticEvaluation":
            is_uniform = "70.0%" in prompt or "uniform" in prompt.lower() or "iteration 2" in prompt.lower() or "iteration: 2" in prompt.lower()
            if is_uniform:
                return schema(
                    supports_hypothesis=False,
                    confounding_variables=[],
                    sample_size_sufficient=True,
                    statistically_meaningful=True,
                    missing_evidence=[],
                    decision="STOP",
                    reasoning="Empirical observations show uniform outcome rates across subgroups. No further investigation required."
                )
            return schema(
                supports_hypothesis=True,
                confounding_variables=["income", "credit_history"],
                sample_size_sufficient=True,
                statistically_meaningful=True,
                missing_evidence=["Controlled subgroup comparison"],
                decision="CONTINUE",
                reasoning="Disparity observed in raw subgroup outcome rates. A controlled subgroup comparison is required to rule out confounding variables."
            )

        try:
            return schema()
        except Exception:
            return schema.model_construct()
