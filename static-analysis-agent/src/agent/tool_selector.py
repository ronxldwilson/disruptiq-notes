"""
Tool selection logic for the static analysis agent.
"""

from typing import List, Dict, Any, Optional
from ..tools.registry import registry


class ToolSelector:
    """Handles intelligent tool selection based on codebase characteristics."""

    def __init__(self):
        self.language_tool_mapping = {
            'python': ['flake8', 'bandit', 'pylint', 'safety', 'semgrep'],
            'javascript': ['eslint', 'semgrep'],
            'typescript': ['eslint', 'semgrep'],
            'java': ['semgrep', 'spotbugs'],
            'cpp': ['semgrep', 'cppcheck'],
            'c': ['semgrep', 'cppcheck'],
            'go': ['semgrep', 'golint', 'gosec'],
            'rust': ['semgrep', 'clippy'],
            'php': ['semgrep', 'phpstan'],
            'ruby': ['semgrep', 'rubocop']
        }

    def select_tools(self, languages: List[str], requested_tools: Optional[List[str]] = None,
                    config: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Select appropriate tools for the given languages."""

        if requested_tools:
            # Use specifically requested tools
            selected = []
            for tool_name in requested_tools:
                tool = registry.get_tool(tool_name)
                if tool and tool.is_installed():
                    selected.append(tool)
            return selected

        # Auto-select enabled tools from config
        enabled_tools = config.get('enabled_tools', []) if config else []
        selected_tools = set()

        # Get all available tools that are installed and enabled
        available_tools = registry.get_available_tools()
        for tool in available_tools:
            if tool.name in enabled_tools:
                selected_tools.add(tool)

        return list(selected_tools)

    def get_recommended_tools(self, languages: List[str]) -> Dict[str, List[str]]:
        """Get recommended tools for given languages."""
        recommendations = {}
        for language in languages:
            lang_lower = language.lower()
            if lang_lower in self.language_tool_mapping:
                recommendations[language] = self.language_tool_mapping[lang_lower]
        return recommendations
