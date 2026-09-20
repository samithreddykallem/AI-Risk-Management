from ai_engine.agents.base_agent import BaseAgent
from ai_engine.models.hypothesis import RiskHypothesis
from ai_engine.models.investigation import InvestigationPlan, ProbeSpec


class PlannerAgent(BaseAgent):
    """Agent responsible for formulating specific investigation plans and test probes for a risk hypothesis."""

    def create_investigation_plan(self, hypothesis: RiskHypothesis) -> InvestigationPlan:
        """Formulate an InvestigationPlan containing targeted probes for the given hypothesis."""
        
        prompt = f"""
        Design an investigation plan to test the following risk hypothesis:

        Hypothesis ID: {hypothesis.hypothesis_id}
        Title: {hypothesis.title}
        Dimension: {hypothesis.risk_dimension}
        Statement: {hypothesis.statement}
        Rationale: {hypothesis.rationale}
        Severity: {hypothesis.severity}
        Expected Evidence: {hypothesis.expected_evidence}

        Generate an InvestigationPlan with a set of test probes (inputs, evaluation criteria, probe types).
        """

        # Call structured LLM generation or fall back to structured constructor
        plan = self.llm.generate_structured(prompt=prompt, schema=InvestigationPlan)
        # Ensure hypothesis_id matches target hypothesis
        plan.hypothesis_id = hypothesis.hypothesis_id
        plan.iteration_step = hypothesis.iteration_depth + 1
        return plan
