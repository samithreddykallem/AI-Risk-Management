import json
import logging
from typing import Optional, List, Any

from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import InvestigationPlan, Observation, Interpretation
from app.schemas.adaptive import (
    AdaptiveDecision,
    AdaptiveIteration,
    AdaptiveInvestigationResult,
    RunAdaptiveInvestigationResponse
)
from app.services.investigation_planner import InvestigationPlanner
from app.services.investigation_executor import InvestigationExecutor
from app.services.observation_interpreter import ObservationInterpreter
from app.core.llm import LLMClient, get_llm_client
from app.prompts.adaptive import ADAPTIVE_DECISION_PROMPT_TEMPLATE, ADAPTIVE_DECISION_SYSTEM_PROMPT

logger = logging.getLogger("ai_engine.services.adaptive_agent")


class AdaptiveInvestigationAgent:
    """
    Core adaptive investigation agent for AI Risk Manager.
    Drives an evidence-guided multi-iteration loop:
    Observe -> Interpret -> Remaining Uncertainty -> Next Question -> Next Investigation -> Execute -> Repeat/Stop
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()
        self.planner = InvestigationPlanner(self.llm)
        self.executor = InvestigationExecutor()
        self.interpreter = ObservationInterpreter(self.llm)

    def run_adaptive_loop(
        self,
        system_profile: SystemProfile,
        hypotheses: List[Hypothesis],
        available_tools: List[Any],
        initial_evidence: Optional[List[str]] = None,
        max_iterations: int = 5
    ) -> AdaptiveInvestigationResult:
        logger.info("Starting Adaptive Investigation Agent loop (max_iterations=%d)...", max_iterations)

        if not hypotheses:
            return AdaptiveInvestigationResult(
                status="completed",
                iterations=[],
                final_evidence=list(initial_evidence or []),
                unresolved_questions=["No risk hypotheses were provided or generated."],
                limitations=["No hypotheses to investigate."]
            )

        active_hypothesis = hypotheses[0]
        iterations_log: List[AdaptiveIteration] = []
        all_evidence: List[str] = list(initial_evidence or [])
        all_previous_plans: List[InvestigationPlan] = []
        all_previous_observations: List[Observation] = []
        last_interpretation: Optional[Interpretation] = None
        limitations: List[str] = []
        unresolved_questions: List[str] = []
        next_q: Optional[str] = None

        overall_status = "completed"

        for iter_idx in range(1, max_iterations + 1):
            logger.info("--- Adaptive Loop Iteration %d/%d ---", iter_idx, max_iterations)

            # 1. Plan Investigation
            if iter_idx == 1 or not next_q:
                plan_response = self.planner.plan_investigation(
                    system_profile=system_profile,
                    hypothesis=active_hypothesis,
                    available_tools=available_tools,
                    existing_evidence=all_evidence
                )
            else:
                plan_response = self.planner.plan_next_investigation(
                    system_profile=system_profile,
                    hypothesis=active_hypothesis,
                    previous_plans=all_previous_plans,
                    previous_observations=all_previous_observations,
                    previous_interpretation=last_interpretation,
                    next_question=next_q,
                    available_tools=available_tools
                )

            if plan_response.status == "insufficient_capability" or not plan_response.investigation_plan:
                logger.warning("Planner returned insufficient_capability: %s", plan_response.reason)
                limitations.append(f"Iteration {iter_idx}: {plan_response.reason or 'Insufficient tool capability for hypothesis.'}")
                if iter_idx == 1:
                    overall_status = "insufficient_capability"
                break

            current_plan = plan_response.investigation_plan
            all_previous_plans.append(current_plan)

            # 2. Execute Investigation Steps
            exec_result = self.executor.execute_plan(
                system_profile=system_profile,
                hypothesis=active_hypothesis,
                investigation_plan=current_plan,
                available_tools=available_tools,
                initial_evidence=all_evidence
            )
            all_evidence.extend(exec_result.evidence)
            all_previous_observations.extend(exec_result.observations)

            if exec_result.limitations:
                limitations.extend(exec_result.limitations)

            if exec_result.status == "insufficient_capability" and not exec_result.observations:
                overall_status = "insufficient_capability"
                logger.info("Tools were unavailable during execution; stopping adaptive loop.")
                break

            # 3. Interpret Observations
            interpretation = self.interpreter.interpret_evidence(
                system_profile=system_profile,
                hypothesis=active_hypothesis,
                investigation_plan=current_plan,
                executed_steps=exec_result.executed_steps,
                observations=exec_result.observations
            )
            last_interpretation = interpretation

            # 4. Run Independent Evidence Critic Role
            from services.llm_roles import run_evidence_critic_role
            obs_text = " | ".join([getattr(obs, "description", str(obs)) for obs in exec_result.observations])
            critic_eval = run_evidence_critic_role(
                hypothesis=active_hypothesis,
                investigation_summary=current_plan.investigation_goal,
                actual_tool_output=obs_text,
                iteration=iter_idx,
                control_variable="income" if iter_idx > 1 else None
            )

            # Update active hypothesis status based on critic
            if critic_eval.supports_hypothesis and iter_idx > 1:
                active_hypothesis.status = "SUPPORTED"
            elif not critic_eval.supports_hypothesis and iter_idx > 1:
                active_hypothesis.status = "WEAKENED"
            elif critic_eval.supports_hypothesis:
                active_hypothesis.status = "OPEN"

            # 5. Adaptive Decision Reasoning
            adaptive_decision = self._make_adaptive_decision(
                system_profile=system_profile,
                hypothesis=active_hypothesis,
                investigation_plan=current_plan,
                executed_steps=exec_result.executed_steps,
                observations=exec_result.observations,
                interpretation=interpretation,
                iteration_count=iter_idx,
                all_evidence=all_evidence
            )

            # Force action from Critic recommendation if available
            if critic_eval.decision == "CONTINUE" and iter_idx < max_iterations:
                adaptive_decision.action = "continue"
                adaptive_decision.next_question = "Perform controlled subgroup comparison controlling for confounding financial variables (income/credit score)."
            elif critic_eval.decision == "STOP":
                adaptive_decision.action = "stop"

            # Construct Evidence Lineage Chain record
            from app.schemas.adaptive import EvidenceLineage
            plan_identifier = getattr(current_plan, "plan_id", getattr(current_plan, "id", f"PLAN-{iter_idx}"))
            lineage = EvidenceLineage(
                dataset_name=getattr(system_profile, "dataset_name", "uploaded_dataset"),
                discovery_summary=f"Sensitive attribute evaluation for {active_hypothesis.id}",
                hypothesis_id=active_hypothesis.id,
                hypothesis_text=active_hypothesis.hypothesis,
                investigation_id=plan_identifier,
                tool_name=current_plan.steps[0].tool_name if (current_plan.steps and hasattr(current_plan.steps[0], "tool_name")) else (current_plan.steps[0].tool if current_plan.steps else "statistical_tool"),
                actual_result_summary=obs_text[:200],
                observation_text=obs_text,
                critic_interpretation=critic_eval.reasoning,
                adaptive_decision=adaptive_decision.action.upper()
            )

            # Record Iteration Trace Log
            iteration_record = AdaptiveIteration(
                iteration=iter_idx,
                hypothesis=active_hypothesis,
                investigation_plan=current_plan,
                tool_executions=exec_result.executed_steps,
                observations=exec_result.observations,
                interpretation=interpretation,
                critic_evaluation=critic_eval,
                adaptive_decision=adaptive_decision,
                lineage=lineage
            )
            iterations_log.append(iteration_record)

            # 5. Evaluate Next Action & Stop Conditions
            if adaptive_decision.remaining_uncertainties:
                unresolved_questions = adaptive_decision.remaining_uncertainties

            if adaptive_decision.action == "stop":
                logger.info("Adaptive decision returned STOP on iteration %d: %s", iter_idx, adaptive_decision.reasoning)
                overall_status = "completed"
                break

            # If action == "continue", set next question for next loop
            next_q = adaptive_decision.next_question
            if iter_idx == max_iterations:
                overall_status = "max_iterations_reached"
                logger.info("Reached maximum iterations limit (%d).", max_iterations)

        return AdaptiveInvestigationResult(
            status=overall_status,
            iterations=iterations_log,
            final_evidence=list(set(all_evidence)),
            unresolved_questions=unresolved_questions,
            limitations=limitations
        )

    def _make_adaptive_decision(
        self,
        system_profile: SystemProfile,
        hypothesis: Hypothesis,
        investigation_plan: InvestigationPlan,
        executed_steps: list,
        observations: list,
        interpretation: Interpretation,
        iteration_count: int,
        all_evidence: list
    ) -> AdaptiveDecision:
        statuses_summary = [step.status for step in executed_steps]
        obs_summary = [obs.description for obs in observations]

        prompt = ADAPTIVE_DECISION_PROMPT_TEMPLATE.format(
            purpose=system_profile.purpose,
            ai_system_type=system_profile.ai_system_type,
            hypothesis_id=hypothesis.id,
            hypothesis_statement=hypothesis.hypothesis,
            investigation_goal=investigation_plan.investigation_goal,
            executed_statuses=json.dumps(statuses_summary),
            observations_summary=json.dumps(obs_summary),
            interpretation_summary=interpretation.interpretation,
            hypothesis_status=interpretation.hypothesis_status,
            iteration_count=iteration_count,
            all_evidence=json.dumps(all_evidence)
        )

        try:
            decision = self.llm.generate_structured(
                prompt=prompt,
                schema=AdaptiveDecision,
                system_prompt=ADAPTIVE_DECISION_SYSTEM_PROMPT
            )
            return decision
        except Exception as e:
            logger.error("Error generating adaptive decision: %s. Defaulting to stop.", str(e))
            return AdaptiveDecision(
                action="stop",
                reasoning=f"Adaptive decision fallback due to parsing error: {str(e)}",
                evidence_summary=interpretation.interpretation,
                remaining_uncertainties=interpretation.remaining_unknowns,
                next_question=None,
                confidence=0.5
            )
