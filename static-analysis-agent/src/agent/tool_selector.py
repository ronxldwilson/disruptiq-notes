"""
Tool selection logic for the static analysis agent.
"""

from typing import List, Dict, Any, Optional
from ..tools.registry import registry


class ToolSelector:
    """Handles intelligent tool selection based on codebase characteristics."""

    def __init__(self):
        self.language_tool_mapping = {
            'python': ['bandit', 'pylint', 'safety', 'semgrep'],
            'javascript': ['eslint', 'semgrep'],
            'typescript': ['eslint', 'semgrep'],
            'java': ['semgrep', 'spotbugs'],
            'cpp': ['semgrep', 'cppcheck'],
            'c': ['semgrep', 'cppcheck'],
            'go': ['semgrep', 'gosec'],
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

        # Auto-select tools based on languages
        selected_tools = set()

        for language in languages:
            lang_lower = language.lower()
            if lang_lower in self.language_tool_mapping:
                for tool_name in self.language_tool_mapping[lang_lower]:
                    tool = registry.get_tool(tool_name)
                    if tool and tool.is_installed():
                        selected_tools.add(tool)

        # Add general-purpose tools like semgrep if available
        semgrep = registry.get_tool('semgrep')
        if semgrep and semgrep.is_installed():
            selected_tools.add(semgrep)

        return list(selected_tools)

    def get_recommended_tools(self, languages: List[str]) -> Dict[str, List[str]]:
        """Get recommended tools for given languages."""
        recommendations = {}
        for language in languages:
            lang_lower = language.lower()
            if lang_lower in self.language_tool_mapping:
                recommendations[language] = self.language_tool_mapping[lang_lower]
        return recommendations
