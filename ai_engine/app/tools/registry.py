import logging
from typing import Dict, Optional, List
from app.tools.base import BaseTool
from app.tools.repository_tool import RepositoryTool
from app.tools.model_tool import ModelTool, ModifyInputTool, CompareOutputsTool
from app.tools.analysis_tool import AnalyzeEvidenceTool
from app.tools.statistical_tools import (
    DatasetProfileTool,
    MissingnessAnalysisTool,
    ClassDistributionTool,
    GroupDistributionTool,
    ProxyAnalysisTool,
    ControlledSubgroupComparisonTool,
    GroupPerformanceAnalysisTool,
    ErrorRateAnalysisTool
)

logger = logging.getLogger("ai_engine.tools.registry")


class ToolRegistry:
    """
    Central registry for safe, explicitly registered AI Engine tools.
    Prevents arbitrary code execution or dynamic imports from untrusted strings.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Explicitly register known safe tools
        self.register(RepositoryTool())
        self.register(ModelTool())
        self.register(ModifyInputTool())
        self.register(CompareOutputsTool())
        self.register(AnalyzeEvidenceTool())
        
        # Register new statistical analysis tools
        self.register(DatasetProfileTool())
        self.register(MissingnessAnalysisTool())
        self.register(ClassDistributionTool())
        self.register(GroupDistributionTool())
        self.register(ProxyAnalysisTool())
        self.register(ControlledSubgroupComparisonTool())
        self.register(GroupPerformanceAnalysisTool())
        self.register(ErrorRateAnalysisTool())


    def register(self, tool: BaseTool) -> None:
        """Register a safe tool instance in the registry."""
        self._tools[tool.name.lower()] = tool
        logger.debug("Registered tool: %s", tool.name)

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Retrieve registered tool instance by name.
        Returns None if tool is not registered.
        """
        if not tool_name:
            return None
        return self._tools.get(tool_name.lower())

    def list_tools(self) -> List[str]:
        """Return list of all registered safe tool names."""
        return list(self._tools.keys())


# Singleton registry instance
default_tool_registry = ToolRegistry()
