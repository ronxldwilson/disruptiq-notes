"""
Pylint integration for Python code analysis.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..base_tool import BaseTool, AnalysisResult


class PylintTool(BaseTool):
    """Pylint Python code analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="pylint",
            description="Python source code analyzer for bugs and quality",
            supported_languages=["python"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install Pylint using pip."""
        try:
            # Try installing via pip first
            result = await asyncio.create_subprocess_exec(
                'pip', 'install', 'pylint',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                return True

            # If pip fails, try installing via pip3
            result = await asyncio.create_subprocess_exec(
                'pip3', 'install', 'pylint',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            return result.returncode == 0

        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if Pylint is installed."""
        try:
            result = subprocess.run(
                ['pylint', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run Pylint on the codebase."""
        config = config or {}
        self.logger.debug(f"Running Pylint on {codebase_path}")

        cmd = ['pylint', '--output-format=json']

        # Add custom config if specified
        custom_config = config.get('custom_config_path')
        if custom_config:
            cmd.extend(['--rcfile', str(custom_config)])

        # Add disable rules if specified
        disable = config.get('disable')
        if disable:
            if isinstance(disable, list):
                disable = ','.join(disable)
            cmd.extend(['--disable', disable])

        # Add enable rules if specified
        enable = config.get('enable')
        if enable:
            if isinstance(enable, list):
                enable = ','.join(enable)
            cmd.extend(['--enable', enable])

        # Add reports level
        reports = config.get('reports', False)
        if reports:
            cmd.append('--reports=y')
        else:
            cmd.append('--reports=n')

        # Find Python files and add them
        python_files = []
        for file_path in codebase_path.rglob('*.py'):
            python_files.append(str(file_path))

        if not python_files:
            return AnalysisResult(
                tool_name=self.name,
                findings=[],
                errors=[]
            )

        cmd.extend(python_files)

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
                errors=[f"Failed to run Pylint: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse Pylint JSON output."""
        findings = []
        errors = []

        if error_output.strip():
            errors.append(error_output.strip())

        try:
            if output.strip():
                data = json.loads(output.strip())
                for finding in data:
                    finding_dict = {
                        'tool': 'pylint',
                        'rule': finding.get('message-id', ''),
                        'file': finding.get('path', ''),
                        'line': finding.get('line', 0),
                        'column': finding.get('column', 0),
                        'severity': self._map_severity(finding.get('type', 'info')),
                        'message': finding.get('message', ''),
                        'code': finding.get('symbol', ''),
                        'cwe': '',
                        'category': 'code-quality'
                    }
                    findings.append(finding_dict)
        except json.JSONDecodeError:
            errors.append("Failed to parse Pylint output as JSON")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )

    def _map_severity(self, pylint_type: str) -> str:
        """Map Pylint message types to severity levels."""
        severity_map = {
            'error': 'high',
            'fatal': 'high',
            'warning': 'medium',
            'info': 'low',
            'convention': 'low',
            'refactor': 'low'
        }
        return severity_map.get(pylint_type.lower(), 'low')
