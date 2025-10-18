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

        cmd = ['pylint']

        # Set output format
        output_format = config.get('output_format', 'json')
        cmd.extend(['--output-format', output_format])

        # Add Python version if specified
        py_version = config.get('py_version')
        if py_version:
            cmd.extend(['--py-version', py_version])

        # Add include options (commented out as not supported in all versions)
        # if config.get('include_ids', True):
        #     cmd.append('--include-ids=y')
        # else:
        #     cmd.append('--include-ids=n')

        # if config.get('include_symbolic_names', True):
        #     cmd.append('--include-symbolic-names=y')
        # else:
        #     cmd.append('--include-symbolic-names=n')

        # Add ignore patterns
        ignore_patterns = config.get('ignore_patterns', [])
        for pattern in ignore_patterns:
            cmd.extend(['--ignore-patterns', pattern])

        # Add disable rules
        disable_rules = config.get('disable', [])
        if disable_rules:
            if isinstance(disable_rules, list):
                disable_rules = ','.join(disable_rules)
            cmd.extend(['--disable', disable_rules])

        # Add enable rules
        enable_rules = config.get('enable', [])
        if enable_rules:
            if isinstance(enable_rules, list):
                enable_rules = ','.join(enable_rules)
            cmd.extend(['--enable', enable_rules])

        # Add confidence levels
        confidence_levels = config.get('confidence', [])
        if confidence_levels:
            if isinstance(confidence_levels, list):
                confidence_levels = ','.join(confidence_levels)
            cmd.extend(['--confidence', confidence_levels])

        # Add various limits from config
        limits = {
            'max_line_length': config.get('max_line_length'),
            'max_args': config.get('max_args'),
            'max_locals': config.get('max_locals'),
            'max_branches': config.get('max_branches'),
            'max_statements': config.get('max_statements'),
            'max_attributes': config.get('max_attributes'),
            'min_public_methods': config.get('min_public_methods')
            # 'max_complexity': config.get('max_complexity')  # Commented out as not supported in all versions
        }

        for limit_name, limit_value in limits.items():
            if limit_value is not None:
                cmd.extend([f'--{limit_name.replace("_", "-")}', str(limit_value)])

        # Find Python files and add them
        python_files = []
        py_files_pattern = config.get('py_files', ['*.py'])
        for pattern in py_files_pattern:
            for file_path in codebase_path.rglob(pattern):
                # Check ignore patterns
                ignore_list = config.get('ignore', [])
                should_ignore = any(ignored in str(file_path) for ignored in ignore_list)
                if not should_ignore:
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
