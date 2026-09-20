from typing import Tuple
from ai_engine.agents.base_agent import BaseAgent
from ai_engine.models.hypothesis import RiskHypothesis, HypothesisStatus
from ai_engine.models.observation import Observation
from ai_engine.config.settings import settings


class EvaluatorAgent(BaseAgent):
    """Agent responsible for reasoning over observation evidence, updating hypothesis status, and determining next audit steps."""

    def evaluate_observation(
        self, hypothesis: RiskHypothesis, observation: Observation
    ) -> Tuple[RiskHypothesis, bool]:
        """
        Evaluates evidence in observation against the target hypothesis.
        Returns updated hypothesis and a boolean (needs_more_investigation).
        """
        # Calculate maximum evidence confidence from detected anomalies
        max_confidence = max([e.confidence_score for e in observation.evidence_items], default=0.0)

        # Decision logic:
        if observation.anomalies_detected_count > 0 and max_confidence >= settings.confidence_threshold:
            hypothesis.status = HypothesisStatus.CONFIRMED
            hypothesis.follow_up_notes = (
                f"CONFIRMED on iteration depth {hypothesis.iteration_depth}. "
                f"Anomalies detected: {observation.anomalies_detected_count}. Confidence: {max_confidence:.2f}"
            )
            needs_more_investigation = False

        elif observation.anomalies_detected_count == 0 and hypothesis.iteration_depth >= 1:
            hypothesis.status = HypothesisStatus.REFUTED
            hypothesis.follow_up_notes = f"REFUTED on iteration depth {hypothesis.iteration_depth}. No anomalies detected across executed probes."
            needs_more_investigation = False

        else:
            # Inconclusive or borderline confidence -> Check depth limit
            if hypothesis.iteration_depth < settings.max_investigation_depth:
                hypothesis.status = HypothesisStatus.IN_PROGRESS
                hypothesis.iteration_depth += 1
                hypothesis.follow_up_notes = (
                    f"INCONCLUSIVE on step {hypothesis.iteration_depth - 1}. "
                    f"Evidence confidence ({max_confidence:.2f}) below threshold ({settings.confidence_threshold}). Planning deeper probes."
                )
                needs_more_investigation = True
            else:
                hypothesis.status = HypothesisStatus.INCONCLUSIVE
                hypothesis.follow_up_notes = f"Max investigation depth ({settings.max_investigation_depth}) reached without definitive threshold convergence."
                needs_more_investigation = False

        return hypothesis, needs_more_investigation
