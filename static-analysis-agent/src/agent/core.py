"""
Core agent logic for static analysis orchestration.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor
import os
import yaml
import logging

from ..tools.registry import registry
from ..tools.base_tool import AnalysisResult
from .tool_selector import ToolSelector
from .report_generator import ReportGenerator


class StaticAnalysisAgent:
    """Main static analysis agent."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
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
            'report_formats': ['json', 'html', 'markdown', 'summary'],
            'default_languages': [],
            'enabled_tools': ['bandit', 'flake8', 'pylint', 'semgrep'],  # Only currently installed tools
            'timeout_seconds': 300,
            'verbose': False,
            'log_level': 'INFO',
            'output_dir': 'output',
            'auto_archive': True,
            'fail_on_high_severity': False,
            'minimum_severity_threshold': 'low',
            'cache_results': True,
            'skip_unchanged_files': False
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
        self.logger.info(f"Starting analysis of codebase: {codebase_path}")

        if not path.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")

        # Detect languages if not specified
        detected_languages = languages or self._detect_languages(path)
        self.logger.info(f"Detected languages: {detected_languages}")

        # Select tools based on languages and configuration
        selected_tools = self.tool_selector.select_tools(
            detected_languages, tools, self.config
        )
        self.logger.info(f"Selected tools: {[tool.name for tool in selected_tools]}")

        if not selected_tools:
            self.logger.warning("No suitable tools found for the detected languages")
            return {
                'success': False,
                'error': 'No suitable tools found for the detected languages',
                'detected_languages': detected_languages
            }

        # Run analysis
        self.logger.info("Running analysis with selected tools...")
        results = await self._run_analysis_parallel(path, selected_tools)

        # Generate report
        self.logger.info("Generating analysis report...")
        report = self.report_generator.generate_report(results, detected_languages)

        self.logger.info("Analysis completed successfully")
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
                self.logger.info(f"Starting analysis with tool: {tool.name}")
                try:
                    # Load tool-specific configuration
                    tool_config = self._load_tool_config(tool.name)
                    result = await tool.run(codebase_path, tool_config)
                    self.logger.info(f"Completed analysis with tool: {tool.name} - {len(result.findings)} findings, {len(result.errors)} errors")
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error running tool {tool.name}: {str(e)}")
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

    def _load_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Load configuration for a specific tool."""
        config_dir = Path(__file__).parent.parent.parent / 'config' / 'tools'
        config_file = config_dir / f"{tool_name}.yaml"

        tool_config = {}
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config and loaded_config.get('enabled', True):
                        # Remove the 'enabled' key as it's not needed by tools
                        tool_config = {k: v for k, v in loaded_config.items() if k != 'enabled'}
            except Exception as e:
                self.logger.warning(f"Failed to load config for {tool_name}: {e}")

        # Merge with any global tool config
        global_tool_config = self.config.get(tool_name, {})
        tool_config.update(global_tool_config)

        return tool_config

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
        self.logger.info("Starting tool installation...")
        if tool_names:
            self.logger.info(f"Installing specific tools: {tool_names}")
            results = []
            for name in tool_names:
                self.logger.info(f"Installing tool: {name}")
                success = await registry.install_tool(name)
                if success:
                    self.logger.info(f"Successfully installed tool: {name}")
                else:
                    self.logger.warning(f"Failed to install tool: {name}")
                results.append({
                    'tool': name,
                    'success': success
                })
        else:
            self.logger.info("Installing all available tools...")
            results = registry.install_all_tools()

        self.logger.info("Tool installation completed")
        return {
            'results': results
        }
