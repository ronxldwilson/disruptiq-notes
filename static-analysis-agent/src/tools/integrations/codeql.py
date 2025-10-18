"""
CodeQL integration for semantic code analysis and security vulnerability detection.
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import tempfile
import os

from ..base_tool import BaseTool, AnalysisResult


class CodeQLTool(BaseTool):
    """CodeQL semantic code analysis tool integration."""

    def __init__(self):
        super().__init__(
            name="codeql",
            description="Semantic code analysis engine for finding security vulnerabilities",
            supported_languages=["cpp", "csharp", "go", "java", "javascript", "python", "ruby", "swift"]
        )
        self.logger = logging.getLogger(__name__)

    async def install(self) -> bool:
        """Install CodeQL CLI."""
        try:
            # Check if already installed
            if self.is_installed():
                return True

            # For Windows, download CodeQL CLI
            import urllib.request
            import zipfile

            # Download CodeQL CLI
            codeql_url = "https://github.com/github/codeql-cli-binaries/releases/download/v2.15.5/codeql-win64.zip"
            codeql_zip = Path(tempfile.gettempdir()) / "codeql.zip"
            codeql_dir = Path.home() / ".codeql"

            self.logger.info("Downloading CodeQL CLI...")
            urllib.request.urlretrieve(codeql_url, codeql_zip)

            # Extract
            with zipfile.ZipFile(codeql_zip, 'r') as zip_ref:
                zip_ref.extractall(codeql_dir)

            # Clean up
            codeql_zip.unlink()

            # Add to PATH
            codeql_bin = codeql_dir / "codeql"
            if codeql_bin.exists():
                os.environ['PATH'] = str(codeql_bin) + os.pathsep + os.environ['PATH']

            return self.is_installed()

        except Exception as e:
            self.logger.error(f"Failed to install CodeQL: {e}")
            return False

    def is_installed(self) -> bool:
        """Check if CodeQL CLI is installed."""
        try:
            result = subprocess.run(
                ['codeql', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                encoding='utf-8'
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    async def run(self, codebase_path: Path, config: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Run CodeQL analysis on the codebase."""
        config = config or {}
        self.logger.debug(f"Running CodeQL on {codebase_path}")

        # Detect language
        languages = self._detect_languages(codebase_path)
        if not languages:
            return AnalysisResult(
                tool_name=self.name,
                findings=[],
                errors=["No supported languages detected for CodeQL analysis"]
            )

        results = []

        for language in languages:
            try:
                # Create CodeQL database
                db_path = await self._create_database(codebase_path, language, config)

                # Run analysis
                analysis_results = await self._run_analysis(db_path, language, config)

                results.extend(analysis_results)

            except Exception as e:
                results.append({
                    'tool': 'codeql',
                    'rule': 'analysis_error',
                    'file': '',
                    'line': 0,
                    'column': 0,
                    'severity': 'error',
                    'message': f'CodeQL analysis failed for {language}: {str(e)}',
                    'code': '',
                    'cwe': '',
                    'category': 'error'
                })

        return AnalysisResult(
            tool_name=self.name,
            findings=results,
            errors=[]
        )

    def _detect_languages(self, codebase_path: Path) -> List[str]:
        """Detect supported languages in the codebase."""
        language_extensions = {
            'cpp': ['.cpp', '.cc', '.cxx', '.c++', '.hpp', '.hh', '.hxx', '.h++', '.c'],
            'csharp': ['.cs'],
            'go': ['.go'],
            'java': ['.java'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'python': ['.py'],
            'ruby': ['.rb'],
            'swift': ['.swift']
        }

        detected = set()
        for file_path in codebase_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                for lang, exts in language_extensions.items():
                    if ext in exts:
                        detected.add(lang)

        return list(detected)

    async def _create_database(self, codebase_path: Path, language: str, config: Dict[str, Any]) -> Path:
        """Create CodeQL database for the codebase."""
        db_path = Path(tempfile.gettempdir()) / f"codeql-db-{language}"

        cmd = [
            'codeql', 'database', 'create',
            str(db_path),
            f'--language={language}',
            f'--source-root={codebase_path}'
        ]

        # Add threads
        threads = config.get('threads', 4)
        cmd.extend(['--threads', str(threads)])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Failed to create CodeQL database: {stderr.decode()}")

        return db_path

    async def _run_analysis(self, db_path: Path, language: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run CodeQL analysis on the database."""
        findings = []

        # Use built-in security queries
        query_suite = config.get('query_suite', 'security-and-quality')

        cmd = [
            'codeql', 'database', 'analyze',
            str(db_path),
            f'--format=json',
            f'--output={db_path / "results.json"}',
            query_suite
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"CodeQL analysis failed: {stderr.decode()}")

        # Parse results
        results_file = db_path / "results.json"
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for result in data.get('results', []):
                finding = {
                    'tool': 'codeql',
                    'rule': result.get('rule', {}).get('id', ''),
                    'file': result.get('location', {}).get('file', ''),
                    'line': result.get('location', {}).get('startLine', 0),
                    'column': result.get('location', {}).get('startColumn', 0),
                    'severity': self._map_severity(result.get('rule', {}).get('severity', 'medium')),
                    'message': result.get('message', ''),
                    'code': result.get('location', {}).get('snippet', ''),
                    'cwe': result.get('rule', {}).get('cwe', ''),
                    'category': result.get('rule', {}).get('category', 'security')
                }
                findings.append(finding)

        return findings

    def _map_severity(self, codeql_severity: str) -> str:
        """Map CodeQL severity levels."""
        severity_map = {
            'error': 'high',
            'warning': 'medium',
            'note': 'low',
            'info': 'low'
        }
        return severity_map.get(codeql_severity.lower(), 'medium')

    def parse_output(self, output: str, error_output: str) -> AnalysisResult:
        """Parse CodeQL output - placeholder since results are handled in run()."""
        # This method is required by the base class but CodeQL results are parsed in run()
        return AnalysisResult(
            tool_name=self.name,
            findings=[],
            errors=[]
        )
