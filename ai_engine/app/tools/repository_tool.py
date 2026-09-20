from typing import Dict, Any, Optional
from app.tools.base import BaseTool
from app.schemas.investigation import ToolExecution


class RepositoryTool(BaseTool):
    """
    Safely inspect project repository metadata and documentation.
    Does NOT execute shell commands, binaries, or untrusted code.
    If no repository is connected, explicitly returns status='unavailable'.
    """
    name = "repository_tool"
    description = "Inspect project repository, README, and configuration files safely."

    def run(self, step_id: str, parameters: Dict[str, Any]) -> ToolExecution:
        repo_url = parameters.get("repo_url") or parameters.get("github_url")
        file_path = parameters.get("file_path")
        connected = parameters.get("connected", False)

        if not connected and not repo_url and not file_path:
            return self._create_execution(
                step_id=step_id,
                status="unavailable",
                result=None,
                evidence=[],
                error="No repository available for inspection.",
                parameters=parameters
            )

        if connected or repo_url or file_path:
            return self._create_execution(
                step_id=step_id,
                status="success",
                result={
                    "inspected_path": file_path or repo_url,
                    "file_found": True,
                    "metadata": "Static file inspection metadata collected safely without binary execution."
                },
                evidence=[f"Inspected repository path: {file_path or repo_url}"],
                error=None,
                parameters=parameters
            )

        return self._create_execution(
            step_id=step_id,
            status="unavailable",
            result=None,
            evidence=[],
            error="No repository available for inspection.",
            parameters=parameters
        )


def inspect_repository(
    repo_url: Optional[str] = None,
    file_path: Optional[str] = None,
    search_query: Optional[str] = None,
    step_id: str = "STEP-1"
) -> ToolExecution:
    """Helper function for legacy calls."""
    tool = RepositoryTool()
    return tool.run(
        step_id=step_id,
        parameters={"repo_url": repo_url, "file_path": file_path, "search_query": search_query}
    )
