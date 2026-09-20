from typing import Dict, Any, List, Optional
from app.tools.base import BaseTool
from app.schemas.investigation import ToolExecution


class AnalyzeEvidenceTool(BaseTool):
    """
    Perform deterministic analysis and logging over collected observation evidence.
    Operates locally on structured data.
    """
    name = "analyze_evidence"
    description = "Analyze and summarize collected evidence items for a specific focus area."

    def run(self, step_id: str, parameters: Dict[str, Any]) -> ToolExecution:
        evidence_items = parameters.get("evidence_items") or parameters.get("processed_items") or []
        focus_area = parameters.get("focus_area", "General Investigation")

        return self._create_execution(
            step_id=step_id,
            status="success",
            result={
                "evidence_count": len(evidence_items),
                "focus_area": focus_area,
                "analyzed_items": evidence_items
            },
            evidence=[f"Analyzed {len(evidence_items)} evidence items for focus area: '{focus_area}'."],
            error=None,
            parameters=parameters
        )


def analyze_evidence(evidence_items: List[str], focus_area: str = "General", step_id: str = "STEP-1") -> ToolExecution:
    tool = AnalyzeEvidenceTool()
    return tool.run(step_id=step_id, parameters={"evidence_items": evidence_items, "focus_area": focus_area})
