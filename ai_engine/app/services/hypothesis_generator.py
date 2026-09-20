import json
import logging
from typing import Optional, List

from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import HypothesisGenerationResponse
from app.core.llm import LLMClient, get_llm_client
from app.prompts.hypothesis import HYPOTHESIS_PROMPT_TEMPLATE, HYPOTHESIS_SYSTEM_PROMPT

logger = logging.getLogger("ai_engine.services.hypothesis_generator")


class HypothesisGenerator:
    """
    Decoupled service for Phase 2: System-Specific Hypothesis Generation.
    Formulates plausible, system-specific risk hypotheses grounded strictly in evidence from System Profile.
    Does NOT use fixed ethical checklists or domain-specific hardcoded rules.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    def generate_hypotheses(
        self,
        system_profile: SystemProfile,
        available_evidence: Optional[List[str]] = None,
        important_unknowns: Optional[List[str]] = None
    ) -> HypothesisGenerationResponse:
        evidence_str = json.dumps(available_evidence or [])
        unknowns_str = json.dumps(important_unknowns or system_profile.important_unknowns or [])

        prompt = HYPOTHESIS_PROMPT_TEMPLATE.format(
            purpose=system_profile.purpose,
            intended_use=system_profile.intended_use,
            ai_system_type=system_profile.ai_system_type,
            model_type=system_profile.model_type,
            inputs=json.dumps(system_profile.inputs),
            outputs=json.dumps(system_profile.outputs),
            decision_process=system_profile.decision_process,
            affected_users=json.dumps(system_profile.affected_users),
            decision_impact=system_profile.decision_impact,
            autonomy_level=system_profile.autonomy_level,
            data_types=json.dumps(system_profile.data_types),
            sensitive_data=json.dumps(system_profile.sensitive_data),
            external_services=json.dumps(system_profile.external_services),
            human_involvement=system_profile.human_involvement,
            deployment_context=system_profile.deployment_context,
            expected_benefits=json.dumps(system_profile.expected_benefits),
            potential_consequences=json.dumps(system_profile.potential_consequences),
            important_unknowns=unknowns_str,
            assumptions=json.dumps(system_profile.assumptions),
            observed_evidence=json.dumps(system_profile.observed_evidence),
            available_evidence=evidence_str
        )

        try:
            logger.info("Generating system-specific hypotheses for AI system...")
            response = self.llm.generate_structured(
                prompt=prompt,
                schema=HypothesisGenerationResponse,
                system_prompt=HYPOTHESIS_SYSTEM_PROMPT
            )
            return response
        except Exception as e:
            logger.error("Error generating hypotheses: %s", str(e))
            raise RuntimeError(f"Hypothesis generation failed: {str(e)}") from e
