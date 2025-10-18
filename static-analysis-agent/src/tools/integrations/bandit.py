"""
Bandit integration for Python security analysis.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..base_tool import BaseTool, AnalysisResult


class BanditTool(BaseTool):
    """Bandit Python security analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="bandit",
            description="Security linter for Python code",
            supported_languages=["python"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install Bandit using pip."""
        try:
            # Try installing via pip first
            result = await asyncio.create_subprocess_exec(
                'pip', 'install', 'bandit[toml]',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                return True

            # If pip fails, try installing via pip3
            result = await asyncio.create_subprocess_exec(
                'pip3', 'install', 'bandit[toml]',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            return result.returncode == 0

        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if Bandit is installed."""
        try:
            result = subprocess.run(
                ['bandit', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run Bandit on the codebase."""
        config = config or {}
        self.logger.debug(f"Running Bandit on {codebase_path}")

        cmd = ['bandit', '-f', 'json']

        # Add severity levels from config
        severity_levels = config.get('severity', ['high', 'medium', 'low'])
        if severity_levels:
            for level in severity_levels:
                cmd.extend(['--severity', level])

        # Add confidence levels from config
        confidence_levels = config.get('confidence', ['high', 'medium', 'low'])
        if confidence_levels:
            for level in confidence_levels:
                cmd.extend(['--confidence', level])

        # Add excluded paths from config
        excluded_paths = config.get('excluded_paths', [])
        for path in excluded_paths:
            cmd.extend(['--exclude', path])

        # Add specific tests from config
        tests = config.get('tests', [])
        if tests:
            if isinstance(tests, list):
                tests = ','.join(tests)
            cmd.extend(['--tests', tests])

        # Add skipped tests from config
        skips = config.get('skips', [])
        if skips:
            if isinstance(skips, list):
                skips = ','.join(skips)
            cmd.extend(['--skips', skips])

        # Add baseline file if specified
        baseline = config.get('baseline')
        if baseline:
            cmd.extend(['--baseline', str(baseline)])

        # Add processes if specified
        processes = config.get('options', {}).get('processes', 1)
        if processes > 1:
            cmd.extend(['--processes', str(processes)])

        # Add recursive flag
        recursive = config.get('options', {}).get('recursive', True)
        if recursive:
            cmd.append('-r')

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
                errors=[f"Failed to run Bandit: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse Bandit JSON output."""
        findings = []
        errors = []

        if error_output.strip():
            errors.append(error_output.strip())

        try:
            if output.strip():
                # Bandit outputs INFO messages before JSON, find the JSON part
                json_start = output.find('{')
                if json_start != -1:
                    json_content = output[json_start:]
                    data = json.loads(json_content)

                    for result in data.get('results', []):
                        filename = result.get('filename', '').replace('.\\', '')  # Clean Windows path
                        finding_dict = {
                            'tool': 'bandit',
                            'rule': result.get('test_id', ''),
                            'file': filename,
                            'line': result.get('line_number', 0),
                            'column': result.get('col_offset', 0),
                            'severity': self._map_severity(result.get('issue_severity', 'medium')),
                            'message': result.get('issue_text', ''),
                            'code': result.get('code', ''),
                            'cwe': result.get('issue_cwe', {}).get('id', ''),
                            'category': 'security'
                        }
                        findings.append(finding_dict)

                    # Add any errors from bandit
                    for error in data.get('errors', []):
                        errors.append(str(error))
        except json.JSONDecodeError:
            errors.append("Failed to parse Bandit output as JSON")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )

    def _map_severity(self, bandit_severity: str) -> str:
        """Map Bandit severity levels."""
        severity_map = {
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }
        return severity_map.get(bandit_severity.lower(), 'medium')
