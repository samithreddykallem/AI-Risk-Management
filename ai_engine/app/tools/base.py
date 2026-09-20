import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.investigation import ToolExecution


class ToolOutput(BaseModel):
    """Output structure returned by tool execution."""
    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)
    observation: str = ""
    evidence: list = Field(default_factory=list)
    error: Optional[str] = None


class BaseTool(ABC):
    """Abstract base class for safe, structured AI Engine investigation tools."""

    name: str
    description: str

    def execute(self, **kwargs) -> ToolOutput:
        """Optional tool execution method for modern statistical tools."""
        raise NotImplementedError("Tool must implement execute() or run()")

    def run(self, step_id: str, parameters: Dict[str, Any]) -> ToolExecution:
        """Execute tool logic for a step and return structured ToolExecution record."""
        try:
            out = self.execute(**parameters)
            status_str = "success" if out.success else "failed"
            return self._create_execution(
                step_id=step_id,
                status=status_str,
                result=out.data,
                evidence=out.evidence or ([out.observation] if out.observation else []),
                error=out.error,
                parameters=parameters
            )
        except Exception as e:
            return self._create_execution(
                step_id=step_id,
                status="failed",
                error=str(e),
                parameters=parameters
            )



    def _create_execution(
        self,
        step_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        evidence: Optional[list] = None,
        error: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolExecution:
        return ToolExecution(
            execution_id=f"EXEC-{uuid.uuid4().hex[:6]}",
            step_id=step_id,
            tool=self.name,
            parameters=parameters or {},
            timestamp=datetime.now().isoformat(),
            status=status,
            result=result,
            evidence=evidence or [],
            error=error
        )
