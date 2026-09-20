import uuid
import logging
from typing import Optional, List, Any, Tuple

from app.schemas.system_profile import SystemProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.investigation import (
    InvestigationPlan,
    InvestigationStep,
    ToolExecution,
    Observation,
    InvestigationResult
)
from app.tools.registry import ToolRegistry, default_tool_registry

logger = logging.getLogger("ai_engine.services.investigation_executor")


class InvestigationExecutor:
    """
    Decoupled service executing an InvestigationPlan step-by-step using registered safe tools.
    Logs ToolExecution entries, source-tracked Observations, and Evidence trails.
    If a tool is unavailable or unknown, explicitly records status='unavailable' without inventing facts.
    """

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or default_tool_registry

    def execute_plan(
        self,
        system_profile: SystemProfile,
        hypothesis: Hypothesis,
        investigation_plan: InvestigationPlan,
        available_tools: Optional[List[Any]] = None,
        initial_evidence: Optional[List[str]] = None
    ) -> InvestigationResult:
        logger.info("Starting investigation execution for hypothesis '%s'...", hypothesis.id)

        executed_steps: List[ToolExecution] = []
        observations: List[Observation] = []
        evidence_trail: List[str] = list(initial_evidence or [])
        limitations: List[str] = []

        success_count = 0
        unavailable_count = 0
        failed_count = 0

        for step in investigation_plan.steps:
            tool_name = step.tool.lower() if step.tool else ""
            tool_instance = self.registry.get_tool(tool_name)

            if not tool_instance:
                # Tool is unknown or not registered
                logger.warning("Step '%s': Tool '%s' is not registered in ToolRegistry.", step.step_id, step.tool)
                execution = ToolExecution(
                    execution_id=f"EXEC-{uuid.uuid4().hex[:6]}",
                    step_id=step.step_id,
                    tool=step.tool,
                    parameters=step.parameters,
                    timestamp=step.step_id,
                    status="unavailable",
                    result=None,
                    evidence=[],
                    error=f"Tool '{step.tool}' is not registered or unavailable in the ToolRegistry."
                )
                executed_steps.append(execution)
                unavailable_count += 1
                limitations.append(f"Step '{step.step_id}': Tool '{step.tool}' was unavailable.")
                continue

            # Inject dataset & hypothesis context into tool parameters
            params = dict(step.parameters or {})
            if hasattr(system_profile, "dataset_path") and system_profile.dataset_path:
                params.setdefault("dataset_path", system_profile.dataset_path)
            if hasattr(system_profile, "target_candidate") and system_profile.target_candidate:
                params.setdefault("target_column", system_profile.target_candidate)
            if hasattr(system_profile, "sensitive_candidates") and system_profile.sensitive_candidates:
                sens_cols = [s.column_name for s in system_profile.sensitive_candidates]
                if sens_cols:
                    params.setdefault("sensitive_column", sens_cols[0])
            params.setdefault("control_column", "income")

            # Execute registered safe tool
            try:
                execution = tool_instance.run(step_id=step.step_id, parameters=params)
                executed_steps.append(execution)

                if execution.status == "success":
                    success_count += 1
                    evidence_trail.extend(execution.evidence)
                    
                    # Create source-tracked observation for successful step
                    obs = Observation(
                        observation_id=f"OBS-{uuid.uuid4().hex[:6]}",
                        step_id=step.step_id,
                        description=f"Executed {step.tool}: {step.objective}. Result: {execution.result}",
                        source=tool_name,
                        evidence=execution.evidence,
                        significance=step.reasoning
                    )
                    observations.append(obs)

                elif execution.status == "unavailable":
                    unavailable_count += 1
                    limitations.append(f"Step '{step.step_id}': Tool '{step.tool}' reported execution unavailable ({execution.error}).")

                else:
                    failed_count += 1
                    limitations.append(f"Step '{step.step_id}': Tool '{step.tool}' failed ({execution.error}).")

            except Exception as e:
                logger.error("Exception executing step '%s' with tool '%s': %s", step.step_id, step.tool, str(e))
                execution = ToolExecution(
                    execution_id=f"EXEC-{uuid.uuid4().hex[:6]}",
                    step_id=step.step_id,
                    tool=step.tool,
                    parameters=step.parameters,
                    timestamp=step.step_id,
                    status="failed",
                    result=None,
                    evidence=[],
                    error=f"Execution error: {str(e)}"
                )
                executed_steps.append(execution)
                failed_count += 1
                limitations.append(f"Step '{step.step_id}' failed due to exception: {str(e)}")

        # Determine overall result status
        total_steps = len(investigation_plan.steps)
        if success_count == total_steps and total_steps > 0:
            overall_status = "completed"
        elif success_count > 0:
            overall_status = "partially_completed"
        elif unavailable_count > 0 and success_count == 0:
            overall_status = "insufficient_capability"
        else:
            overall_status = "failed"

        return InvestigationResult(
            hypothesis_id=hypothesis.id,
            investigation_goal=investigation_plan.investigation_goal,
            status=overall_status,
            executed_steps=executed_steps,
            observations=observations,
            evidence=evidence_trail,
            limitations=limitations
        )
