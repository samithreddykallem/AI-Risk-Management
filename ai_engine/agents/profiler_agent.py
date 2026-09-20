import json
from ai_engine.agents.base_agent import BaseAgent
from ai_engine.models.system_input import SystemInput, ProjectInput
from ai_engine.models.system_profile import SystemProfile


class ProfilerAgent(BaseAgent):
    """Agent responsible for understanding an individual AI project and constructing its SystemProfile."""

    def analyze_project(self, project_input: ProjectInput) -> SystemProfile:
        """
        Analyze an individual AI project specification and return a strict, structured SystemProfile.
        Reasons strictly from the submitted project information. Never invents facts or uses generic domain checklists.
        """
        
        prompt = f"""
        You are an expert AI Auditor & System Architecture Profiler.
        Analyze the following submitted AI Project specification carefully:

        PROJECT NAME: {project_input.project_name}
        DESCRIPTION: {project_input.description}
        GITHUB URL: {project_input.github_url or 'unknown'}
        DOCUMENTATION: {project_input.documentation or 'unknown'}
        SAMPLE INPUTS: {json.dumps(project_input.sample_inputs) if project_input.sample_inputs else 'unknown'}
        SAMPLE OUTPUTS: {json.dumps(project_input.sample_outputs) if project_input.sample_outputs else 'unknown'}

        CRITICAL AUDITING INSTRUCTIONS:
        1. DO NOT use fixed domain checklists or assume default risks based on category names.
        2. Reason strictly from the actual provided project information above.
        3. If any field or detail is not explicitly stated or clearly inferable from the text, you MUST mark it as "unknown" (or an empty list if a list field). NEVER invent facts, capabilities, or integrations.
        4. Fill "observed_evidence" with a dictionary mapping key profile attributes (e.g., "purpose", "model_type", "human_involvement") to specific quotes or pieces of text from the submission that support your analysis.
        5. Identify "important_unknowns" - critical missing pieces of technical/operational context that are necessary to fully evaluate the system.
        """

        system_prompt = (
            "You are an objective AI system auditor. You extract structured System Profiles strictly from "
            "provided documentation without inventing facts or relying on fixed domain checklists."
        )

        return self.llm.generate_structured(
            prompt=prompt,
            schema=SystemProfile,
            system_prompt=system_prompt
        )

    def build_profile(self, system_input: SystemInput) -> SystemProfile:
        """Legacy profile builder for SystemInput."""
        proj_input = ProjectInput(
            project_name=system_input.system_name,
            description=f"{system_input.problem_solved}. Use case: {system_input.intended_use_case}. Implementation: {system_input.model_implementation_details}",
            documentation=f"Autonomy: {system_input.autonomy_level}. Data: {', '.join(system_input.data_handled)}. Potential consequences: {', '.join(system_input.potential_consequences)}",
            sample_inputs=system_input.input_types,
            sample_outputs=system_input.output_types
        )
        return self.analyze_project(proj_input)
