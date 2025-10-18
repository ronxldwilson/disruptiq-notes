"""
Cppcheck integration for C/C++ static analysis.
"""

import asyncio
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from ..base_tool import BaseTool, AnalysisResult


class CppcheckTool(BaseTool):
    """Cppcheck C/C++ static analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="cppcheck",
            description="Static analysis tool for C/C++ code",
            supported_languages=["c", "cpp"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install Cppcheck using package manager or from source."""
        # Check if already installed
        if self.is_installed():
            return True

        try:
            # Try installing via apt (Linux)
            result = await asyncio.create_subprocess_exec(
                'apt-get', 'update',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                result = await asyncio.create_subprocess_exec(
                    'apt-get', 'install', '-y', 'cppcheck',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await result.wait()
                if result.returncode == 0:
                    return True

            # Try installing via brew (macOS)
            result = await asyncio.create_subprocess_exec(
                'brew', 'install', 'cppcheck',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                return True

            # Try installing via choco (Windows)
            result = await asyncio.create_subprocess_exec(
                'choco', 'install', 'cppcheck', '-y',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                return True

            # Try winget (Windows)
            result = await asyncio.create_subprocess_exec(
                'winget', 'install', 'Cppcheck.Cppcheck',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()

            if result.returncode == 0:
                return True

            # Manual installation instructions
            print("Cppcheck could not be installed automatically.")
            print("Please install manually:")
            print("- Windows: Download from https://cppcheck.sourceforge.net/")
            print("- Linux: sudo apt install cppcheck")
            print("- macOS: brew install cppcheck")
            return False

        except Exception as e:
            print(f"Installation failed: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if Cppcheck is installed."""
        try:
            result = subprocess.run(
                ['cppcheck', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                encoding='utf-8'
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, UnicodeDecodeError):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run Cppcheck on the codebase."""
        config = config or {}
        self.logger.debug(f"Running Cppcheck on {codebase_path}")

        cmd = ['cppcheck', '--xml', '--xml-version=2']

        # Add enable checks if specified
        enable = config.get('enable', 'all')
        cmd.extend(['--enable', enable])

        # Add language if specified
        language = config.get('language')
        if language:
            cmd.extend(['--language', language])

        # Add include paths if specified
        includes = config.get('includes', [])
        for include_path in includes:
            cmd.extend(['-I', str(include_path)])

        # Add defines if specified
        defines = config.get('defines', [])
        for define in defines:
            cmd.extend(['-D', define])

        # Add suppressed checks if specified
        suppress = config.get('suppress', [])
        for suppression in suppress:
            cmd.extend(['--suppress', suppression])

        # Add platform if specified
        platform = config.get('platform')
        if platform:
            cmd.extend(['--platform', platform])

        # Add std if specified
        std = config.get('std')
        if std:
            cmd.extend(['--std', std])

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
                errors=[f"Failed to run Cppcheck: {str(e)}"]
            )

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse Cppcheck XML output."""
        findings = []
        errors = []

        if error_output.strip():
            errors.append(error_output.strip())

        try:
            if output.strip():
                root = ET.fromstring(output)
                for error in root.findall('.//error'):
                    for location in error.findall('location'):
                        finding_dict = {
                            'tool': 'cppcheck',
                            'rule': error.get('id', ''),
                            'file': location.get('file', ''),
                            'line': int(location.get('line', 0)),
                            'column': 0,
                            'severity': self._map_severity(error.get('severity', 'medium')),
                            'message': error.get('msg', ''),
                            'code': error.get('verbose', ''),
                            'cwe': '',
                            'category': 'static-analysis'
                        }
                        findings.append(finding_dict)
        except ET.ParseError:
            errors.append("Failed to parse Cppcheck output as XML")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )

    def _map_severity(self, cppcheck_severity: str) -> str:
        """Map Cppcheck severity levels."""
        severity_map = {
            'error': 'high',
            'warning': 'medium',
            'style': 'low',
            'performance': 'medium',
            'portability': 'low',
            'information': 'low'
        }
        return severity_map.get(cppcheck_severity.lower(), 'medium')
