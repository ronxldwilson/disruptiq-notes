"""
ESLint integration for JavaScript and TypeScript linting.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..base_tool import BaseTool, AnalysisResult


class EslintTool(BaseTool):
    """ESLint JavaScript/TypeScript linting tool integration."""

    def __init__(self):
        super().__init__(
            name="eslint",
            description="Pluggable JavaScript and TypeScript linter",
            supported_languages=["javascript", "typescript"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install ESLint using npm."""
        # Check if already installed
        if self.is_installed():
            return True

        try:
            # Try installing via npm
            result = await asyncio.create_subprocess_exec(
                'npm', 'install', '-g', 'eslint',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            return result.returncode == 0

        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if ESLint is installed."""
        try:
            # Try to run eslint --version using shell
            result = subprocess.run(
                'eslint --version',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                encoding='utf-8'
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, UnicodeDecodeError, OSError):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run ESLint on the codebase."""
        config = config or {}
        self.logger.debug(f"Running ESLint on {codebase_path}")

        cmd = ['eslint', '--format=json']

        # Add custom config if specified
        custom_config = config.get('custom_config_path')
        if custom_config:
            cmd.extend(['--config', str(custom_config)])

        # Add extensions for TypeScript
        extensions = config.get('extensions', ['.js', '.jsx', '.ts', '.tsx'])
        if extensions:
            ext_str = ','.join(extensions)
            cmd.extend(['--ext', ext_str])

        # Add ignore patterns if specified
        ignore_patterns = config.get('ignore_patterns', [])
        for pattern in ignore_patterns:
            cmd.extend(['--ignore-pattern', pattern])

        # Add rules if specified
        rules = config.get('rules', {})
        for rule, value in rules.items():
            if isinstance(value, bool):
                cmd.extend(['--rule', f"{rule}: {'error' if value else 'off'}"])
            elif isinstance(value, list):
                cmd.extend(['--rule', f"{rule}: {json.dumps(value)}"])
            else:
                cmd.extend(['--rule', f"{rule}: {value}"])

        # Add codebase path
        cmd.append(str(codebase_path))

        try:
            # Use shell=True to ensure proper PATH
            process = await asyncio.create_subprocess_shell(
                ' '.join(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return self.parse_output(stdout.decode(), stderr.decode())

        except Exception as e:
            return AnalysisResult(
                tool_name=self.name,
                findings=[],
                errors=[f"Failed to run ESLint: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse ESLint JSON output."""
        findings = []
        errors = []

        if error_output.strip():
            errors.append(error_output.strip())

        try:
            if output.strip():
                data = json.loads(output.strip())
                for file_data in data:
                    filename = file_data.get('filePath', '')
                    for message in file_data.get('messages', []):
                        finding_dict = {
                            'tool': 'eslint',
                            'rule': message.get('ruleId', ''),
                            'file': filename,
                            'line': message.get('line', 0),
                            'column': message.get('column', 0),
                            'severity': self._map_severity(message.get('severity', 1)),
                            'message': message.get('message', ''),
                            'code': '',
                            'cwe': '',
                            'category': 'lint'
                        }
                        findings.append(finding_dict)
        except json.JSONDecodeError:
            errors.append("Failed to parse ESLint output as JSON")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )

    def _map_severity(self, severity: int) -> str:
        """Map ESLint severity levels."""
        if severity == 2:
            return 'high'
        elif severity == 1:
            return 'medium'
        else:
            return 'low'
