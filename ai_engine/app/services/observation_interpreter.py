import json
import logging
from typing import Optional, List

from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import InvestigationPlan, ToolExecution, Observation, Interpretation
from app.core.llm import LLMClient, get_llm_client
from app.prompts.interpretation import INTERPRETATION_PROMPT_TEMPLATE, INTERPRETATION_SYSTEM_PROMPT

logger = logging.getLogger("ai_engine.services.observation_interpreter")


class ObservationInterpreter:
    """
    Decoupled service interpreting tool execution observations relative to a specific hypothesis.
    Evaluates whether evidence supports, weakens, or is inconclusive for the hypothesis.
    Does NOT issue global ethical verdicts.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    def interpret_evidence(
        self,
        system_profile: SystemProfile,
        hypothesis: Hypothesis,
        investigation_plan: InvestigationPlan,
        executed_steps: List[ToolExecution],
        observations: List[Observation]
    ) -> Interpretation:
        logger.info("Interpreting evidence for hypothesis '%s'...", hypothesis.id)

        # Prepare JSON serialized representations for prompt grounding
        tool_executions_json = json.dumps([step.model_dump() for step in executed_steps], indent=2)
        observations_json = json.dumps([obs.model_dump() for obs in observations], indent=2)
        all_evidence = []
        for step in executed_steps:
            all_evidence.extend(step.evidence)
        for obs in observations:
            all_evidence.extend(obs.evidence)
        evidence_json = json.dumps(list(set(all_evidence)), indent=2)

        prompt = INTERPRETATION_PROMPT_TEMPLATE.format(
            purpose=system_profile.purpose,
            intended_use=system_profile.intended_use,
            ai_system_type=system_profile.ai_system_type,
            hypothesis_id=hypothesis.id,
            hypothesis_statement=hypothesis.hypothesis,
            why_plausible=hypothesis.why_it_is_plausible,
            affected_part=hypothesis.affected_part,
            potential_consequence=hypothesis.potential_consequence,
            investigation_goal=investigation_plan.investigation_goal,
            plan_reasoning=investigation_plan.reasoning,
            tool_executions_json=tool_executions_json,
            observations_json=observations_json,
            evidence_json=evidence_json
        )

        try:
            interpretation = self.llm.generate_structured(
                prompt=prompt,
                schema=Interpretation,
                system_prompt=INTERPRETATION_SYSTEM_PROMPT
            )
            return interpretation
        except Exception as e:
            logger.error("Error interpreting evidence: %s", str(e))
            raise RuntimeError(f"Evidence interpretation failed: {str(e)}") from e
