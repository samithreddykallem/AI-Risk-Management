from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """An individual piece of empirical evidence extracted from probe execution."""
    evidence_id: str
    probe_id: str
    input_sent: str
    output_received: str
    is_anomaly: bool = Field(..., description="True if output violates evaluation criteria or shows risk behavior")
    anomaly_description: Optional[str] = Field(default=None, description="Description of detected anomaly")
    confidence_score: float = Field(default=0.0, description="Confidence in anomaly detection (0.0 to 1.0)")


class Observation(BaseModel):
    """Structured results collected by ExecutorAgent after running an InvestigationPlan."""
    observation_id: str
    plan_id: str
    hypothesis_id: str
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    total_probes_run: int
    anomalies_detected_count: int
    summary_findings: str = Field(..., description="High-level narrative of observation results")
    raw_logs: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
