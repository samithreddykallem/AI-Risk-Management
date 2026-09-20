import uuid
from ai_engine.agents.base_agent import BaseAgent
from ai_engine.models.investigation import InvestigationPlan
from ai_engine.models.observation import Observation, EvidenceItem
from ai_engine.probes.simulated_target import SimulatedTargetAI
from ai_engine.probes.behavioral_probe import BehavioralProbe


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing investigation probes against target AI systems and collecting observations."""

    def execute_investigation(self, plan: InvestigationPlan, target: SimulatedTargetAI) -> Observation:
        """Execute all probes specified in an InvestigationPlan and assemble structured Observation."""
        probe_runner = BehavioralProbe()
        evidence_items = []
        anomalies_count = 0

        for probe_spec in plan.probes:
            evidence = probe_runner.run_probe(probe_spec, target)
            evidence_items.append(evidence)
            if evidence.is_anomaly:
                anomalies_count += 1

        summary = (
            f"Executed {len(plan.probes)} probes for hypothesis {plan.hypothesis_id}. "
            f"Detected {anomalies_count} anomaly evidence items."
        )

        return Observation(
            observation_id=f"OBS-{uuid.uuid4().hex[:6]}",
            plan_id=plan.plan_id,
            hypothesis_id=plan.hypothesis_id,
            evidence_items=evidence_items,
            total_probes_run=len(plan.probes),
            anomalies_detected_count=anomalies_count,
            summary_findings=summary
        )
