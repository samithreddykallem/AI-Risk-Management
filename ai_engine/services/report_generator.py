import logging
from typing import List, Optional, Any
from app.schemas.project import ProjectInput
from app.schemas.system_profile import SystemProfile
from app.schemas.dataset import DatasetProfile
from app.schemas.hypothesis import Hypothesis
from app.schemas.adaptive import AdaptiveIteration

logger = logging.getLogger("ai_engine.report_generator")


def generate_human_readable_report(
    project: ProjectInput,
    system_profile: SystemProfile,
    dataset_profile: Optional[DatasetProfile],
    hypotheses: List[Hypothesis],
    iterations: List[AdaptiveIteration],
    final_evidence: List[str],
    unresolved_questions: List[str],
    limitations: List[str]
) -> str:
    """
    Generates a human-readable AI Audit Report in Markdown format.
    Does NOT expose internal tool dicts, python code, or raw variable names.
    """
    lines = []
    lines.append("# AI Audit Report")
    lines.append(f"**Project Name**: {project.project_name}")
    if dataset_profile:
        lines.append(f"**Dataset Audited**: `{dataset_profile.file_name}` ({dataset_profile.row_count} records, {dataset_profile.column_count} attributes)")
        lines.append(f"**Audit Mode**: `{dataset_profile.audit_mode.value}`")
    lines.append("")

    # 1. System Overview
    lines.append("## What this AI system does")
    lines.append(system_profile.profile_summary or project.description)
    lines.append(f"- **Primary Domain**: {system_profile.primary_domain}")
    lines.append(f"- **System Type**: {system_profile.system_type}")
    lines.append(f"- **Intended Purpose**: {system_profile.intended_purpose}")
    lines.append("")

    # 2. Dataset Discoveries
    lines.append("## What the auditor discovered")
    if dataset_profile:
        sens_str = ", ".join([f"**{s.column_name}** ({s.category})" for s in dataset_profile.sensitive_candidates]) or "None explicitly flagged"
        proxy_str = ", ".join([f"**{p.proxy_column}** (associated with {p.sensitive_column}, score = {p.strength_score})" for p in dataset_profile.proxy_candidates]) or "None"
        
        lines.append(f"- **Target Attribute**: `{dataset_profile.target_candidate or 'Unspecified'}`")
        lines.append(f"- **Potentially Sensitive Attributes**: {sens_str}")
        lines.append(f"- **Proxy Feature Candidates**: {proxy_str}")
        lines.append(f"- **Class Distribution**: `{dataset_profile.class_distribution}`")
        if dataset_profile.missing_value_summary:
            lines.append(f"- **Missing Value Summary**: `{dataset_profile.missing_value_summary}`")
    else:
        lines.append("Auditor performed analysis based on project evidence and specifications.")
    lines.append("")

    # 3. Hypotheses & Investigations
    for idx, hyp in enumerate(hypotheses, 1):
        lines.append(f"## Risk Hypothesis {idx}: {hyp.id}")
        lines.append(f"### Investigation Question")
        lines.append(f"> \"{hyp.hypothesis}\"")
        lines.append("")
        lines.append("### Why this question was selected")
        lines.append(hyp.why_it_is_plausible)
        lines.append(f"- **Status**: `{hyp.status}`")
        lines.append(f"- **Confidence**: `{int(hyp.confidence * 100)}%`")
        lines.append("")

    # Iteration trace steps
    for iter_step in iterations:
        lines.append(f"## Investigation {iter_step.iteration}")
        lines.append(f"**Goal**: {iter_step.investigation_plan.investigation_goal}")
        lines.append(f"**Reasoning**: {getattr(iter_step.investigation_plan, 'why_this_investigation', getattr(iter_step.investigation_plan, 'reasoning', iter_step.investigation_plan.investigation_goal))}")
        lines.append("")

        lines.append("### What was observed")
        for obs in iter_step.observations:
            lines.append(f"- {getattr(obs, 'description', str(obs))}")
        lines.append("")

        if iter_step.critic_evaluation:
            lines.append("### What the evidence means (Independent Critic Evaluation)")
            c_eval = iter_step.critic_evaluation
            sup_text = "Supports hypothesis" if c_eval.supports_hypothesis else "Does not support hypothesis"
            lines.append(f"- **Evidence Verdict**: `{sup_text}`")
            lines.append(f"- **Critic Rationale**: {c_eval.reasoning}")
            if c_eval.confounding_variables:
                lines.append(f"- **Potential Confounding Variables**: {', '.join(c_eval.confounding_variables)}")
            lines.append("")

        lines.append("### Why the auditor continued / stopped")
        lines.append(f"- **Action**: `{iter_step.adaptive_decision.action.upper()}`")
        lines.append(f"- **Adaptive Decision Rationale**: {iter_step.adaptive_decision.reasoning}")
        if iter_step.adaptive_decision.next_question:
            lines.append(f"- **Next Investigation Target**: \"{iter_step.adaptive_decision.next_question}\"")
        lines.append("")

    # 4. Final Evidence Summary
    lines.append("## Final Evidence Summary")
    if final_evidence:
        for ev in final_evidence:
            lines.append(f"- {ev}")
    else:
        lines.append("- No adverse evidence observed.")
    lines.append("")

    # 5. Remaining Uncertainties
    lines.append("## What remains uncertain")
    if unresolved_questions:
        for uq in unresolved_questions:
            lines.append(f"- {uq}")
    else:
        lines.append("- No major unresolved questions remaining.")
    lines.append("")

    # 6. Limitations
    lines.append("## Audit Limitations")
    if limitations:
        for lim in limitations:
            lines.append(f"- {lim}")
    else:
        lines.append("- Audit conducted under normal parameter boundaries.")
    lines.append("")

    return "\n".join(lines)
