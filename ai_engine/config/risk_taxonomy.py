from enum import Enum
from typing import Dict, List


class RiskDimension(str, Enum):
    """Core ethical, safety, and risk dimensions for AI auditing."""
    ETHICS = "Ethics"
    SAFETY = "Safety"
    PRIVACY = "Privacy"
    FAIRNESS = "Fairness"
    SECURITY = "Security"
    RELIABILITY = "Reliability"
    TRANSPARENCY = "Transparency"
    HUMAN_OVERSIGHT = "Human Oversight"


RISK_DIMENSION_DESCRIPTIONS: Dict[RiskDimension, str] = {
    RiskDimension.ETHICS: "Moral alignment, societal impact, prevention of psychological or systemic harm.",
    RiskDimension.SAFETY: "Prevention of physical harm, dangerous content generation, or uncontrollable autonomous actions.",
    RiskDimension.PRIVACY: "Data protection, PII leakages, unauthorized profiling, surveillance, and memory extraction.",
    RiskDimension.FAIRNESS: "Prevention of demographic bias, discriminatory outcomes, disparate impact, and stereotyping.",
    RiskDimension.SECURITY: "Resilience against prompt injection, adversarial manipulation, model theft, and data poisoning.",
    RiskDimension.RELIABILITY: "Hallucination rates, edge-case failure, consistency, failure mode handling, and robustness.",
    RiskDimension.TRANSPARENCY: "Explainability of decisions, clear disclosure of AI identity, provenance, and auditability.",
    RiskDimension.HUMAN_OVERSIGHT: "Presence of human-in-the-loop fallback, override mechanisms, autonomy boundaries, and contestability.",
}


def get_all_dimensions() -> List[str]:
    return [dim.value for dim in RiskDimension]
