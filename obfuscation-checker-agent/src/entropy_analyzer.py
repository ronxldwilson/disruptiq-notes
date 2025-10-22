import re
from collections import Counter
import math
from pathlib import Path
from typing import List

from findings import Finding

class EntropyAnalyzer:
    def __init__(self, config, common_words=None):
        self.config = config
        self.common_words = common_words or set()

    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0

        char_counts = Counter(text)
        text_length = len(text)
        entropy = 0.0

        for count in char_counts.values():
            probability = count / text_length
            entropy -= probability * math.log2(probability)

        return entropy

    def detect_high_entropy_strings(self, lines: List[str]) -> List[Finding]:
        """Detect strings with high entropy (potential encoded data)."""
        findings = []
        high_entropy_threshold = 4.5  # Typical for base64/encrypted data

        for line_num, line in enumerate(lines, 1):
            # Find string literals
            strings = re.findall(r'["\']([^"\']+)["\']', line)
            for string in strings:
                if len(string) > 20:  # Only check longer strings
                    entropy = self.calculate_entropy(string)
                    if entropy > high_entropy_threshold:
                        findings.append(Finding(
                            file_path="",  # Will be set by caller
                            line_number=line_num,
                            obfuscation_type="high_entropy_string",
                            description=f"Found a string with very high information entropy ({entropy:.2f} bits per character), which is unusual for human-readable text. Normal English text has entropy around 2.5-3.5, while compressed or encrypted data can reach 5.0+. This suggests the string contains encoded, compressed, or encrypted content that appears random to hide its true meaning. Malware commonly uses such techniques to conceal command strings, URLs, or executable code from casual inspection.",
                            severity="medium",
                            evidence=string[:50] + "..." if len(string) > 50 else string,
                            confidence=min(1.0, entropy / 6.0),  # Normalize confidence
                            full_line=line,
                            category="string_obfuscation"
                        ))

        return findings

    def analyze_variable_names(self, lines: List[str]) -> List[Finding]:
        """Analyze variable names for obfuscation patterns."""
        findings = []

        # Extract variable names using regex patterns
        var_patterns = [
            # Python/JavaScript style: var x =, let x =, const x =, x =
            r'\b(?:var|let|const|def|function)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[=:]',
            # Function parameters: function(x, y) or def func(x, y)
            r'\b(?:function|def)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*([^)]*)\s*\)',
            # Class properties: this.x, self.x
            r'\b(?:this|self)\.([a-zA-Z_][a-zA-Z0-9_]*)',
            # Variable assignments: x = value, x += value, etc.
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*[+\-*/]?=',
        ]

        # Skip JavaScript keywords and common constructs
        skip_words = {
            'debugger', 'console', 'clear', 'log', 'error', 'warn', 'info',
            'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default',
            'try', 'catch', 'finally', 'throw', 'return', 'break', 'continue',
            'function', 'var', 'let', 'const', 'class', 'extends', 'super',
            'this', 'self', 'new', 'delete', 'typeof', 'instanceof', 'in',
            'true', 'false', 'null', 'undefined', 'NaN', 'Infinity',
            # Additional JavaScript statements and common legitimate names
            'alert', 'prompt', 'confirm', 'eval', 'parseInt', 'parseFloat',
            'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
            'addEventListener', 'removeEventListener', 'getElementById',
            'querySelector', 'innerHTML', 'textContent', 'style', 'className',
            'document', 'window', 'location', 'navigator', 'Date', 'Array',
            'Object', 'String', 'Number', 'Boolean', 'Math', 'RegExp',
            'JSON', 'Promise', 'async', 'await', 'yield', 'import', 'export',
            'require', 'module', 'exports', 'global', 'process', 'Buffer'
        }

        all_vars = set()
        for line_num, line in enumerate(lines, 1):
            for pattern in var_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    # Handle function parameters (comma-separated)
                    if ',' in match:
                        params = [p.strip() for p in match.split(',')]
                        for param in params:
                            param = param.split('=')[0].strip()  # Remove default values
                            if param and param not in ['self', 'cls', 'this'] and param not in skip_words:
                                all_vars.add((param, line_num))
                    else:
                        if match and match not in ['self', 'cls', 'this'] and match not in skip_words:
                            all_vars.add((match, line_num))

        # Analyze each unique variable
        analyzed_vars = set()
        for var_name, line_num in all_vars:
            if var_name in analyzed_vars:
                continue
            analyzed_vars.add(var_name)

            # Skip common legitimate words
            if var_name.lower() in self.common_words:
                continue

            # Check for obfuscation patterns
            if len(var_name) == 1:
                # Single character variable
                findings.append(Finding(
                    file_path="",  # Will be set by caller
                    line_number=line_num,
                    obfuscation_type="single_char_vars",
                    description="Found single-letter variable names like 'a', 'b', 'x'. While sometimes acceptable for simple counters or math variables, this pattern is commonly used in obfuscated code to make it harder to understand the program's logic and purpose.",
                    severity="low",
                    evidence=var_name,
                    confidence=0.7,
                    full_line=lines[line_num - 1] if line_num <= len(lines) else "",
                    category="variable_obfuscation"
                ))
            elif len(var_name) <= 3:
                # Short meaningless variables
                findings.append(Finding(
                    file_path="",  # Will be set by caller
                    line_number=line_num,
                    obfuscation_type="short_meaningless_vars",
                    description="Detected very short variable names (1-3 characters) that don't convey meaning. Legitimate code usually uses descriptive names that explain what the variable represents, making code self-documenting and easier to maintain.",
                    severity="low",
                    evidence=var_name,
                    confidence=0.6,
                    full_line=lines[line_num - 1] if line_num <= len(lines) else "",
                    category="variable_obfuscation"
                ))
            elif re.match(r'^[a-zA-Z]{1,2}\d+$', var_name):
                # Variables like a1, x2, b10
                findings.append(Finding(
                    file_path="",  # Will be set by caller
                    line_number=line_num,
                    obfuscation_type="obfuscated_vars",
                    description="Identified variable names combining short letters with numbers (like 'a1', 'x2', 'b10'). This naming pattern is characteristic of code that has been automatically minified or obfuscated, making it difficult for humans to understand variable purposes and relationships.",
                    severity="low",
                    evidence=var_name,
                    confidence=0.8,
                    full_line=lines[line_num - 1] if line_num <= len(lines) else "",
                    category="variable_obfuscation"
                ))
            elif 4 <= len(var_name) <= 10 and not any(c.isupper() for c in var_name) and var_name.isalnum():
                # Potentially random looking variables
                entropy = self.calculate_entropy(var_name)
                if entropy > 3.0:  # High entropy for variable name
                    findings.append(Finding(
                        file_path="",  # Will be set by caller
                        line_number=line_num,
                        obfuscation_type="random_vars",
                        description=f"Found seemingly random variable names that appear computer-generated rather than human-chosen. Variable '{var_name}' has high entropy ({entropy:.2f}), suggesting the code may have been processed through an obfuscation tool.",
                        severity="medium",
                        evidence=var_name,
                        confidence=min(0.9, entropy / 4.0),
                        full_line=lines[line_num - 1] if line_num <= len(lines) else "",
                        category="variable_obfuscation"
                    ))

        return findings
