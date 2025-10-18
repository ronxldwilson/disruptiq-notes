"""
Core agent logic for static analysis orchestration.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor
import os
import yaml

from ..tools.registry import registry
from ..tools.base_tool import AnalysisResult
from .tool_selector import ToolSelector
from .report_generator import ReportGenerator


class StaticAnalysisAgent:
    """Main static analysis agent."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.tool_selector = ToolSelector()
        self.report_generator = ReportGenerator()
        self.max_concurrent_tools = self.config.get('max_concurrent_tools', 4)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from config files."""
        config_dir = Path(__file__).parent.parent.parent / 'config'
        agent_config_file = config_dir / 'agent.yaml'

        default_config = {
            'parallel_execution': True,
            'max_concurrent_tools': 4,
            'report_formats': ['json', 'html', 'markdown'],
            'default_languages': [],
            'enabled_tools': ['semgrep'],
            'timeout_seconds': 300,
            'verbose': False
        }

        if agent_config_file.exists():
            try:
                with open(agent_config_file, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        default_config.update(loaded_config)
            except Exception:
                pass  # Use defaults if config loading fails

        return default_config

    async def analyze_codebase(self, codebase_path: str, languages: Optional[List[str]] = None,
                             tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze a codebase using appropriate tools."""

        path = Path(codebase_path)
        if not path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")

        # Detect languages if not specified
        detected_languages = languages or self._detect_languages(path)

        # Select tools based on languages and configuration
        selected_tools = self.tool_selector.select_tools(
            detected_languages, tools, self.config
        )

        if not selected_tools:
            return {
                'success': False,
                'error': 'No suitable tools found for the detected languages',
                'detected_languages': detected_languages
            }

        # Run analysis
        results = await self._run_analysis_parallel(path, selected_tools)

        # Generate report
        report = self.report_generator.generate_report(results, detected_languages)

        return {
            'success': True,
            'detected_languages': detected_languages,
            'tools_used': [tool.name for tool in selected_tools],
            'results': [result.to_dict() for result in results],
            'report': report
        }

    def _detect_languages(self, path: Path) -> List[str]:
        """Detect programming languages in the codebase."""
        languages = set()

        # Simple file extension-based detection
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.cs': 'csharp'
        }

        for file_path in path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in extensions:
                    languages.add(extensions[ext])

        return list(languages)

    async def _run_analysis_parallel(self, codebase_path: Path,
                                   tools: List[Any]) -> List[AnalysisResult]:
        """Run multiple tools in parallel."""
        semaphore = asyncio.Semaphore(self.max_concurrent_tools)
        results = []

        async def run_tool(tool):
            async with semaphore:
                try:
                    result = await tool.run(codebase_path, self.config.get(tool.name, {}))
                    results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = AnalysisResult(
                        tool_name=tool.name,
                        findings=[],
                        errors=[str(e)]
                    )
                    results.append(error_result)

        # Create tasks for all tools
        tasks = [run_tool(tool) for tool in tools]
        await asyncio.gather(*tasks, return_exceptions=True)

        return results

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get information about available tools."""
        tools_info = []
        available_tools = registry.get_available_tools()
        available_names = {tool.name for tool in available_tools}

        for tool in registry.get_all_tools():
            tools_info.append({
                'name': tool.name,
                'description': tool.description,
                'supported_languages': tool.supported_languages,
                'installed': tool.name in available_names
            })
        return tools_info

    async def install_tools(self, tool_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Install specified tools or all tools."""
        if tool_names:
            results = []
            for name in tool_names:
                success = await registry.install_tool(name)
                results.append({
                    'tool': name,
                    'success': success
                })
        else:
            results = registry.install_all_tools()

        return {
            'results': results
        }
