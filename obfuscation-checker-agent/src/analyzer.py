import concurrent.futures
import re
from pathlib import Path
from typing import List

from patterns import ObfuscationPatterns
from entropy_analyzer import EntropyAnalyzer
from ast_analyzer import ASTAnalyzer
from file_structure_analyzer import FileStructureAnalyzer
from findings import Finding

class Analyzer:
    def __init__(self, config):
        self.config = config
        self.patterns_obj = ObfuscationPatterns()
        self.patterns = self.patterns_obj.get_patterns()
        self.common_words = self.patterns_obj.common_words
        self.entropy_analyzer = EntropyAnalyzer(config, self.common_words)
        self.ast_analyzer = ASTAnalyzer(config)
        self.structure_analyzer = FileStructureAnalyzer(config)

        # Define file types for pattern filtering
        self.code_extensions = {
            '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.c', '.cpp', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj',
            '.hs', '.ml', '.fs', '.elm', '.dart', '.lua', '.r', '.m', '.mm'
        }
        self.config_extensions = {
            '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.cfg', '.conf',
            '.properties', '.env', '.md', '.txt', '.lock', '.editorconfig',
            '.npmrc', '.yarnrc', '.gitignore', '.prettierignore', '.eslintignore',
            '.eslintcache', '.mdc', '.snaplet', '.cursor'
        }

    def _ensure_patterns_compiled(self):
        """Ensure patterns are compiled (call this in child processes)."""
        for pattern_name, pattern_info in self.patterns.items():
            if "compiled" not in pattern_info:
                pattern_info["compiled"] = re.compile(pattern_info["pattern"])

    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a source code file that should have variable patterns applied."""
        return file_path.suffix.lower() in self.code_extensions

    def _is_config_file(self, file_path: Path) -> bool:
        """Check if file is a configuration/data file."""
        return file_path.suffix.lower() in self.config_extensions

    def _is_css_class_line(self, line: str) -> bool:
        """Check if a line appears to be CSS class declarations or Tailwind usage."""
        line = line.strip()

        # Skip CSS class attributes
        if 'class=' in line or 'className=' in line:
            return True

        # Skip Tailwind class arrays
        if '[' in line and ']' in line and any(indicator in line for indicator in ['className', 'clsx', 'cn(', 'twMerge']):
            return True

        # Skip lines with multiple CSS/Tailwind classes
        css_classes = ['flex', 'grid', 'block', 'inline', 'hidden', 'justify-', 'items-', 'bg-', 'text-', 'border-', 'rounded', 'shadow', 'p-', 'm-', 'w-', 'h-']
        if any(cls in line for cls in css_classes):
            # Check if it looks like a class list
            if ',' in line or ' ' in line.strip() or '"' in line or "'" in line:
                return True

        return False

    def analyze_file(self, file_path: Path) -> List[dict]:
        """Analyze a single file for obfuscation patterns."""
        findings = []

        # Ensure patterns are compiled (important for child processes)
        self._ensure_patterns_compiled()

        # Skip very large files to prevent memory issues
        max_file_size = 50 * 1024 * 1024  # 50MB limit
        try:
            file_size = file_path.stat().st_size
            if file_size > max_file_size:
                findings.append(Finding(
                    file_path=str(file_path),
                    line_number=0,
                    obfuscation_type="file_too_large",
                    description=f"File is too large ({file_size/1024/1024:.1f}MB) to analyze efficiently. Skipped to prevent memory issues.",
                    severity="info",
                    evidence=f"Size: {file_size} bytes",
                    confidence=1.0,
                    full_line="",
                    category="performance"
                ).to_dict())
                return findings
        except OSError:
            pass  # Continue with analysis if we can't get file size

        try:
            # Use streaming approach for large files
            if file_path.stat().st_size > 1024 * 1024:  # > 1MB
                return self._analyze_file_streaming(file_path)
            else:
                # For smaller files, keep the original approach
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.splitlines()
                    return self._analyze_file_content(file_path, content, lines)
        except Exception as e:
            # Skip files that can't be read
            return findings

    def _analyze_file_streaming(self, file_path: Path) -> List[Finding]:
        """Analyze large files using streaming approach to save memory."""
        findings = []

        try:
            # For streaming analysis, we'll do line-by-line processing
            # This skips some advanced analysis that requires full file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_num = 0
                lines_sample = []  # Keep a small sample for structural analysis

                for line in f:
                    line_num += 1
                    line = line.rstrip('\n\r')

                    # Keep sample of lines for analysis that needs context
                    if len(lines_sample) < 1000:  # Limit sample size
                        lines_sample.append(line)

                    # Skip lines that are clearly CSS/Tailwind class declarations
                    if self._is_css_class_line(line):
                        continue

                    # Regex pattern matching (streaming version)
                    for pattern_name, pattern_info in self.patterns.items():
                        # Skip variable-related patterns for config files
                        if pattern_name in ["random_vars", "short_meaningless_vars", "single_char_vars", "obfuscated_vars"] and self._is_config_file(file_path):
                            continue
                        # Skip computed property access for config files (JSON arrays/objects are not obfuscated)
                        if pattern_name == "computed_property_access" and self._is_config_file(file_path):
                            continue

                        matches = pattern_info["compiled"].findall(line)
                        if matches:
                            # Filter matches (simplified for streaming)
                            filtered_matches = []
                            for match in matches:
                                # Skip common legitimate words for variable-related patterns
                                if pattern_name in ["random_vars", "short_meaningless_vars", "single_char_vars", "obfuscated_vars"] and match.lower() in self.common_words:
                                    continue
                            # Skip base64 in package-lock.json integrity fields
                                if pattern_name in ["base64_strings", "encoded_urls"] and file_path.name == "package-lock.json" and "integrity" in line:
                                    continue
                            filtered_matches.append(match)

                            if filtered_matches:
                                first_match = filtered_matches[0]
                                evidence = first_match[:100] if len(first_match) > 100 else first_match
                                if len(filtered_matches) > 1:
                                    evidence = f"{evidence} (+{len(filtered_matches)-1} more)"
                                    confidence = min(0.9, 0.8 + 0.05 * len(filtered_matches))
                                else:
                                    confidence = 0.8

                                finding = Finding(
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    obfuscation_type=pattern_name,
                                    description=pattern_info["description"],
                                    severity=pattern_info["severity"],
                                    evidence=evidence,
                                    confidence=confidence,
                                    full_line=line,
                                    category=pattern_info.get("category", "unknown")
                                )
                                findings.append(finding.to_dict())

                # Do basic structural analysis on the sample
                if lines_sample:
                    structural_findings = self.structure_analyzer.check_file_structure(file_path, lines_sample)
                    findings.extend([f.to_dict() for f in structural_findings])

                    # Note: Skipping advanced analysis (AST, entropy, variable names) for large files
                    # to maintain performance. Could be added back with careful memory management if needed.

        except Exception as e:
            # Skip files that can't be read
            pass

        return findings

    def _analyze_file_content(self, file_path: Path, content: str, lines: List[str]) -> List[Finding]:
        """Analyze file content (original full analysis for smaller files)."""
        findings = []

        # Regex pattern matching
        for line_num, line in enumerate(lines, 1):
            # Skip lines that are clearly CSS/Tailwind class declarations
            if self._is_css_class_line(line):
                continue

            for pattern_name, pattern_info in self.patterns.items():
                # Skip variable-related patterns for config files
                if pattern_name in ["random_vars", "short_meaningless_vars", "single_char_vars", "obfuscated_vars"] and self._is_config_file(file_path):
                    continue
                # Skip computed property access for config files (JSON arrays/objects are not obfuscated)
                if pattern_name == "computed_property_access" and self._is_config_file(file_path):
                    continue

                matches = pattern_info["compiled"].findall(line)
                if matches:
                    # Filter matches
                    filtered_matches = []
                    for match in matches:
                        # Skip common legitimate words for variable-related patterns
                        if pattern_name in ["random_vars", "short_meaningless_vars", "single_char_vars", "obfuscated_vars"] and match.lower() in self.common_words:
                            continue
                        # Skip TypeScript interface properties and object destructuring
                        if pattern_name in ["random_vars", "short_meaningless_vars"]:
                            # Skip interface properties (name: type;)
                            if ":" in line and ";" in line:
                                line_stripped = line.strip()
                                if not line_stripped.startswith(('if ', 'for ', 'while ', 'const ', 'let ', 'var ', 'function ')) and ': ' in line and line_stripped.endswith(';'):
                                    continue
                            # Skip destructuring assignments ({ prop } = obj or function params ({ prop }: Type)
                            if "{" in line and "}" in line and (": " in line or "=" in line or "(" in line):
                                continue
                        # Skip base64 in package-lock.json integrity fields
                        if pattern_name in ["base64_strings", "encoded_urls"] and file_path.name == "package-lock.json" and "integrity" in line:
                            continue
                        # Skip CSS class-like patterns in arrays/objects (common in React/Tailwind)
                        if pattern_name in ["random_vars", "short_meaningless_vars"] and ("className" in line or "class=" in line or "[" in line and "]" in line):
                            # Check if this looks like CSS class usage
                            if any(css_indicator in line for css_indicator in ["className", "class=", "styles", "tailwind", "clsx", "cn("]):
                                continue
                        filtered_matches.append(match)

                    if filtered_matches:
                        # Only create one finding per pattern per line to avoid spam
                        # Use the first match as evidence, or count if multiple
                        first_match = filtered_matches[0]
                        evidence = first_match[:100] if len(first_match) > 100 else first_match
                        if len(filtered_matches) > 1:
                            evidence = f"{evidence} (+{len(filtered_matches)-1} more)"
                            # Slightly increase confidence for multiple matches
                            confidence = min(0.9, 0.8 + 0.05 * len(filtered_matches))
                        else:
                            confidence = 0.8

                        finding_dict = {
                            "file_path": str(file_path),
                            "line_number": line_num,
                            "obfuscation_type": pattern_name,
                            "description": pattern_info["description"],
                            "severity": pattern_info["severity"],
                            "evidence": evidence,
                            "confidence": confidence,
                            "full_line": line,
                            "category": pattern_info.get("category", "unknown")
                        }
                        findings.append(finding_dict)

        # Advanced analysis - run independent checks in parallel
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
                futures = [
                    executor.submit(self.entropy_analyzer.detect_high_entropy_strings, lines),
                    executor.submit(self.entropy_analyzer.analyze_variable_names, lines),
                    executor.submit(self.structure_analyzer.check_file_structure, file_path, lines)
                ]

                # Language-specific analysis (conditional)
                if file_path.suffix == '.py':
                    futures.append(executor.submit(self.ast_analyzer.analyze_python_ast, file_path, content, lines))

                for future in concurrent.futures.as_completed(futures):
                    try:
                        adv_findings = future.result()
                        for finding in adv_findings:
                            finding_dict = {
                                "file_path": str(file_path),
                                "line_number": finding.line_number,
                                "obfuscation_type": finding.obfuscation_type,
                                "description": finding.description,
                                "severity": finding.severity,
                                "evidence": finding.evidence,
                                "confidence": finding.confidence,
                                "full_line": finding.full_line,
                                "category": finding.category
                            }
                            findings.append(finding_dict)
                    except Exception as e:
                        if self.config.get('verbose', False):
                            print(f"Error in advanced analysis: {e}")
        except Exception as e:
            if self.config.get('verbose', False):
                print(f"Error setting up advanced analysis: {e}")

        return findings
