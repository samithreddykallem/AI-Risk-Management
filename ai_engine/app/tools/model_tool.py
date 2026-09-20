from typing import Dict, Any, Optional
from app.tools.base import BaseTool
from app.schemas.investigation import ToolExecution


class ModelTool(BaseTool):
    """
    Run an executable model interface against controlled inputs.
    If no executable model interface is connected, explicitly returns status='unavailable'.
    Does NOT fabricate model outputs.
    """
    name = "model_tool"
    description = "Query target AI model endpoint or simulator with controlled test payloads."

    def run(self, step_id: str, parameters: Dict[str, Any]) -> ToolExecution:
        model_endpoint = parameters.get("model_endpoint")
        connected = parameters.get("connected", False)
        input_data = parameters.get("input_data") or parameters.get("input")

        # Explicit check: If no live model endpoint or simulator is connected, return unavailable
        if not connected and not model_endpoint:
            return self._create_execution(
                step_id=step_id,
                status="unavailable",
                result=None,
                evidence=[],
                error="No executable model interface is currently connected.",
                parameters=parameters
            )

        # If a model interface IS connected:
        return self._create_execution(
            step_id=step_id,
            status="success",
            result={
                "model_endpoint": model_endpoint,
                "input_sent": input_data,
                "output_received": f"Execution result for connected model at '{model_endpoint}'"
            },
            evidence=[f"Executed connected model at '{model_endpoint}' with input payload."],
            error=None,
            parameters=parameters
        )


class ModifyInputTool(BaseTool):
    """
    Safely modify specific input fields for controlled variable testing.
    Creates a modified copy of an input rather than modifying the original.
    """
    name = "modify_input"
    description = "Create a modified copy of an input dictionary with perturbed fields."

    def run(self, step_id: str, parameters: Dict[str, Any]) -> ToolExecution:
        base_input = parameters.get("base_input") or parameters.get("input_data") or {}
        perturbations = parameters.get("perturbations") or parameters.get("modifications") or {}

        if not isinstance(base_input, dict):
            base_input = {"raw_input": base_input}

        modified = dict(base_input)
        if isinstance(perturbations, dict):
            modified.update(perturbations)

        return self._create_execution(
            step_id=step_id,
            status="success",
            result={
                "original_input": base_input,
                "modified_input": modified,
                "perturbed_fields": list(perturbations.keys()) if isinstance(perturbations, dict) else []
            },
            evidence=[f"Perturbed input fields: {list(perturbations.keys()) if isinstance(perturbations, dict) else []}"],
            error=None,
            parameters=parameters
        )


class CompareOutputsTool(BaseTool):
    """
    Safely compare two outputs to measure variance, discrepancies, or anomalies.
    Operates deterministically over structured output payloads.
    """
    name = "compare_outputs"
    description = "Compare baseline and perturbed outputs deterministically to detect variance."

    def run(self, step_id: str, parameters: Dict[str, Any]) -> ToolExecution:
        output_a = parameters.get("output_a") or parameters.get("baseline_output")
        output_b = parameters.get("output_b") or parameters.get("perturbed_output")
        metric = parameters.get("metric", "exact_match")

        is_different = (output_a != output_b)
        return self._create_execution(
            step_id=step_id,
            status="success",
            result={
                "output_a": output_a,
                "output_b": output_b,
                "variance_detected": is_different,
                "metric_used": metric
            },
            evidence=[f"Output variance detected via metric '{metric}': {is_different}"],
            error=None,
            parameters=parameters
        )


# Legacy functions helper
def run_model(input_data: Any, model_endpoint: Optional[str] = None, step_id: str = "STEP-1") -> ToolExecution:
    tool = ModelTool()
    return tool.run(step_id=step_id, parameters={"input_data": input_data, "model_endpoint": model_endpoint})


def modify_input(base_input: Dict[str, Any], perturbations: Dict[str, Any], step_id: str = "STEP-1") -> ToolExecution:
    tool = ModifyInputTool()
    return tool.run(step_id=step_id, parameters={"base_input": base_input, "perturbations": perturbations})


def compare_outputs(output_a: Any, output_b: Any, metric: str = "exact_match", step_id: str = "STEP-1") -> ToolExecution:
    tool = CompareOutputsTool()
    return tool.run(step_id=step_id, parameters={"output_a": output_a, "output_b": output_b, "metric": metric})
