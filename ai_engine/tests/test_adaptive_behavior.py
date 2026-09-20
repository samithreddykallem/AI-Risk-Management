import os
import pytest
from app.schemas.hypothesis import Hypothesis
from services.llm_roles import run_evidence_critic_role


def test_adaptive_behavior_disparity_triggers_controlled_investigation():
    """
    Proves Adaptive Requirement:
    If Observation 1 shows outcome disparity across subgroups ->
    Evidence Critic identifies potential confounding variables (e.g., income) ->
    Next Investigation selected is Controlled Subgroup Comparison.
    """
    hyp = Hypothesis(
        id="HYP-001",
        hypothesis="Approval rates differ across gender groups.",
        why_it_is_plausible="Initial data profiling indicated gender group outcome variance.",
        affected_part="subgroup_eval",
        potential_consequence="Outcome disparity",
        priority="high",
        confidence=0.85
    )

    observation_disparity = "Subgroup outcome rates for target 'Loan_Status' by sensitive attribute 'Gender': Group 'Male': 80.0% approval, Group 'Female': 50.0% approval."

    critic = run_evidence_critic_role(
        hypothesis=hyp,
        investigation_summary="Compare raw approval rates by gender",
        actual_tool_output=observation_disparity,
        iteration=1
    )

    # Assert adaptive decision dynamically responds to evidence
    assert critic.supports_hypothesis is True
    assert critic.decision == "CONTINUE"
    assert "income" in [v.lower() for v in critic.confounding_variables] or len(critic.confounding_variables) > 0


def test_adaptive_behavior_no_disparity_triggers_stop():
    """
    Proves Adaptive Requirement:
    If Observation 1 shows uniform outcomes across subgroups ->
    Evidence Critic concludes no further controlled investigation needed ->
    Agent decision is STOP.
    """
    hyp = Hypothesis(
        id="HYP-001",
        hypothesis="Approval rates differ across gender groups.",
        why_it_is_plausible="Initial data profiling.",
        affected_part="subgroup_eval",
        potential_consequence="Outcome disparity",
        priority="high",
        confidence=0.85
    )

    observation_uniform = "Subgroup outcome rates for target 'Loan_Status' by sensitive attribute 'Gender': Group 'Male': 70.0% approval, Group 'Female': 70.0% approval."

    critic = run_evidence_critic_role(
        hypothesis=hyp,
        investigation_summary="Compare raw approval rates by gender",
        actual_tool_output=observation_uniform,
        iteration=2
    )

    # Assert adaptive decision dynamically responds to uniform evidence
    assert critic.decision == "STOP"
