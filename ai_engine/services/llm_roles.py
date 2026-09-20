import os
import logging
from typing import List, Dict, Any, Optional
import json

from app.schemas.project import ProjectInput
from app.schemas.system_profile import SystemProfile
from app.schemas.dataset import DatasetProfile
from app.schemas.hypothesis import Hypothesis, HypothesisGenerationResponse
from app.schemas.investigation import InvestigationPlan
from app.schemas.adaptive import CriticEvaluation
from llm.provider_factory import get_llm_provider

logger = logging.getLogger("ai_engine.llm_roles")


def get_role_llm(is_critic: bool = False):
    """
    Retrieves configured LLM provider instance for primary reasoning or critic role.
    Supports environment variables PRIMARY_REASONING_MODEL and CRITIC_MODEL.
    """
    model_env = "CRITIC_MODEL" if is_critic else "PRIMARY_REASONING_MODEL"
    override_model = os.getenv(model_env)
    return get_llm_provider(model_name=override_model)


# --- ROLE 1: SYSTEM ANALYST ---
def run_system_analyst_role(project: ProjectInput, dataset_profile: Optional[DatasetProfile] = None) -> SystemProfile:
    """ROLE 1 — SYSTEM ANALYST: Builds a grounded System Profile from project info & dataset profile."""
    llm = get_role_llm(is_critic=False)
    
    ds_context = ""
    if dataset_profile:
        ds_context = (
            f"\nDataset Context:\n"
            f"- File: {dataset_profile.file_name} ({dataset_profile.row_count} rows, {dataset_profile.column_count} cols)\n"
            f"- Audit Mode: {dataset_profile.audit_mode.value}\n"
            f"- Target Candidate: {dataset_profile.target_candidate}\n"
            f"- Sensitive Attributes: {[s.column_name for s in dataset_profile.sensitive_candidates]}\n"
            f"- Proxy Candidates: {[p.proxy_column for p in dataset_profile.proxy_candidates]}\n"
        )

    prompt = (
        f"You are the SYSTEM ANALYST role in an adaptive AI audit system.\n"
        f"Analyze the following AI project specification and build a grounded System Profile.\n\n"
        f"Project Name: {project.project_name}\n"
        f"Description: {project.description}\n"
        f"GitHub URL: {project.github_url or 'None'}\n"
        f"Documentation: {project.documentation or 'None'}\n"
        f"{ds_context}\n"
        f"Instructions:\n"
        f"1. Identify system name, primary domain, system type, purpose, target audience.\n"
        f"2. Identify input attributes, target outputs, and operational context.\n"
        f"3. Mark any missing or unstated details as 'unknown'. Do NOT invent details.\n"
    )

    try:
        profile = llm.generate_structured(prompt=prompt, schema=SystemProfile)
        return profile
    except Exception as e:
        logger.warning(f"System Analyst LLM generation failed ({e}). Falling back to rule-based profile.")
        return SystemProfile(
            system_name=project.project_name,
            primary_domain="general_ai",
            system_type="classification_model",
            intended_purpose=project.description[:200],
            target_audience="end_users",
            input_attributes=[col.name for col in dataset_profile.columns] if dataset_profile else ["unknown"],
            target_outputs=[dataset_profile.target_candidate] if dataset_profile and dataset_profile.target_candidate else ["unknown"],
            operational_context="production_evaluation",
            important_unstated_information=["Model architecture", "Training hyperparameters"],
            profile_summary=f"System profile built for {project.project_name}."
        )


