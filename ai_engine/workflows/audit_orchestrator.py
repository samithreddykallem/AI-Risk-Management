import uuid
from datetime import datetime
from typing import List, Optional

from ai_engine.models.system_input import SystemInput
from ai_engine.models.system_profile import SystemProfile
from ai_engine.models.hypothesis import RiskHypothesis, HypothesisStatus, RiskSeverity
from ai_engine.models.report import AuditReport, VerifiedRiskFinding
from ai_engine.config.settings import settings

from ai_engine.agents.profiler_agent import ProfilerAgent
from ai_engine.agents.hypothesis_agent import HypothesisAgent
from ai_engine.agents.planner_agent import PlannerAgent
from ai_engine.agents.executor_agent import ExecutorAgent
from ai_engine.agents.evaluator_agent import EvaluatorAgent

from ai_engine.probes.simulated_target import SimulatedTargetAI
from ai_engine.memory.audit_store import AuditStore
from ai_engine.memory.state_manager import AuditStateTracker, AuditPhase


class AuditOrchestrator:
    """
    Main engine orchestrator implementing the adaptive audit loop:
    Input AI System -> Profile -> Hypotheses -> Investigation Plan -> Probes -> Observations -> Reasoning -> Loop/Conclude -> Audit Report
    """

    def __init__(self, llm_provider=None):
        self.profiler = ProfilerAgent(llm_provider)
        self.hypothesis_agent = HypothesisAgent(llm_provider)
        self.planner = PlannerAgent(llm_provider)
        self.executor = ExecutorAgent(llm_provider)
        self.evaluator = EvaluatorAgent(llm_provider)

        self.store = AuditStore()
        self.state_tracker = AuditStateTracker()

    def run_audit(self, system_input: SystemInput) -> AuditReport:
        """Run full adaptive risk audit on a target AI system input."""
        audit_id = f"AUDIT-{uuid.uuid4().hex[:8].upper()}"
        
        # 1. Understand System & Build System Profile
        self.state_tracker.transition_to(AuditPhase.PROFILING, f"Analyzing system specs for '{system_input.system_name}'")
        profile: SystemProfile = self.profiler.build_profile(system_input)
        self.store.set_profile(profile)

        # 2. Generate System-Specific Hypotheses
        self.state_tracker.transition_to(AuditPhase.HYPOTHESIS_GENERATION, "Generating targeted risk hypotheses")
        hypotheses: List[RiskHypothesis] = self.hypothesis_agent.generate_hypotheses(profile)
        for hyp in hypotheses[:settings.max_hypotheses_per_run]:
            self.store.add_hypothesis(hyp)

        # Target AI simulator setup
        target = SimulatedTargetAI(system_input)

        # 3. Iterative Investigation Loop per Hypothesis
        for hyp in self.store.get_all_hypotheses():
            while hyp.status in [HypothesisStatus.UNTESTED, HypothesisStatus.IN_PROGRESS]:
                # Design Investigation
                self.state_tracker.transition_to(
                    AuditPhase.INVESTIGATION_PLANNING,
                    f"Designing probes for hypothesis {hyp.hypothesis_id} (Step {hyp.iteration_depth + 1})"
                )
                plan = self.planner.create_investigation_plan(hyp)
                self.store.add_plan(plan)

                # Execute Investigations & Observe Results
                self.state_tracker.transition_to(
                    AuditPhase.INVESTIGATION_EXECUTION,
                    f"Executing probes for plan {plan.plan_id}"
                )
                observation = self.executor.execute_investigation(plan, target)
                self.store.add_observation(observation)

                # Reason About Results & Decide What To Investigate Next
                self.state_tracker.transition_to(
                    AuditPhase.EVALUATION_REASONING,
                    f"Reasoning over observation {observation.observation_id} for hypothesis {hyp.hypothesis_id}"
                )
                hyp, needs_more = self.evaluator.evaluate_observation(hyp, observation)

                if not needs_more:
                    break

        # 4. Synthesize Audit Findings & Produce Report
        self.state_tracker.transition_to(AuditPhase.REPORT_SYNTHESIS, "Synthesizing final audit report")
        report = self._synthesize_report(audit_id, system_input, profile)
        self.state_tracker.transition_to(AuditPhase.COMPLETED, f"Audit {audit_id} successfully completed")

        return report

    def _synthesize_report(
        self, audit_id: str, system_input: SystemInput, profile: SystemProfile
    ) -> AuditReport:
        verified_findings: List[VerifiedRiskFinding] = []
        refuted_titles: List[str] = []
        inconclusive_titles: List[str] = []
        highest_severity = RiskSeverity.LOW

        for hyp in self.store.get_all_hypotheses():
            if hyp.status == HypothesisStatus.CONFIRMED:
                obs_list = self.store.observations.get(hyp.hypothesis_id, [])
                latest_obs_summary = obs_list[-1].summary_findings if obs_list else "Anomalies observed during probes."
                
                finding = VerifiedRiskFinding(
                    finding_id=f"FIND-{uuid.uuid4().hex[:6].upper()}",
                    risk_dimension=hyp.risk_dimension,
                    title=hyp.title,
                    severity=hyp.severity,
                    hypothesis_statement=hyp.statement,
                    evidence_summary=latest_obs_summary,
                    impact_analysis=hyp.potential_impact,
                    recommended_mitigation=f"Implement input sanitization, bias mitigations, and human override safeguards for {hyp.risk_dimension.value}.",
                    confidence_score=0.88
                )
                verified_findings.append(finding)

                if hyp.severity == RiskSeverity.CRITICAL:
                    highest_severity = RiskSeverity.CRITICAL
                elif hyp.severity == RiskSeverity.HIGH and highest_severity != RiskSeverity.CRITICAL:
                    highest_severity = RiskSeverity.HIGH
                elif hyp.severity == RiskSeverity.MEDIUM and highest_severity not in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]:
                    highest_severity = RiskSeverity.MEDIUM

            elif hyp.status == HypothesisStatus.REFUTED:
                refuted_titles.append(hyp.title)
            else:
                inconclusive_titles.append(hyp.title)

        exec_summary = (
            f"Audit completed for AI System '{system_input.system_name}' ({profile.primary_domain}). "
            f"Evaluated {len(self.store.get_all_hypotheses())} system-specific risk hypotheses across ethical, safety, privacy, fairness, and security dimensions. "
            f"Identified {len(verified_findings)} confirmed risk findings. Overall Risk Assessment: {highest_severity.value}."
        )

        recommendations = [
            f"Remediate identified {finding.severity.value} finding: '{finding.title}'"
            for finding in verified_findings
        ]
        if not recommendations:
            recommendations.append("Continue periodic adaptive re-auditing as model or data updates occur.")

        return AuditReport(
            audit_id=audit_id,
            system_name=system_input.system_name,
            audit_timestamp=datetime.now().isoformat(),
            system_summary=profile.profile_summary,
            total_hypotheses_evaluated=len(self.store.get_all_hypotheses()),
            verified_findings=verified_findings,
            refuted_hypotheses=refuted_titles,
            inconclusive_hypotheses=inconclusive_titles,
            overall_risk_rating=highest_severity,
            executive_summary=exec_summary,
            actionable_recommendations=recommendations
        )
