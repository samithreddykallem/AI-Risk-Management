from enum import Enum
from typing import List, Dict, Any


class AuditPhase(str, Enum):
    INIT = "INIT"
    PROFILING = "PROFILING"
    HYPOTHESIS_GENERATION = "HYPOTHESIS_GENERATION"
    INVESTIGATION_PLANNING = "INVESTIGATION_PLANNING"
    INVESTIGATION_EXECUTION = "INVESTIGATION_EXECUTION"
    EVALUATION_REASONING = "EVALUATION_REASONING"
    REPORT_SYNTHESIS = "REPORT_SYNTHESIS"
    COMPLETED = "COMPLETED"


class AuditStateTracker:
    """Manages audit phase transitions and state history audit logs."""

    def __init__(self):
        self.current_phase: AuditPhase = AuditPhase.INIT
        self.history: List[Dict[str, Any]] = []

    def transition_to(self, phase: AuditPhase, message: str = "") -> None:
        self.current_phase = phase
        log_entry = {"phase": phase.value, "message": message}
        self.history.append(log_entry)

    def get_summary_log(self) -> List[str]:
        return [f"[{entry['phase']}] {entry['message']}" for entry in self.history]
