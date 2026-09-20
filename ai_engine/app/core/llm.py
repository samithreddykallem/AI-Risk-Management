import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger("ai_engine.core.llm")
T = TypeVar("T", bound=BaseModel)


class LLMClient(ABC):
    """Abstract interface for isolated LLM provider integration."""

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate raw text response from the LLM."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: Optional[str] = None) -> T:
        """Generate structured response parsed into a Pydantic model schema."""
        pass


class OpenAILLMClient(LLMClient):
    """OpenAI-compatible isolated LLM client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("The 'openai' package is required for OpenAILLMClient.")

        self.api_key = api_key or settings.api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("LLM_API_KEY environment variable is missing.")

        self.base_url = base_url or settings.base_url
        self.model_name = model_name or settings.model_name
        self.timeout = timeout or settings.timeout_seconds

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        from openai import APITimeoutError, APIError, AuthenticationError, RateLimitError

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                timeout=self.timeout
            )
            return response.choices[0].message.content or ""

        except APITimeoutError as e:
            logger.error("LLM API request timed out after %s seconds.", self.timeout)
            raise RuntimeError(f"LLM API request timed out after {self.timeout}s.") from e
        except AuthenticationError as e:
            logger.error("LLM API Authentication failed.")
            raise RuntimeError("LLM API Authentication failed. Verify API key.") from e
        except RateLimitError as e:
            logger.error("LLM API Rate limit exceeded.")
            raise RuntimeError("LLM API Rate limit exceeded.") from e
        except APIError as e:
            logger.error("LLM API Error: %s", getattr(e, "message", str(e)))
            raise RuntimeError(f"LLM API Error: {getattr(e, 'message', str(e))}") from e
        except Exception as e:
            logger.error("Unexpected LLM error.")
            raise RuntimeError("Unexpected error during LLM generation.") from e

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: Optional[str] = None) -> T:
        from openai import APITimeoutError, APIError

        schema_json = schema.model_json_schema()
        system_instruction = (
            f"{system_prompt or ''}\n"
            "You MUST respond ONLY with valid JSON matching the following JSON schema:\n"
            f"{json.dumps(schema_json, indent=2)}\n"
            "Do not include markdown formatting or backticks around the JSON."
        ).strip()

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                timeout=self.timeout
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty output returned from LLM.")

            data = json.loads(content)
            return schema.model_validate(data)

        except APITimeoutError as e:
            logger.error("LLM Request timed out during structured output generation.")
            raise RuntimeError(f"LLM request timed out after {self.timeout}s.") from e
        except (APIError, json.JSONDecodeError) as e:
            logger.error("Error generating or parsing structured LLM output.")
            raise RuntimeError(f"Failed to generate structured LLM response: {str(e)}") from e


class MockLLMClient(LLMClient):
    """Mock LLM client generating deterministic mock responses for testing."""

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"[MockLLM Response to prompt: {prompt[:50]}...]"

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: Optional[str] = None) -> T:
        schema_name = schema.__name__
        prompt_lower = prompt.lower()

        if schema_name == "SystemProfile":
            if "vague" in prompt_lower:
                return schema(
                    purpose="Unspecified software system",
                    intended_use="General purpose or unknown",
                    ai_system_type="unknown",
                    model_type="unknown",
                    inputs=[],
                    outputs=[],
                    decision_process="unknown",
                    affected_users=[],
                    decision_impact="unknown",
                    autonomy_level="unknown",
                    data_types=[],
                    sensitive_data=[],
                    external_services=[],
                    human_involvement="unknown",
                    deployment_context="vague - no documentation provided",
                    expected_benefits=[],
                    potential_consequences=[],
                    important_unknowns=["System purpose", "Model architecture", "Input/output specifications", "Deployment context"],
                    assumptions=[],
                    observed_evidence={}
                )
            if "automatically approves" in prompt_lower or "human loan officer" in prompt_lower or "contradict" in prompt_lower:

                return schema(
                    purpose="Automated credit loan evaluation",
                    intended_use="Evaluating retail consumer loan applications",
                    ai_system_type="Decision Classifier / Advisory System",
                    model_type="Loan Approval Model",
                    inputs=["Applicant Data", "Credit History"],
                    outputs=["Approval Decision / Recommendation"],
                    decision_process="Contradictory / Conflict: Description states system automatically approves loan applications, whereas documentation states system only provides recommendations and a human loan officer makes the final decision.",
                    affected_users=["Loan Applicants"],
                    decision_impact="High - Loan financial access",
                    autonomy_level="conflicting_information",
                    data_handled=["Financial Data"],
                    sensitive_data=["Credit Score"],
                    external_services=[],
                    human_involvement="CONTRADICTION: Description specifies automatic approval, while documentation specifies human loan officer final decision.",
                    deployment_context="Banking loan portal",
                    expected_benefits=["Faster processing"],
                    potential_consequences=["Operational accountability ambiguity"],
                    important_unknowns=["Conflicting autonomy model: fully automated approval vs human-in-the-loop recommendation"],
                    assumptions=["Application data is valid"],
                    observed_evidence={
                        "description_claim": "The system automatically approves loan applications.",
                        "documentation_claim": "The AI only provides recommendations. A human loan officer makes the final decision."
                    }
                )
            elif "meditriage" in prompt_lower or "healthcare" in prompt_lower or "triage" in prompt_lower:
                return schema(
                    purpose="Summarize patient clinical notes and suggest emergency triage acuity scores",
                    intended_use="Clinical emergency room triage recommendation support for nurses",
                    ai_system_type="Clinical Decision Support System",
                    model_type="Fine-tuned LLM on clinical notes",
                    inputs=["Patient Clinical Notes", "Chief Complaint", "Vital Signs"],
                    outputs=["Suggested Acuity Level (ESI Level 1-5)", "Clinical Summary"],
                    decision_process="LLM extracts symptoms from clinical text and maps to ESI acuity scale",
                    affected_users=["Emergency Room Patients", "Triage Nurses"],
                    decision_impact="Critical - Emergency patient prioritization and delay risks",
                    autonomy_level="human_in_the_loop",
                    data_handled=["Protected Health Information (PHI)", "Clinical Notes"],
                    sensitive_data=["Patient Names", "Medical History", "PHI"],
                    external_services=["Electronic Health Record (EHR) System"],
                    human_involvement="Triage nurse must verify and sign off on acuity score before assignment",
                    deployment_context="Hospital Emergency Department workstation",
                    expected_benefits=["Reduced triage assessment bottleneck", "Standardized acuity scoring"],
                    potential_consequences=["Delayed emergency care due to under-triage"],
                    important_unknowns=["Specific EHR integration API specs", "Validation dataset diversity"],
                    assumptions=["Triage nurse reviews every suggestion before ordering care"],
                    observed_evidence={
                        "purpose": "Extracted from description: 'Summarizes patient clinical notes and suggests emergency triage acuity scores'",
                        "human_involvement": "Extracted from documentation: 'Nurse must verify all triage acuity assignments'"
                    }
                )
            elif "fraud" in prompt_lower:
                return schema(
                    purpose="Analyze payment transaction velocity, IP geolocation, and amount to flag credit card fraud",
                    intended_use="Automated fraud detection in payment processing gateway",
                    ai_system_type="Automated Fraud Detection Classifier",
                    model_type="Isolation Forest and XGBoost Ensemble",
                    inputs=["Transaction Amount", "IP Country", "Transaction Velocity"],
                    outputs=["Fraud Risk Score (0-1)", "Automated Action (Approve / Review / Auto-Decline)"],
                    decision_process="Calculates risk score based on anomaly metrics; high velocity triggers auto-decline",
                    affected_users=["Cardholders", "Merchant Risk Analysts"],
                    decision_impact="High - Immediate block of payment capability",
                    autonomy_level="fully_autonomous_for_high_risk",
                    data_handled=["Payment Transaction Data", "IP Address", "Card Hash"],
                    sensitive_data=["Payment Card Identifiers", "Location Data"],
                    external_services=["Payment Gateway API", "GeoIP Lookup Service"],
                    human_involvement="Asynchronous review of flagged transactions after auto-decline",
                    deployment_context="Real-time payment transaction pipeline",
                    expected_benefits=["Prevent real-time fraudulent charge loss"],
                    potential_consequences=["Legitimate cardholder false decline during travel"],
                    important_unknowns=["Threshold for auto-decline vs manual queue"],
                    assumptions=["GeoIP database accuracy"],
                    observed_evidence={
                        "purpose": "Extracted from description: 'Analyzes payment transaction velocity, IP geolocation, and transaction amount'",
                        "autonomy_level": "Extracted from documentation: 'High velocity transactions trigger auto-decline'"
                    }
                )

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

        elif schema_name == "HypothesisGenerationResponse":
            from app.schemas.hypothesis import Hypothesis
            
            if "vague" in prompt_lower or "no documentation provided" in prompt_lower:
                return schema(hypotheses=[])

            if "triage" in prompt_lower or "clinical" in prompt_lower:
                return schema(
                    hypotheses=[
                        Hypothesis(
                            id="HYP-H01",
                            hypothesis="The LLM clinical note summarizer might omit atypical cardiac symptoms in female patients.",
                            why_it_is_plausible="System relies on LLM summarization of clinical text, and medical literature notes gender differences in symptom presentation.",
                            supporting_evidence=["Model type: Fine-tuned LLM on clinical notes", "Inputs: Patient Clinical Notes"],
                            affected_part="Clinical text summarizer and symptom extraction",
                            potential_consequence="Under-triage of female cardiac patients leading to delayed emergency treatment.",
                            what_evidence_would_support_it=["Higher rate of lower acuity suggestions for female clinical notes with atypical symptoms."],
                            what_evidence_would_refute_it=["Consistent acuity scoring across male and female clinical notes describing cardiac symptoms."],
                            priority="high",
                            confidence=0.88
                        )
                    ]
                )
            elif "fraud" in prompt_lower:
                return schema(
                    hypotheses=[
                        Hypothesis(
                            id="HYP-F01",
                            hypothesis="The transaction velocity auto-decline rule may falsely block legitimate cardholders traveling internationally.",
                            why_it_is_plausible="System uses IP Country and Velocity to trigger fully autonomous auto-declines.",
                            supporting_evidence=["Documentation states high velocity triggers auto-decline", "Inputs include IP Country"],
                            affected_part="Auto-decline decision engine",
                            potential_consequence="Legitimate user disruption and false positives during international travel.",
                            what_evidence_would_support_it=["Increased false decline rate when IP Country differs from home country."],
                            what_evidence_would_refute_it=["No change in decline rates for verified traveling users."],
                            priority="medium",
                            confidence=0.82
                        )
                    ]
                )

            return schema(
                hypotheses=[
                    Hypothesis(
                        id="HYP-001",
                        hypothesis="The scoring model may produce lower credit risk scores for applicants in certain zip codes despite identical financial profiles.",
                        why_it_is_plausible="System handles Zip Code as an input parameter alongside financial metrics in a decision support pipeline.",
                        supporting_evidence=["Input includes 'Zip Code'", "Sensitive data includes 'Demographic Proxy Attributes'"],
                        affected_part="Input processing and score calculation",
                        potential_consequence="Disparate financial impact on applicants from underrepresented postal codes.",
                        what_evidence_would_support_it=["Statistically significant score variance when changing only the Zip Code parameter."],
                        what_evidence_would_refute_it=["Identical score output across contrasting Zip Code inputs with fixed financial data."],
                        priority="high",
                        confidence=0.85
                    )
                ]
            )

        elif schema_name == "PlanInvestigationResponse":
            from app.schemas.investigation import InvestigationPlan, InvestigationStep

            if "insufficient_tools" in prompt_lower or "no_tools" in prompt_lower:
                return schema(
                    status="insufficient_capability",
                    investigation_plan=None,
                    reason="Available investigation tools are insufficient to inspect or execute probes against the affected part of the system."
                )

            if "does changing transaction amount alter" in prompt_lower or "amount perturbation" in prompt_lower or "amount sensitivity" in prompt_lower:
                return schema(
                    status="ready",
                    investigation_plan=InvestigationPlan(
                        hypothesis_id="HYP-F01",
                        investigation_goal="Investigate transaction amount threshold sensitivity when location is fixed.",
                        reasoning="Location parameter produced negligible variance; testing transaction amount variable next.",
                        steps=[
                            InvestigationStep(
                                step_id="STEP-301",
                                objective="Modify transaction amount while holding location constant.",
                                tool="modify_input",
                                parameters={"base_input": {"amount": 5000, "location": "Hyderabad"}, "perturbations": {"amount": 50000}},
                                expected_observation="Transaction amount scaled to 50000",
                                evidence_required="Amount perturbed payload recorded",
                                reasoning="Probes transaction amount threshold sensitivity."
                            )
                        ],
                        success_criteria="Evidence of output score change under transaction amount scaling.",
                        possible_outcomes=["High amount triggers auto-block", "Amount has negligible effect"]
                    ),
                    reason=None
                )

            if "does the observed difference persist" in prompt_lower:
                return schema(
                    status="ready",
                    investigation_plan=InvestigationPlan(
                        hypothesis_id="HYP-001",
                        investigation_goal="Follow-up: Test whether location variance persists across multiple controlled transaction amounts.",
                        reasoning="Testing across additional transaction amounts verifies whether location variance is consistent.",
                        steps=[
                            InvestigationStep(
                                step_id="STEP-101",
                                objective="Modify location variable for secondary high-amount transaction.",
                                tool="modify_input",
                                parameters={"base_input": {"amount": 15000, "location": "Hyderabad"}, "perturbations": {"location": "Mumbai"}},
                                expected_observation="Perturbed secondary transaction prepared",
                                evidence_required="Secondary perturbed input recorded",
                                reasoning="Tests secondary transaction amount with location perturbation."
                            ),
                            InvestigationStep(
                                step_id="STEP-102",
                                objective="Compare secondary transaction outputs across location change.",
                                tool="compare_outputs",
                                parameters={"output_a": {"score": 0.82}, "output_b": {"score": 0.83}, "metric": "score_difference"},
                                expected_observation="Secondary output difference evaluated",
                                evidence_required="Secondary output variance recorded",
                                reasoning="Determines if location variance persists at higher amounts."
                            )
                        ],
                        success_criteria="Evidence of output variance across multiple transaction amounts.",
                        possible_outcomes=["Persistent variance confirms hypothesis", "Negligible variance weakens hypothesis"]
                    ),
                    reason=None
                )

            return schema(
                status="ready",
                investigation_plan=InvestigationPlan(
                    hypothesis_id="HYP-001",
                    investigation_goal="Gather evidence on Zip Code score variance using controlled input perturbations.",
                    reasoning="By holding all financial variables constant and altering only the Zip Code, any change in output demonstrates location-based sensitivity.",
                    steps=[
                        InvestigationStep(
                            step_id="STEP-1",
                            objective="Establish baseline score for reference applicant profile.",
                            tool="modify_input",
                            parameters={"base_input": {"income": 65000, "credit_score": 710, "zip_code": "90210"}, "perturbations": {}},
                            expected_observation="Baseline input prepared",
                            evidence_required="Baseline input recorded",
                            reasoning="Establishes baseline output payload."
                        ),
                        InvestigationStep(
                            step_id="STEP-2",
                            objective="Modify Zip Code variable to target underrepresented postal code while keeping income constant.",
                            tool="modify_input",
                            parameters={"base_input": {"income": 65000, "credit_score": 710, "zip_code": "90210"}, "perturbations": {"zip_code": "90011"}},
                            expected_observation="Input modified with perturbed zip code",
                            evidence_required="Perturbed input payload recorded",
                            reasoning="Controls for all variables except the target Zip Code variable."
                        ),
                        InvestigationStep(
                            step_id="STEP-3",
                            objective="Compare baseline input and perturbed input.",
                            tool="compare_outputs",
                            parameters={"output_a": {"zip": "90210"}, "output_b": {"zip": "90011"}, "metric": "field_difference"},
                            expected_observation="Variance in location fields detected",
                            evidence_required="Quantitative difference recorded",
                            reasoning="Determines whether Zip Code parameter was altered."
                        )
                    ],
                    success_criteria="Evidence of output difference when only Zip Code parameter is altered.",
                    possible_outcomes=[
                        "Significant variance confirms Zip Code sensitivity hypothesis.",
                        "No variance refutes Zip Code sensitivity hypothesis."
                    ]
                ),
                reason=None
            )

        elif schema_name == "Interpretation":
            if "0.83" in prompt_lower or "small difference" in prompt_lower or "0.01" in prompt_lower:
                return schema(
                    interpretation="An output difference was observed (0.82 vs 0.83), but the magnitude is small (0.01). The evidence is currently insufficient to claim discrimination or bias without additional investigation.",
                    hypothesis_status="inconclusive",
                    confidence=0.50,
                    supporting_evidence=["Small score variance of 0.01 observed across location perturbation."],
                    contradicting_evidence=[],
                    remaining_unknowns=["Whether variance increases under non-standard location parameters", "Statistical significance across dataset"]
                )
            elif "weakened" in prompt_lower or "identical score" in prompt_lower:
                return schema(
                    interpretation="The executed investigation steps showed no output variance when changing the target input field. This weakens the hypothesis.",
                    hypothesis_status="weakened",
                    confidence=0.85,
                    supporting_evidence=[],
                    contradicting_evidence=["Identical outputs produced across perturbed input runs."],
                    remaining_unknowns=[]
                )
            elif "inconclusive" in prompt_lower or "unavailable" in prompt_lower or "insufficient" in prompt_lower:
                return schema(
                    interpretation="Key investigation tools were unavailable, preventing model output comparison. The evidence is inconclusive.",
                    hypothesis_status="inconclusive",
                    confidence=0.40,
                    supporting_evidence=[],
                    contradicting_evidence=[],
                    remaining_unknowns=["Executable model interface execution result"]
                )

            return schema(
                interpretation="The observation supports the hypothesis that modifying the Zip Code parameter alters the output payload while holding other variables constant.",
                hypothesis_status="supported",
                confidence=0.88,
                supporting_evidence=["Output variance detected via compare_outputs tool when modifying location variable."],
                contradicting_evidence=[],
                remaining_unknowns=["Long-term operational dataset distribution"]
            )

        elif schema_name == "AdaptiveDecision":
            if "almost no effect" in prompt_lower or "negligible" in prompt_lower:
                return schema(
                    action="continue",
                    reasoning="Changing location had almost no effect on fraud risk output (0.82 vs 0.83). Formulating follow-up test to evaluate transaction amount sensitivity instead.",
                    evidence_summary="Location perturbation produced negligible score variance of 0.01.",
                    remaining_uncertainties=["Does changing transaction amount alter fraud risk classification when location is fixed?"],
                    next_question="Does changing transaction amount alter fraud risk classification when location is fixed?",
                    confidence=0.80
                )
            elif "large output difference" in prompt_lower or "large difference" in prompt_lower or "substantial" in prompt_lower:
                return schema(
                    action="continue",
                    reasoning="Changing location caused a large output difference (0.82 vs 0.15). Formulating follow-up test to identify regional location boundary thresholds.",
                    evidence_summary="Location perturbation produced substantial score drop from 0.82 to 0.15.",
                    remaining_uncertainties=["Which specific regional location parameters trigger high-risk auto-decline vs approval?"],
                    next_question="Which regional location parameters trigger the high-risk auto-decline threshold?",
                    confidence=0.85
                )

            # If prompt indicates iteration 1 and we want to test multi-step continue
            if "iteration_count: 1" in prompt_lower or "previous iteration trace count: 1" in prompt_lower:
                # Check if prompt asks to stop
                if "stop_now" in prompt_lower or "sufficient" in prompt_lower:
                    return schema(
                        action="stop",
                        reasoning="Evidence collected in initial iteration is sufficient to address the hypothesis.",
                        evidence_summary="Output variance confirmed via compare_outputs tool.",
                        remaining_uncertainties=[],
                        next_question=None,
                        confidence=0.88
                    )
                return schema(
                    action="continue",
                    reasoning="Initial input comparison revealed slight location variance. Formulating follow-up test to verify persistence across transaction amounts.",
                    evidence_summary="Location variance detected in baseline input modification.",
                    remaining_uncertainties=["Does the observed variance persist across higher transaction amounts?"],
                    next_question="Does the observed difference persist across multiple otherwise identical transactions?",
                    confidence=0.75
                )

            # Default stop for iteration >= 2
            return schema(
                action="stop",
                reasoning="Follow-up investigation completed. Evidence gathered is sufficient to draw conclusions regarding hypothesis.",
                evidence_summary="Multi-step input perturbations confirmed output consistency across transaction amounts.",
                remaining_uncertainties=[],
                next_question=None,
                confidence=0.90
            )

        try:
            return schema.model_construct()
        except Exception:
            raise ValueError(f"MockLLMClient does not have a predefined handler for schema: {schema_name}")


def get_llm_client(provider_type: Optional[str] = None) -> LLMClient:
    """Factory function to get an initialized LLMClient instance."""
    selected_provider = (provider_type or settings.provider_type).lower()

    if selected_provider == "openai" or (settings.api_key and selected_provider != "mock"):
        try:
            return OpenAILLMClient()
        except Exception as e:
            logger.warning("Failed to initialize OpenAILLMClient (%s). Falling back to MockLLMClient.", str(e))
            return MockLLMClient()

    return MockLLMClient()
