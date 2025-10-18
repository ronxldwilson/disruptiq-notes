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

        # Add max line length from config
        max_line_length = config.get('max_line_length', 88)
        cmd.extend(['--max-line-length', str(max_line_length)])

        # Add select rules from config
        select_rules = config.get('select', [])
        if select_rules:
            if isinstance(select_rules, list):
                select_rules = ','.join(select_rules)
            cmd.extend(['--select', select_rules])

        # Add ignore rules from config
        ignore_rules = config.get('ignore', [])
        if ignore_rules:
            if isinstance(ignore_rules, list):
                ignore_rules = ','.join(ignore_rules)
            cmd.extend(['--ignore', ignore_rules])

        # Add max complexity from config
        max_complexity = config.get('max_complexity')
        if max_complexity:
            cmd.extend(['--max-complexity', str(max_complexity)])

        # Add exclude patterns from config
        exclude_patterns = config.get('exclude', [])
        if exclude_patterns:
            if isinstance(exclude_patterns, list):
                exclude_patterns = ','.join(exclude_patterns)
            cmd.extend(['--exclude', exclude_patterns])

        # Add filename patterns from config
        filename_patterns = config.get('filename', [])
        if filename_patterns:
            for pattern in filename_patterns:
                cmd.extend(['--filename', pattern])

        # Add per-file ignores from config
        per_file_ignores = config.get('per_file_ignores', {})
        if per_file_ignores:
            for pattern, ignores in per_file_ignores.items():
                if isinstance(ignores, list):
                    ignores = ','.join(ignores)
                cmd.extend(['--per-file-ignores', f"{pattern}:{ignores}"])

        # Add other options from config
        if config.get('count'):
            cmd.append('--count')
        if config.get('show_source'):
            cmd.append('--show-source')
        if config.get('show_pep8'):
            cmd.append('--show-pep8')

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
