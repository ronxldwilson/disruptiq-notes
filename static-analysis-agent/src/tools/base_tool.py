"""
Base tool interface for static analysis tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio


class AnalysisResult:
    """Represents the result of a static analysis tool run."""

    def __init__(self, tool_name: str, findings: List[Dict[str, Any]], errors: List[str] = None):
        self.tool_name = tool_name
        self.findings = findings
        self.errors = errors or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'tool_name': self.tool_name,
            'findings': self.findings,
            'errors': self.errors
        }


class BaseTool(ABC):
    """Abstract base class for static analysis tools."""

    def __init__(self, name: str, description: str, supported_languages: List[str]):
        self.name = name
        self.description = description
        self.supported_languages = supported_languages

    @abstractmethod
    async def install(self) -> bool:
        """Install the tool if not already installed."""
        pass

    @abstractmethod
    async def is_installed(self) -> bool:
        """Check if the tool is installed and available."""
        pass

    @abstractmethod
    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run the tool on the given codebase."""
        pass

    @abstractmethod
    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse the tool's output into a standardized format."""
        pass

    def get_config_schema(self) -> Dict[str, Any]:
        """Return the configuration schema for this tool."""
        return {
            'type': 'object',
            'properties': {
                'enabled': {'type': 'boolean', 'default': True},
                'rules': {'type': 'array', 'items': {'type': 'string'}},
                'custom_config_path': {'type': 'string'}
            }
        }

    def __str__(self) -> str:
        return f"{self.name}: {self.description} (supports: {', '.join(self.supported_languages)})"