# --- ROLE 3: HYPOTHESIS GENERATOR ---
def run_hypothesis_generator_role(
    system_profile: SystemProfile,
    dataset_profile: Optional[DatasetProfile] = None
) -> List[Hypothesis]:
    """ROLE 3 — HYPOTHESIS GENERATOR: Generates dataset-grounded, system-specific risk hypotheses."""
    llm = get_role_llm(is_critic=False)

    ds_discoveries = ""
    if dataset_profile:
        sens_str = ", ".join([f"{s.column_name} ({s.category})" for s in dataset_profile.sensitive_candidates]) or "None"
        proxy_str = ", ".join([f"{p.proxy_column} (proxy for {p.sensitive_column}, score={p.strength_score})" for p in dataset_profile.proxy_candidates]) or "None"
        class_str = str(dataset_profile.class_distribution) or "Unknown"

        ds_discoveries = (
            f"\nDataset Discoveries:\n"
            f"- Row Count: {dataset_profile.row_count}, Col Count: {dataset_profile.column_count}\n"
            f"- Target Column: {dataset_profile.target_candidate} (Class Dist: {class_str})\n"
            f"- Sensitive Attributes Identified: {sens_str}\n"
            f"- Proxy Candidates Identified: {proxy_str}\n"
            f"- Missingness Summary: {dataset_profile.missing_value_summary}\n"
        )

    prompt = (
        f"You are the HYPOTHESIS GENERATOR role in an adaptive AI audit system.\n"
        f"Generate 1 to 3 specific, dataset-grounded risk hypotheses for this AI system.\n\n"
        f"System Profile: {system_profile.profile_summary}\n"
        f"Domain: {system_profile.primary_domain}\n"
        f"{ds_discoveries}\n"
        f"Rules:\n"
        f"- Ground hypotheses strictly in dataset discoveries and system description.\n"
        f"- Do NOT use fixed generic checklists.\n"
        f"- If sensitive attributes or proxies exist, hypothesize potential outcome disparities or proxy pathways.\n"
    )

    try:
        resp = llm.generate_structured(prompt=prompt, schema=HypothesisGenerationResponse)
        return resp.hypotheses
    except Exception as e:
        logger.warning(f"Hypothesis Generator LLM failed ({e}). Falling back to rule-based dataset hypotheses.")
        fallback_hypotheses = []
        if dataset_profile and dataset_profile.sensitive_candidates:
            sens_col = dataset_profile.sensitive_candidates[0].column_name
            target_col = dataset_profile.target_candidate or "outcome"
            fallback_hypotheses.append(
                Hypothesis(
                    id="HYP-001",
                    hypothesis=f"Target outcome '{target_col}' may differ significantly across subgroups of sensitive attribute '{sens_col}'.",
                    why_it_is_plausible=f"Dataset profiling identified '{sens_col}' as a sensitive attribute with potential representation or outcome imbalance.",
                    supporting_evidence=[f"Sensitive attribute candidate: {sens_col}"],
                    affected_part="subgroup_evaluation",
                    potential_consequence="Unintended outcome disparity across demographic subgroups.",
                    what_evidence_would_support_it=[f"Statistically significant difference in positive outcome rates across '{sens_col}' groups."],
                    what_evidence_would_refute_it=[f"Equal outcome rates across '{sens_col}' groups."],
                    priority="high",
                    confidence=0.85,
                    status="OPEN"
                )
            )
            if dataset_profile.proxy_candidates:
                proxy = dataset_profile.proxy_candidates[0]
                fallback_hypotheses.append(
                    Hypothesis(
                        id="HYP-002",
                        hypothesis=f"Feature '{proxy.proxy_column}' may act as a proxy pathway for sensitive attribute '{proxy.sensitive_column}'.",
                        why_it_is_plausible=f"Feature '{proxy.proxy_column}' has a strong statistical association ({proxy.strength_score}) with '{proxy.sensitive_column}'.",
                        supporting_evidence=[f"Statistical proxy association score: {proxy.strength_score}"],
                        affected_part="feature_processing",
                        potential_consequence="Proxy-based indirect outcome disparity.",
                        what_evidence_would_support_it=[f"Outcome disparity persisting through '{proxy.proxy_column}' feature values."],
                        what_evidence_would_refute_it=[f"No correlation between '{proxy.proxy_column}' and outcome."],
                        priority="medium",
                        confidence=0.75,
                        status="OPEN"
                    )
                )
        else:
            fallback_hypotheses.append(
                Hypothesis(
                    id="HYP-001",
                    hypothesis="System performance or outcome distribution may exhibit imbalance across dataset categories.",
                    why_it_is_plausible="Dataset profiling indicates potential class or feature distribution imbalance.",
                    supporting_evidence=["Dataset class distribution"],
                    affected_part="model_evaluation",
                    potential_consequence="Unbalanced model decision performance.",
                    what_evidence_would_support_it=["Observed variance in subgroup error rates."],
                    what_evidence_would_refute_it=["Uniform error rate across groups."],
                    priority="medium",
                    confidence=0.70,
                    status="OPEN"
                )
            )
        return fallback_hypotheses


# --- ROLE 6: EVIDENCE CRITIC ---
def run_evidence_critic_role(
    hypothesis: Hypothesis,
    investigation_summary: str,
    actual_tool_output: str,
    iteration: int,
    control_variable: Optional[str] = None
) -> CriticEvaluation:
    """ROLE 6 — EVIDENCE CRITIC: Independent reviewer evaluating evidence after an investigation step."""
    llm = get_role_llm(is_critic=True)

    prompt = (
        f"You are the EVIDENCE CRITIC role in an adaptive AI audit system.\n"
        f"Independently evaluate the empirical results of an investigation.\n\n"
        f"Hypothesis: {hypothesis.hypothesis}\n"
        f"Investigation Conducted: {investigation_summary}\n"
        f"Actual Tool Results: {actual_tool_output}\n"
        f"Iteration Number: {iteration}\n"
        f"Control Variable Used: {control_variable or 'None'}\n\n"
        f"Questions to Answer:\n"
        f"1. Does the evidence actually support the hypothesis?\n"
        f"2. Could the result be explained by another confounding variable (e.g. income, credit score)?\n"
        f"3. Is the sample size sufficient?\n"
        f"4. What evidence is still missing?\n"
        f"5. Should the auditor continue with a controlled follow-up investigation or stop?\n"
    )

    try:
        critic_res = llm.generate_structured(prompt=prompt, schema=CriticEvaluation)
        return critic_res
    except Exception as e:
        logger.warning(f"Evidence Critic LLM failed ({e}). Using deterministic critic evaluation.")
        
        # Deterministic logic for fallback critic
        supports = "disparity" in actual_tool_output.lower() or "difference" in actual_tool_output.lower() or "associated" in actual_tool_output.lower()
        
        if iteration == 1 and supports and not control_variable:
            # Iteration 1 found disparity -> Recommend continuing with controlled investigation
            return CriticEvaluation(
                supports_hypothesis=True,
                confounding_variables=["income", "credit_history", "loan_amount"],
                sample_size_sufficient=True,
                statistically_meaningful=True,
                missing_evidence=["Controlled comparison accounting for financial risk factors"],
                decision="CONTINUE",
                reasoning="Disparity observed in raw subgroup outcome rates. However, this difference may be explained by confounding financial variables (e.g. income or credit score). A controlled subgroup comparison is required before reaching a conclusion."
            )
        else:
            # Iteration 2+ or refuted -> STOP
            return CriticEvaluation(
                supports_hypothesis=supports,
                confounding_variables=[],
                sample_size_sufficient=True,
                statistically_meaningful=True,
                missing_evidence=[],
                decision="STOP",
                reasoning=f"Evidence collection complete for iteration {iteration}. Empirical observations provide sufficient evidence to evaluate the hypothesis."
            )
