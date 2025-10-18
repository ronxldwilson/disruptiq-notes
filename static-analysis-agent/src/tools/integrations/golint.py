"""
Golint integration for Go code linting.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..base_tool import BaseTool, AnalysisResult


class GolintTool(BaseTool):
    """Golint Go code linting tool integration."""

    def __init__(self):
        super().__init__(
            name="golint",
            description="Linter for Go source code",
            supported_languages=["go"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install Golint using go get."""
        try:
            result = await asyncio.create_subprocess_exec(
                'go', 'install', 'golang.org/x/lint/golint@latest',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            return result.returncode == 0

        except Exception:
            return False

    def is_installed(self) -> bool:
        """Check if Golint is installed."""
        try:
            result = subprocess.run(
                ['golint', '-h'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run Golint on the codebase."""
        config = config or {}
        self.logger.debug(f"Running Golint on {codebase_path}")

        # Find Go files
        go_files = []
        for file_path in codebase_path.rglob('*.go'):
            go_files.append(str(file_path))

        if not go_files:
            return AnalysisResult(
                tool_name=self.name,
                findings=[],
                errors=[]
            )

        cmd = ['golint']

        # Add set_exit_status if specified
        set_exit_status = config.get('set_exit_status', False)
        if set_exit_status:
            cmd.append('-set_exit_status')

        # Add min_confidence if specified
        min_confidence = config.get('min_confidence')
        if min_confidence:
            cmd.extend(['-min_confidence', str(min_confidence)])

        # Add Go files
        cmd.extend(go_files)

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
                errors=[f"Failed to run Golint: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse Golint output."""
        findings = []
        errors = []

        if error_output.strip():
            errors.append(error_output.strip())

        try:
            if output.strip():
                lines = output.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            filename = parts[0]
                            line_num = int(parts[1])
                            column = int(parts[2]) if parts[2].isdigit() else 0
                            message = parts[3].strip()

                            finding_dict = {
                                'tool': 'golint',
                                'rule': 'golint',
                                'file': filename,
                                'line': line_num,
                                'column': column,
                                'severity': 'low',
                                'message': message,
                                'code': '',
                                'cwe': '',
                                'category': 'style'
                            }
                            findings.append(finding_dict)
        except Exception as e:
            errors.append(f"Failed to parse Golint output: {str(e)}")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )
