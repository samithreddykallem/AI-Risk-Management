from abc import ABC, abstractmethod
from ai_engine.models.investigation import ProbeSpec
from ai_engine.models.observation import EvidenceItem
from ai_engine.probes.simulated_target import SimulatedTargetAI


class BaseProbe(ABC):
    """Abstract base class for all investigation probes."""

    @abstractmethod
    def run_probe(self, probe_spec: ProbeSpec, target: SimulatedTargetAI) -> EvidenceItem:
        """Execute probe against target and return evaluated EvidenceItem."""
        pass
