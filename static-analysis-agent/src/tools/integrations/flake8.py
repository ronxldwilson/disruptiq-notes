"""
Flake8 integration for Python linting.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..base_tool import BaseTool, AnalysisResult


class Flake8Tool(BaseTool):
    """Flake8 Python linting tool integration."""

    def __init__(self):
        super().__init__(
            name="flake8",
            description="Python style guide enforcement and error detection",
            supported_languages=["python"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install Flake8 using pip."""
        try:
            # Try installing via pip first
            result = await asyncio.create_subprocess_exec(
                'pip', 'install', 'flake8',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                return True

            # If pip fails, try installing via pip3
            result = await asyncio.create_subprocess_exec(
                'pip3', 'install', 'flake8',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            return result.returncode == 0

        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if Flake8 is installed."""
        try:
            result = subprocess.run(
                ['flake8', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run Flake8 on the codebase."""
        config = config or {}
        self.logger.debug(f"Running Flake8 on {codebase_path}")

        cmd = ['flake8']

        # Add custom config if specified
        custom_config = config.get('custom_config_path')
        if custom_config:
            cmd.extend(['--config', str(custom_config)])

        # Add max line length if specified
        max_line_length = config.get('max_line_length')
        if max_line_length:
            cmd.extend(['--max-line-length', str(max_line_length)])

        # Add select rules if specified
        select = config.get('select')
        if select:
            if isinstance(select, list):
                select = ','.join(select)
            cmd.extend(['--select', select])

        # Add ignore rules if specified
        ignore = config.get('ignore')
        if ignore:
            if isinstance(ignore, list):
                ignore = ','.join(ignore)
            cmd.extend(['--ignore', ignore])

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
                errors=[f"Failed to run Flake8: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse Flake8 default output."""
        findings = []
        errors = []

        if error_output.strip():
            errors.append(error_output.strip())

        try:
            if output.strip():
                lines = output.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Format: filename:line:column: code message
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            filename = parts[0]
                            line_num = int(parts[1])
                            column = int(parts[2]) if parts[2].isdigit() else 0
                            code_and_message = parts[3].strip()

                            # Split code and message
                            code_end = code_and_message.find(' ')
                            if code_end > 0:
                                code = code_and_message[:code_end]
                                message = code_and_message[code_end + 1:]
                            else:
                                code = code_and_message
                                message = ""

                            finding_dict = {
                                'tool': 'flake8',
                                'rule': code,
                                'file': filename,
                                'line': line_num,
                                'column': column,
                                'severity': self._map_severity(code),
                                'message': message,
                                'code': '',
                                'cwe': '',
                                'category': 'style'
                            }
                            findings.append(finding_dict)
        except Exception as e:
            errors.append(f"Failed to parse Flake8 output: {str(e)}")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )

    def _map_severity(self, code: str) -> str:
        """Map Flake8 error codes to severity levels."""
        if code.startswith('E'):
            return 'high'  # Syntax errors
        elif code.startswith('F'):
            return 'high'  # Pyflakes errors
        elif code.startswith('W'):
            return 'medium'  # Warnings
        else:
            return 'low'  # Style issues
