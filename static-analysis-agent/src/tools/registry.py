"""
Tool registry for managing static analysis tools.
"""

from typing import Dict, List, Type, Optional
from pathlib import Path
import importlib
import pkgutil
from .base_tool import BaseTool


class ToolRegistry:
    """Registry for static analysis tools."""

    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}
        self._instances: Dict[str, BaseTool] = {}
        self._discover_tools()

    def _discover_tools(self):
        """Discover and register available tools."""
        # Import all tool modules from integrations
        integrations_path = Path(__file__).parent / 'integrations'
        if integrations_path.exists():
            for finder, name, ispkg in pkgutil.iter_modules([str(integrations_path)]):
                try:
                    module = importlib.import_module(f'src.tools.integrations.{name}')
                    # Look for tool classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, BaseTool) and
                            attr != BaseTool):
                            self.register_tool(attr)
                except ImportError as e:
                    print(f"Failed to import tool module {name}: {e}")

    def register_tool(self, tool_class: Type[BaseTool]):
        """Register a tool class."""
        tool_instance = tool_class()
        self._tools[tool_instance.name] = tool_class
        self._instances[tool_instance.name] = tool_instance

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool instance by name."""
        return self._instances.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tool instances."""
        return list(self._instances.values())

    def get_tools_for_language(self, language: str) -> List[BaseTool]:
        """Get tools that support a specific language."""
        return [tool for tool in self._instances.values()
                if language.lower() in [lang.lower() for lang in tool.supported_languages]]

    async def get_available_tools(self) -> List[BaseTool]:
        """Get tools that are currently installed."""
        available = []
        for tool in self._instances.values():
            try:
                if await tool.is_installed():
                    available.append(tool)
            except Exception:
                # If check fails, assume not installed
                pass
        return available

    def install_tool(self, name: str) -> bool:
        """Install a specific tool."""
        tool = self.get_tool(name)
        if tool:
            return tool.install()
        return False

    def install_all_tools(self) -> List[str]:
        """Install all registered tools."""
        results = []
        for tool in self._instances.values():
            try:
                success = tool.install()
                if success:
                    results.append(f"Successfully installed {tool.name}")
                else:
                    results.append(f"Failed to install {tool.name}")
            except Exception as e:
                results.append(f"Error installing {tool.name}: {e}")
        return results


# Global registry instance
registry = ToolRegistry()
