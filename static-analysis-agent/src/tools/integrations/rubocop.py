"""
RuboCop integration for Ruby code analysis.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..base_tool import BaseTool, AnalysisResult


class RubocopTool(BaseTool):
    """RuboCop Ruby code analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="rubocop",
            description="Ruby static code analyzer and formatter",
            supported_languages=["ruby"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install RuboCop using gem."""
        try:
            result = await asyncio.create_subprocess_exec(
                'gem', 'install', 'rubocop',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            return result.returncode == 0

        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if RuboCop is installed."""
        try:
            result = subprocess.run(
                ['rubocop', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run RuboCop on the codebase."""
        config = config or {}
        self.logger.debug(f"Running RuboCop on {codebase_path}")

        cmd = ['rubocop', '--format', 'json']

        # Add custom config if specified
        custom_config = config.get('custom_config_path')
        if custom_config:
            cmd.extend(['--config', str(custom_config)])

        # Add require files if specified
        requires = config.get('require', [])
        for req in requires:
            cmd.extend(['--require', req])

        # Add only rules if specified
        only = config.get('only')
        if only:
            if isinstance(only, list):
                only = ','.join(only)
            cmd.extend(['--only', only])

        # Add except rules if specified
        except_rules = config.get('except')
        if except_rules:
            if isinstance(except_rules, list):
                except_rules = ','.join(except_rules)
            cmd.extend(['--except', except_rules])

        # Add display style guide if specified
        display_style_guide = config.get('display_style_guide', False)
        if display_style_guide:
            cmd.append('--display-style-guide')

        # Add display cop names if specified
        display_cop_names = config.get('display_cop_names', False)
        if display_cop_names:
            cmd.append('--display-cop-names')

        # Add fail level if specified
        fail_level = config.get('fail_level')
        if fail_level:
            cmd.extend(['--fail-level', fail_level])

        # Add codebase path
        cmd.append(str(codebase_path))

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return self.parse_output(stdout.decode(), stderr.decode())

        except Exception as e:
            return AnalysisResult(
                tool_name=self.name,
                findings=[],
                errors=[f"Failed to run RuboCop: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse RuboCop JSON output."""
        findings = []
        errors = []

        if error_output.strip():
            errors.append(error_output.strip())

        try:
            if output.strip():
                data = json.loads(output.strip())
                for file_data in data.get('files', []):
                    filename = file_data.get('path', '')
                    for offense in file_data.get('offenses', []):
                        finding_dict = {
                            'tool': 'rubocop',
                            'rule': offense.get('cop_name', ''),
                            'file': filename,
                            'line': offense.get('location', {}).get('line', 0),
                            'column': offense.get('location', {}).get('column', 0),
                            'severity': self._map_severity(offense.get('severity', 'convention')),
                            'message': offense.get('message', ''),
                            'code': offense.get('location', {}).get('source', ''),
                            'cwe': '',
                            'category': 'style'
                        }
                        findings.append(finding_dict)
        except json.JSONDecodeError:
            errors.append("Failed to parse RuboCop output as JSON")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )

    def _map_severity(self, rubocop_severity: str) -> str:
        """Map RuboCop severity levels."""
        severity_map = {
            'fatal': 'high',
            'error': 'high',
            'warning': 'medium',
            'convention': 'low',
            'refactor': 'low',
            'info': 'low'
        }
        return severity_map.get(rubocop_severity.lower(), 'low')
