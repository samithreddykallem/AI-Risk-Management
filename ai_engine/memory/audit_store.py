from typing import Dict, List, Optional
from ai_engine.models.system_profile import SystemProfile
from ai_engine.models.hypothesis import RiskHypothesis
from ai_engine.models.investigation import InvestigationPlan
from ai_engine.models.observation import Observation


class AuditStore:
    """In-memory audit store tracking evidence and artifacts across the evaluation pipeline."""

    def __init__(self):
        self.profile: Optional[SystemProfile] = None
        self.hypotheses: Dict[str, RiskHypothesis] = {}
        self.plans: Dict[str, InvestigationPlan] = {}
        self.observations: Dict[str, List[Observation]] = {}

    def set_profile(self, profile: SystemProfile) -> None:
        self.profile = profile

    def add_hypothesis(self, hypothesis: RiskHypothesis) -> None:
        self.hypotheses[hypothesis.hypothesis_id] = hypothesis

    def add_plan(self, plan: InvestigationPlan) -> None:
        self.plans[plan.plan_id] = plan

    def add_observation(self, observation: Observation) -> None:
        hyp_id = observation.hypothesis_id
        if hyp_id not in self.observations:
            self.observations[hyp_id] = []
        self.observations[hyp_id].append(observation)

    def get_all_hypotheses(self) -> List[RiskHypothesis]:
        return list(self.hypotheses.values())
