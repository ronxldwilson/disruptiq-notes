"""
Semgrep integration for static analysis.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil
import logging

from ..base_tool import BaseTool, AnalysisResult


class SemgrepTool(BaseTool):
    """Semgrep static analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="semgrep",
            description="Semantic code analysis for security vulnerabilities and code quality",
            supported_languages=["python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "php", "ruby", "csharp"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install Semgrep using pip or system package manager."""
        try:
            # Try installing via pip first
            result = await asyncio.create_subprocess_exec(
                'pip', 'install', 'semgrep',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                return True

            # If pip fails, try installing via pip3
            result = await asyncio.create_subprocess_exec(
                'pip3', 'install', 'semgrep',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            return result.returncode == 0

        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if Semgrep is installed."""
        try:
            result = subprocess.run(
                ['semgrep', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run Semgrep on the codebase."""
        config = config or {}
        self.logger.debug(f"Running Semgrep on {codebase_path}")

        cmd = ['semgrep', '--json']

        # Add rules if specified
        rules = config.get('rules', ['auto'])
        if rules:
            for rule in rules:
                if rule.startswith('p/'):
                    cmd.extend(['--config', rule])
                else:
                    cmd.extend(['--config', rule])

        # Add custom config if specified
        custom_config = config.get('custom_config_path')
        if custom_config:
            cmd.extend(['--config', str(custom_config)])

        # Add codebase path - use "." since we're setting cwd to the codebase directory
        cmd.append(".")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(codebase_path)
            )

            stdout, stderr = await process.communicate()

            return self.parse_output(stdout.decode(), stderr.decode())

        except Exception as e:
            return AnalysisResult(
                tool_name=self.name,
                findings=[],
                errors=[f"Failed to run Semgrep: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse Semgrep JSON output."""
        findings = []
        errors = []

        if error_output.strip():
            # Filter out SSL warnings and other non-critical messages
            filtered_errors = []
            for line in error_output.split('\n'):
                line = line.strip()
                if line and not any(keyword in line.upper() for keyword in ['WARNING', 'IGNORED', 'NEGATIVE SERIAL']):
                    filtered_errors.append(line)
            if filtered_errors:
                errors.extend(filtered_errors)

        try:
            # Semgrep outputs JSON at the end, extract it
            if isinstance(output, bytes):
                output_str = output.decode()
            else:
                output_str = output

            # Find the JSON part (starts with '{')
            json_start = output_str.find('{')
            if json_start == -1:
                raise json.JSONDecodeError("No JSON found in output", output_str, 0)

            json_part = output_str[json_start:]
            data = json.loads(json_part)
            results = data.get('results', [])

            for result in results:
                extra = result.get('extra', {})
                finding = {
                    'tool': 'semgrep',
                    'rule': result.get('check_id', ''),
                    'file': result.get('path', ''),
                    'line': result.get('start', {}).get('line', 0),
                    'column': result.get('start', {}).get('col', 0),
                    'severity': self._map_severity(extra.get('severity', 'medium')),
                    'message': extra.get('message', ''),
                    'code': result.get('lines', ''),
                    'cwe': extra.get('metadata', {}).get('cwe', ''),
                    'category': extra.get('metadata', {}).get('category', '')
                }
                findings.append(finding)

        except json.JSONDecodeError:
            errors.append("Failed to parse Semgrep output as JSON")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )

    def _map_severity(self, semgrep_severity: str) -> str:
        """Map Semgrep severity to our standard levels."""
        severity_map = {
            'ERROR': 'high',
            'WARNING': 'medium',
            'INFO': 'low'
        }
        return severity_map.get(semgrep_severity.upper(), 'medium')
