"""
SonarQube integration for comprehensive code quality analysis.
"""

import asyncio
import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import tempfile
import os

from ..base_tool import BaseTool, AnalysisResult


class SonarQubeTool(BaseTool):
    """SonarQube code quality analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="sonar",
            description="Comprehensive code quality and security platform",
            supported_languages=["java", "javascript", "typescript", "python", "c#", "c", "cpp", "php", "ruby", "go", "scala", "kotlin", "swift"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install SonarScanner CLI."""
        try:
            # Try installing via different methods
            # First check if already installed
            if self.is_installed():
                return True

            # For Windows, download and install SonarScanner
            import urllib.request
            import zipfile

            # Download SonarScanner CLI
            scanner_url = "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-windows.zip"
            scanner_zip = Path(tempfile.gettempdir()) / "sonar-scanner.zip"
            scanner_dir = Path.home() / ".sonar" / "scanner"

            self.logger.info("Downloading SonarScanner CLI...")
            urllib.request.urlretrieve(scanner_url, scanner_zip)

            # Extract
            with zipfile.ZipFile(scanner_zip, 'r') as zip_ref:
                zip_ref.extractall(scanner_dir.parent)

            # Clean up
            scanner_zip.unlink()

            # Add to PATH (would need to be done system-wide for persistence)
            scanner_bin = scanner_dir / "bin"
            if scanner_bin.exists():
                os.environ['PATH'] = str(scanner_bin) + os.pathsep + os.environ['PATH']

            return self.is_installed()

        except Exception as e:
            self.logger.error(f"Failed to install SonarScanner: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if SonarScanner is installed."""
        try:
            result = subprocess.run(
                ['sonar-scanner', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                encoding='utf-8'
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run SonarQube analysis on the codebase."""
        config = config or {}
        self.logger.debug(f"Running SonarQube on {codebase_path}")

        # Create sonar-project.properties if not exists
        project_props = self._create_sonar_project_properties(codebase_path, config)

        cmd = ['sonar-scanner']

        # Add custom properties
        if config.get('server_url'):
            cmd.extend(['-Dsonar.host.url', config['server_url']])
        if config.get('login'):
            cmd.extend(['-Dsonar.login', config['login']])
        if config.get('project_key'):
            cmd.extend(['-Dsonar.projectKey', config['project_key']])
        if config.get('organization'):
            cmd.extend(['-Dsonar.organization', config['organization']])

        # Add working directory
        cmd.extend(['-Dsonar.projectBaseDir', str(codebase_path)])

        try:
            # Run sonar-scanner
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=codebase_path
            )

            stdout, stderr = await process.communicate()

            # For now, SonarQube doesn't produce structured output directly
            # We would need to query the SonarQube API for results
            # This is a simplified implementation
            return self.parse_output(stdout.decode(), stderr.decode())

        except Exception as e:
            return AnalysisResult(
                tool_name=self.name,
                findings=[],
                errors=[f"Failed to run SonarQube: {str(e)}"]
            )

    def _create_sonar_project_properties(self, codebase_path: Path, config: Dict[str, Any]) -> Path:
        """Create sonar-project.properties file."""
        props_file = codebase_path / "sonar-project.properties"

        if not props_file.exists():
            properties = f"""# SonarQube project configuration
sonar.projectKey={config.get('project_key', 'static-analysis-agent')}
sonar.projectName={config.get('project_name', 'Static Analysis Agent')}
sonar.projectVersion=1.0
sonar.sources=.
sonar.sourceEncoding=UTF-8

# Language-specific settings
sonar.python.version={config.get('python_version', '3.8')}
sonar.java.binaries={config.get('java_binaries', 'target/classes')}

# Exclusions
sonar.exclusions={','.join(config.get('exclusions', ['**/node_modules/**', '**/test/**', '**/tests/**']))}

# Coverage
sonar.python.coverage.reportPaths={config.get('coverage_reports', 'coverage.xml')}
"""

            props_file.write_text(properties)

        return props_file

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse SonarQube output."""
        findings = []
        errors = []

        if error_output.strip():
            # Check for actual errors vs informational messages
            error_lines = [line for line in error_output.split('\n') if line.strip() and not line.startswith('INFO')]
            if error_lines:
                errors.extend(error_lines)

        # Note: SonarQube analysis results are typically viewed in the web UI
        # For automated processing, we would need to use the SonarQube API
        # This is a placeholder for basic execution
        if "ANALYSIS SUCCESSFUL" in output:
            findings.append({
                'tool': 'sonar',
                'rule': 'analysis_complete',
                'file': '',
                'line': 0,
                'column': 0,
                'severity': 'info',
                'message': 'SonarQube analysis completed successfully. Check SonarQube dashboard for detailed results.',
                'code': '',
                'cwe': '',
                'category': 'info'
            })
        elif errors:
            pass  # Errors already captured
        else:
            errors.append("SonarQube analysis may have failed - check logs")

        return AnalysisResult(
            tool_name=self.name,
            findings=findings,
            errors=errors
        )
