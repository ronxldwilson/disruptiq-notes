"""
Semgrep integration for static analysis.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

from ..base_tool import BaseTool, AnalysisResult


class SemgrepTool(BaseTool):
    """Semgrep static analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="semgrep",
            description="Semantic code analysis for security vulnerabilities and code quality",
            supported_languages=["python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "php", "ruby", "csharp"]
        )

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

    async def is_installed(self) -> bool:
        """Check if Semgrep is installed."""
        try:
            result = await asyncio.create_subprocess_exec(
                'semgrep', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run Semgrep on the codebase."""
        config = config or {}

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

        # Add codebase path
        cmd.append(str(codebase_path))

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
            errors.append(error_output.strip())

        try:
            data = json.loads(output)
            results = data.get('results', [])

            for result in results:
                finding = {
                    'tool': 'semgrep',
                    'rule': result.get('check_id', ''),
                    'file': result.get('path', ''),
                    'line': result.get('start', {}).get('line', 0),
                    'column': result.get('start', {}).get('col', 0),
                    'severity': self._map_severity(result.get('severity', 'medium')),
                    'message': result.get('message', ''),
                    'code': result.get('lines', ''),
                    'cwe': result.get('metadata', {}).get('cwe', ''),
                    'category': result.get('metadata', {}).get('category', '')
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
