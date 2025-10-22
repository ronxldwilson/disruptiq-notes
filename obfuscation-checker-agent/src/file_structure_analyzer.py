import re
from pathlib import Path
from typing import List

from findings import Finding

class FileStructureAnalyzer:
    def __init__(self, config):
        self.config = config

    def check_file_structure(self, file_path: Path, lines: List[str]) -> List[Finding]:
        """Check for file-level obfuscation indicators."""
        findings = []
        total_lines = len(lines)
        total_chars = sum(len(line) for line in lines)

        # Calculate metrics
        avg_line_length = total_chars / total_lines if total_lines > 0 else 0
        max_line_length = max(len(line) for line in lines) if lines else 0
        empty_lines = sum(1 for line in lines if line.strip() == "")
        empty_ratio = empty_lines / total_lines if total_lines > 0 else 0

        # Check for minified files (few lines, many chars per line)
        if total_lines < 10 and total_chars > 5000:
            finding = Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="minified_file",
                description=f"This file appears to be minified - it contains only {total_lines} lines but {total_chars} total characters, averaging {avg_line_length:.1f} characters per line. Minification is a legitimate optimization technique that removes whitespace, shortens names, and compresses code for production use. However, when found in source repositories or during development, it may indicate attempts to hide code logic or bypass code review processes.",
                severity="high",
                evidence=f"{total_lines} lines, {total_chars} chars, avg {avg_line_length:.1f} chars/line",
                confidence=0.9,
                full_line="",
                category="structure_obfuscation"
            )
            findings.append(finding)

        # Check for extremely long lines (minification indicator)
        if max_line_length > 1000:
            finding = Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="extremely_long_lines",
                description=f"This file contains extremely long lines, with the longest being {max_line_length} characters (average {avg_line_length:.1f}). While some languages allow long lines, this extreme length often results from code minification or obfuscation processes that remove all whitespace and line breaks. Such formatting makes the code nearly impossible to read and debug, suggesting it may have been processed through automated tools to hide its structure.",
                severity="medium",
                evidence=f"Max line length: {max_line_length}, Avg: {avg_line_length:.1f}",
                confidence=0.8,
                full_line="",
                category="structure_obfuscation"
            )
            findings.append(finding)

        # Check for no whitespace (extreme minification)
        if empty_ratio < 0.05 and total_lines > 20:  # Less than 5% empty lines
            finding = Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="no_whitespace",
                description=f"This file has virtually no whitespace formatting - only {empty_ratio:.2f} of lines are empty or whitespace-only in a {total_lines}-line file. Normal code uses whitespace for readability, with blank lines separating logical sections and indentation showing code structure. The complete absence of formatting suggests aggressive minification or deliberate obfuscation to make the code as compact and unreadable as possible.",
                severity="high",
                evidence=f"Empty line ratio: {empty_ratio:.2f}, Total lines: {total_lines}",
                confidence=0.9,
                full_line="",
                category="structure_obfuscation"
            )
            findings.append(finding)

        # Check for no comments (potential removal)
        comment_patterns = {
            ".js": r'//|/\\*|\\*/',
            ".py": r'#',
            ".java": r'//|/\\*|\\*/',
            ".cpp": r'//|/\\*|\\*/',
            ".c": r'//|/\\*|\\*/',
            ".cs": r'//|/\\*|\\*/'
        }
        ext = file_path.suffix.lower()
        if ext in comment_patterns and total_lines > 20:
            has_comments = any(re.search(comment_patterns[ext], line) for line in lines)
            if not has_comments:
                confidence = 0.8 if total_lines > 100 else 0.6  # Higher confidence for larger files
                finding = Finding(
                    file_path=str(file_path),
                    line_number=0,
                    obfuscation_type="no_comments",
                    description=f"This {total_lines}-line file contains absolutely no comments, despite being substantial enough to benefit from documentation. Well-written code typically includes comments to explain complex logic, API usage, and business rules. The complete absence of comments in a file of this size strongly suggests it has been deliberately stripped of all human-readable documentation, either through aggressive minification or intentional obfuscation to make the code harder to understand and maintain.",
                    severity="medium",
                    evidence=f"No {comment_patterns[ext]} patterns found in {total_lines} lines",
                    confidence=confidence,
                    full_line="",
                    category="structure_obfuscation"
                )
                findings.append(finding)

        # Check for unusual file structure (single very long line)
        if total_lines == 1 and total_chars > 1000:
            finding = Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="single_line_file",
                description=f"This file consists entirely of a single massive line containing {total_chars} characters with no line breaks whatsoever. While some data files or highly compressed code might legitimately be single-line, this extreme formatting in a code file suggests it has been aggressively minified or obfuscated. The lack of any line structure makes it virtually impossible to read, debug, or maintain - classic signs of code that has been processed to hide its functionality.",
                severity="high",
                evidence=f"1 line, {total_chars} characters",
                confidence=0.95,
                full_line="",
                category="structure_obfuscation"
            )
            findings.append(finding)

        # Check for packed/encrypted file indicators (very high character density)
        if avg_line_length > 200 and total_lines > 50:
            finding = Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="high_density_code",
                description=f"This file exhibits unusually high code density with an average of {avg_line_length:.1f} characters per line across {total_lines} lines. Normal source code files have averages around 30-80 characters per line due to proper formatting, indentation, and spacing. This extreme density suggests the code has been heavily compressed or packed, potentially to conceal malicious payloads or to bypass size-based security filters. Such dense formatting makes the code extremely difficult to analyze or review.",
                severity="medium",
                evidence=f"Average line length: {avg_line_length:.1f}, Total lines: {total_lines}",
                confidence=0.7,
                full_line="",
                category="structure_obfuscation"
            )
            findings.append(finding)

        return findings
