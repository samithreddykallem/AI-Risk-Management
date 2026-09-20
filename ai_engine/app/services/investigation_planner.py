import json
import logging
from typing import Optional, List, Any

from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import PlanInvestigationResponse, InvestigationPlan, Observation, Interpretation
from app.core.llm import LLMClient, get_llm_client
from app.prompts.investigation import INVESTIGATION_PROMPT_TEMPLATE, INVESTIGATION_SYSTEM_PROMPT
from app.prompts.adaptive import NEXT_INVESTIGATION_PROMPT_TEMPLATE

logger = logging.getLogger("ai_engine.services.investigation_planner")


class InvestigationPlanner:
    """
    Decoupled service for Phase 3 & Phase 6: Investigation Planning.
    Formulates a targeted, controlled investigation plan for a selected hypothesis using available tools.
    Can also generate adaptive follow-up plans informed by previous investigations and next questions without duplicating past tests.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    def plan_investigation(
        self,
        system_profile: SystemProfile,
        hypothesis: Hypothesis,
        available_tools: List[Any],
        existing_evidence: Optional[List[str]] = None
    ) -> PlanInvestigationResponse:
        default_tool_list = [
            "inspect_repository",
            "run_model",
            "modify_input",
            "compare_outputs",
            "analyze_evidence"
        ]
        tools_list = available_tools if available_tools else default_tool_list

        prompt = INVESTIGATION_PROMPT_TEMPLATE.format(
            purpose=system_profile.purpose,
            intended_use=system_profile.intended_use,
            ai_system_type=system_profile.ai_system_type,
            model_type=system_profile.model_type,
            inputs=json.dumps(system_profile.inputs),
            outputs=json.dumps(system_profile.outputs),
            decision_process=system_profile.decision_process,
            affected_users=json.dumps(system_profile.affected_users),
            autonomy_level=system_profile.autonomy_level,
            sensitive_data=json.dumps(system_profile.sensitive_data),
            human_involvement=system_profile.human_involvement,
            deployment_context=system_profile.deployment_context,
            hypothesis_id=hypothesis.id,
            hypothesis_statement=hypothesis.hypothesis,
            why_plausible=hypothesis.why_it_is_plausible,
            affected_part=hypothesis.affected_part,
            potential_consequence=hypothesis.potential_consequence,
            evidence_support=json.dumps(hypothesis.what_evidence_would_support_it),
            evidence_refute=json.dumps(hypothesis.what_evidence_would_refute_it),
            available_tools=json.dumps(tools_list),
            existing_evidence=json.dumps(existing_evidence or [])
        )

        try:
            logger.info("Formulating initial investigation plan for hypothesis '%s'...", hypothesis.id)
            response = self.llm.generate_structured(
                prompt=prompt,
                schema=PlanInvestigationResponse,
                system_prompt=INVESTIGATION_SYSTEM_PROMPT
            )
            return response
        except Exception as e:
            logger.error("Error generating investigation plan: %s", str(e))
            raise RuntimeError(f"Investigation planning failed: {str(e)}") from e

    def plan_next_investigation(
        self,
        system_profile: SystemProfile,
        hypothesis: Hypothesis,
        previous_plans: List[InvestigationPlan],
        previous_observations: List[Observation],
        previous_interpretation: Optional[Interpretation],
        next_question: str,
        available_tools: List[Any]
    ) -> PlanInvestigationResponse:
        """Formulate a NEW investigation plan informed by previous investigations and next_question."""
        default_tool_list = [
            "inspect_repository",
            "run_model",
            "modify_input",
            "compare_outputs",
            "analyze_evidence"
        ]
        tools_list = available_tools if available_tools else default_tool_list

        prev_goals = [plan.investigation_goal for plan in previous_plans]
        prev_obs = [obs.description for obs in previous_observations]
        interp_summary = previous_interpretation.interpretation if previous_interpretation else "None"

        prompt = NEXT_INVESTIGATION_PROMPT_TEMPLATE.format(
            purpose=system_profile.purpose,
            ai_system_type=system_profile.ai_system_type,
            model_type=system_profile.model_type,
            inputs=json.dumps(system_profile.inputs),
            outputs=json.dumps(system_profile.outputs),
            hypothesis_id=hypothesis.id,
            hypothesis_statement=hypothesis.hypothesis,
            previous_goals=json.dumps(prev_goals),
            previous_observations=json.dumps(prev_obs),
            previous_interpretation=interp_summary,
            next_question=next_question,
            available_tools=json.dumps(tools_list)
        )

        try:
            logger.info("Formulating adaptive follow-up investigation plan for question: '%s'...", next_question)
            response = self.llm.generate_structured(
                prompt=prompt,
                schema=PlanInvestigationResponse,
                system_prompt=INVESTIGATION_SYSTEM_PROMPT
            )
            return response
        except Exception as e:
            logger.error("Error generating next investigation plan: %s", str(e))
            raise RuntimeError(f"Adaptive investigation planning failed: {str(e)}") from e
