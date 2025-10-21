import ast
import concurrent.futures
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter

class Finding:
    def __init__(self, file_path: str, line_number: int, obfuscation_type: str, description: str, severity: str, evidence: str, confidence: float = 1.0, full_line: str = "", category: str = "", id: int = None):
        self.file_path = file_path
        self.line_number = line_number
        self.obfuscation_type = obfuscation_type
        self.description = description
        self.severity = severity
        self.evidence = evidence
        self.confidence = confidence
        self.full_line = full_line
        self.category = category
        self.id = id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "obfuscation_type": self.obfuscation_type,
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "full_line": self.full_line,
            "category": self.category
        }

class Analyzer:
    def __init__(self, config):
        self.config = config
        self.patterns = self.define_patterns()

    def define_patterns(self) -> Dict[str, Dict]:
        """Define regex patterns for detecting obfuscation."""

        # Common legitimate words/properties to exclude from random_vars detection
        self.common_words = {
        # Basic CSS properties
        'background', 'foreground', 'color', 'family', 'scheme', 'width', 'height',
        'className', 'href', 'target', 'rel', 'src', 'alt', 'type', 'name', 'value',
        'style', 'props', 'state', 'config', 'plugins', 'rules', 'theme', 'mode',
        'path', 'types', 'NOTE', 'https', 'compat', 'ignores', 'nextConfig',

        # Typography
        'sans', 'mono', 'serif', 'text', 'font', 'size', 'weight', 'leading', 'tracking',
        'uppercase', 'lowercase', 'capitalize', 'truncate', 'antialiased', 'subpixel',

        # Spacing and sizing
        'margin', 'padding', 'border', 'radius', 'shadow', 'opacity', 'space', 'gap',
        'px', 'rem', 'em', 'full', 'half', 'screen', 'min', 'max', 'fit', 'auto',

        # Layout
        'display', 'position', 'flex', 'grid', 'table', 'flow', 'inline', 'block',
        'hidden', 'visible', 'absolute', 'relative', 'fixed', 'static', 'sticky',
        'container', 'box', 'content', 'items', 'self', 'order', 'basis',

        # Positioning
        'top', 'right', 'bottom', 'left', 'inset', 'center', 'start', 'end',
        'justify', 'align', 'place', 'direction', 'wrap', 'nowrap', 'reverse',

        # Colors and backgrounds
        'bg', 'text', 'border', 'ring', 'divide', 'outline', 'decoration',
        'blue', 'red', 'green', 'yellow', 'purple', 'pink', 'indigo', 'gray', 'black', 'white',
        'slate', 'zinc', 'neutral', 'stone', 'orange', 'amber', 'lime', 'emerald', 'teal', 'cyan', 'sky',
        'violet', 'fuchsia', 'rose', 'transparent', 'current',

        # Effects and transforms
        'blur', 'brightness', 'contrast', 'grayscale', 'invert', 'sepia', 'saturate', 'hue',
        'rotate', 'scale', 'translate', 'skew', 'transform', 'origin', 'perspective',
        'backdrop', 'filter', 'mix', 'isolation', 'will', 'scroll',

        # Responsive prefixes
        'sm', 'md', 'lg', 'xl', '2xl', 'xs', 'xx', '3xl', '4xl', '5xl', '6xl', '7xl',

        # State prefixes
        'hover', 'focus', 'active', 'visited', 'disabled', 'checked', 'default', 'first', 'last',
        'odd', 'even', 'empty', 'target', 'before', 'after', 'first', 'last', 'only', 'placeholder',

        # JavaScript/CSS common words
        'null', 'nullable', 'true', 'false', 'undefined', 'string', 'number', 'boolean',
        'object', 'array', 'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
        'return', 'import', 'export', 'default', 'async', 'await', 'try', 'catch',
        'throw', 'new', 'this', 'super', 'extends', 'implements', 'interface', 'class',
        'public', 'private', 'protected', 'static', 'final', 'abstract', 'enum',

        # Additional common programming terms
        'data', 'index', 'length', 'count', 'size', 'total', 'current', 'next', 'prev',
        'first', 'last', 'item', 'list', 'array', 'object', 'props', 'children', 'parent',
        'child', 'element', 'component', 'module', 'package', 'library', 'utils', 'helpers',
        'constants', 'types', 'interfaces', 'models', 'services', 'hooks', 'effects', 'actions',
        'reducers', 'selectors', 'sagas', 'thunks', 'middlewares', 'routes', 'pages', 'views',
        'layouts', 'containers', 'components', 'atoms', 'molecules', 'organisms', 'templates',
        'styles', 'themes', 'colors', 'fonts', 'icons', 'images', 'assets', 'files', 'folders',
        'config', 'settings', 'options', 'params', 'query', 'body', 'headers', 'response', 'request',
        'method', 'url', 'path', 'route', 'endpoint', 'api', 'graphql', 'rest', 'http', 'https',
        'json', 'xml', 'html', 'css', 'js', 'ts', 'jsx', 'tsx', 'vue', 'react', 'angular', 'svelte'
        }

        return {
    # Variable name obfuscation
    "single_char_vars": {
    "pattern": r'\b[a-zA-Z]\b(?=\s*[=;:])',
    "description": "Found single-letter variable names like 'a', 'b', 'x'. While sometimes acceptable for simple counters or math variables, this pattern is commonly used in obfuscated code to make it harder to understand the program's logic and purpose.",
    "severity": "low",
    "category": "variable_obfuscation"
    },
    "short_meaningless_vars": {
    "pattern": r'\b[a-zA-Z]{1,3}\b(?=\s*[=;:])(?!\b(?:sm|md|lg|xl|xs|xx|bg|text|flex|grid|top|left|right|bottom|min|max|px|rem|em|auto|none|block|inline|hidden|visible|absolute|relative|fixed|static|sticky)\b)',
    "description": "Detected very short variable names (1-3 characters) that don't convey meaning. Legitimate code usually uses descriptive names that explain what the variable represents, making code self-documenting and easier to maintain.",
    "severity": "low",
    "category": "variable_obfuscation"
    },
            "random_vars": {
                "pattern": r'\b[a-zA-Z]{4,10}(?=\s*[=;:])\b(?!\w*(?:if|for|while|def|function|class|var|let|const|return|import|export))',
                "description": "Found seemingly random variable names that appear computer-generated rather than human-chosen. This suggests the code may have been processed through an obfuscation tool that replaces meaningful names with gibberish to hide the code's true functionality.",
                "severity": "medium",
                "category": "variable_obfuscation"
            },
            "obfuscated_vars": {
                "pattern": r'\b[a-zA-Z]{1,2}[0-9]+\b',
                "description": "Identified variable names combining short letters with numbers (like 'a1', 'x2', 'b10'). This naming pattern is characteristic of code that has been automatically minified or obfuscated, making it difficult for humans to understand variable purposes and relationships.",
                "severity": "low",
                "category": "variable_obfuscation"
            },

            # String obfuscation
            "base64_strings": {
            "pattern": r'[A-Za-z0-9+/]{30,}=*[A-Za-z0-9+/]*={1,2}',
            "description": "Detected long sequences of base64-encoded data. While base64 encoding has legitimate uses (like encoding binary data for transmission), unusually long base64 strings in source code often indicate attempts to hide readable text or binary payloads from casual inspection. This is commonly used by malware to conceal command strings, URLs, or executable code.",
            "severity": "medium",
            "category": "string_obfuscation"
            },
            "hex_strings": {
                "pattern": r'\\x[0-9a-fA-F]{2}',
                "description": "Found hexadecimal escape sequences (\\xXX format) in strings. These are used to represent characters by their ASCII/hexadecimal values. While occasionally legitimate for encoding special characters, patterns of hex escapes often indicate attempts to obscure readable text or hide malicious payloads by making them appear as binary data rather than human-readable strings.",
                "severity": "medium",
                "category": "string_obfuscation"
            },
            "unicode_escapes": {
                "pattern": r'\\u[0-9a-fA-F]{4}',
                "description": "Identified Unicode escape sequences (\\uXXXX format) in the code. Unicode escapes can be legitimate for internationalization, but excessive use or unusual patterns may indicate attempts to hide readable text by representing it in a less obvious encoded format. This technique makes it harder to spot malicious strings during code review.",
                "severity": "medium",
                "category": "string_obfuscation"
            },
            "octal_escapes": {
                "pattern": r'\\[0-7]{1,3}',
                "description": "Detected octal escape sequences (\\XXX format where X is 0-7). These represent characters by their octal (base-8) ASCII values. While sometimes used for legitimate purposes like encoding control characters, this encoding method is often employed to make strings less readable and hide potentially malicious content from automated detection and human reviewers.",
                "severity": "medium",
                "category": "string_obfuscation"
            },

            # Control flow obfuscation
            "eval_usage": {
                "pattern": r'\beval\s*\(',
                "description": "Found usage of the eval() function, which executes arbitrary JavaScript code from a string. This is extremely dangerous as it allows dynamic code execution that can be controlled by external inputs. Eval is commonly used in obfuscated malware to hide malicious payloads and bypass static analysis. It's considered a major security risk and should never be used in production code.",
                "severity": "high",
                "category": "runtime_obfuscation"
            },
            "function_constructor": {
                "pattern": r'\bnew\s+Function\s*\(',
                "description": "Detected dynamic function creation using the Function constructor. This allows creating functions from strings at runtime, similar to eval(). While it can be useful for dynamic code generation, it's often abused by obfuscated malware to hide function logic and payloads. This makes it impossible to statically analyze what the function actually does.",
                "severity": "high",
                "category": "runtime_obfuscation"
            },
            "setTimeout_string": {
                "pattern": r'setTimeout\s*\(\s*["\']',
                "description": "Found setTimeout being called with a string parameter instead of a function. This causes JavaScript to evaluate the string as code using eval(), which is a security risk. Legitimate code should pass function references instead of strings. This pattern is commonly used in obfuscated code to delay execution of malicious payloads.",
                "severity": "medium",
                "category": "runtime_obfuscation"
            },
            "setInterval_string": {
                "pattern": r'setInterval\s*\(\s*["\']',
                "description": "Detected setInterval being called with a string parameter instead of a function. Similar to setTimeout with strings, this evaluates code dynamically and poses security risks. It's commonly used in obfuscated malware to create persistent execution loops that are harder to detect and analyze statically.",
                "severity": "medium",
                "category": "runtime_obfuscation"
            },

            # Code structure obfuscation
            "long_lines": {
                "pattern": r'.{500,}',
                "description": "Extremely long lines",
                "severity": "low",
                "category": "structure_obfuscation"
            },
            "minified_code": {
                "pattern": r'[a-zA-Z_][a-zA-Z0-9_]*=[^;]*;[a-zA-Z_][a-zA-Z0-9_]*=[^;]*;',
                "description": "Multiple assignments on one line (minification pattern)",
                "severity": "medium",
                "category": "structure_obfuscation"
            },
            "nested_ternary": {
                "pattern": r'\?\s*[^?]*\?\s*[^:]*:',
                "description": "Nested ternary operators",
                "severity": "low",
                "category": "structure_obfuscation"
            },

            # Dead code and opaque predicates
            "always_false": {
                "pattern": r'\bif\s*\(\s*false\s*\)',
                "description": "Found an 'if (false)' condition that will never execute. This creates dead code - sections of the program that can never be reached during normal execution. While sometimes used for debugging or feature toggles, this pattern is commonly employed in obfuscated code to confuse analysis tools and make the code appear more complex than it actually is.",
                "severity": "medium",
                "category": "control_flow_obfuscation"
            },
            "always_true": {
                "pattern": r'\bif\s*\(\s*true\s*\)',
                "description": "Detected an 'if (true)' condition that is always true. This creates unnecessary conditional logic that doesn't actually branch. While occasionally used for code organization, this pattern often indicates attempts to make the code appear more complex or to prepare for future obfuscation transformations that would make the condition more complex.",
                "severity": "low",
                "category": "control_flow_obfuscation"
            },

            # Python-specific patterns
            "exec_usage": {
                "pattern": r'\bexec\s*\(',
                "description": "Use of exec() function",
                "severity": "high",
                "category": "runtime_obfuscation"
            },
            "compile_usage": {
                "pattern": r'\bcompile\s*\(',
                "description": "Use of compile() function",
                "severity": "high",
                "category": "runtime_obfuscation"
            },

            # Suspicious patterns
            "suspicious_hex": {
                "pattern": r'0x[0-9a-fA-F]{8,}',
                "description": "Very long hexadecimal numbers",
                "severity": "low",
                "category": "suspicious_patterns"
            },
            "encoded_urls": {
                "pattern": r'[a-zA-Z0-9%]{50,}',
                "description": "Potentially encoded URLs or data",
                "severity": "medium",
                "category": "suspicious_patterns"
            },

            # Known malware signatures (common patterns)
            "obfuscated_function_names": {
                "pattern": r'\b_0x[0-9a-fA-F]+\b',
                "description": "Detected function or variable names following the pattern '_0x' followed by hexadecimal digits. This is a signature of the popular JavaScript obfuscator 'obfuscator.io', which automatically generates these machine-readable names to replace meaningful human-readable identifiers. Such patterns strongly suggest the code has been processed through commercial obfuscation tools, potentially to hide malicious functionality.",
                "severity": "high",
                "category": "malware_signatures"
            },
            "suspicious_eval_patterns": {
                "pattern": r'eval\s*\(\s*atob\s*\(',
                "description": "Found the dangerous combination of eval() and atob() - where base64-encoded data is being decoded and then executed as JavaScript code. This is a classic deobfuscation technique used by malware to hide its true payload. The base64 encoding conceals the malicious code from static analysis, and eval() brings it to life at runtime. This pattern is almost always malicious.",
                "severity": "high",
                "category": "malware_signatures"
            },
            "char_code_strings": {
                "pattern": r'String\.fromCharCode\s*\([^)]{20,}\)',
                "description": "Identified String.fromCharCode() being called with a very long list of numeric arguments. This function converts ASCII character codes back to readable text. Malware often uses this to hide strings by representing them as arrays of numbers, making the malicious content invisible to casual inspection. The long argument list suggests substantial hidden content that could be command strings, URLs, or executable code.",
                "severity": "high",
                "category": "malware_signatures"
            },
            "dynamic_function_creation": {
            "pattern": r'\(function\s*\(\s*\)\s*\{[^}]{100,}',
            "description": "Detected an immediately invoked function expression (IIFE) with an unusually large body of code. While IIFEs are legitimate JavaScript patterns for encapsulation, extremely large ones often indicate that substantial amounts of code have been wrapped in this way to hide functionality. This can be used to create isolated execution contexts for malware while making the code harder to analyze and understand.",
            "severity": "medium",
            "category": "malware_signatures"
            },

            # Additional control flow obfuscation patterns
            "exception_control_flow": {
                "pattern": r'\btry\s*\{[^}]*\}\s*catch\s*\([^)]*\)\s*\{[^}]*\}\s*finally\s*\{[^}]*\}',
                "description": "Complex try/catch/finally blocks used for control flow instead of error handling. While exception handling is legitimate, this pattern with all three blocks suggests the exceptions are being used to create non-linear execution paths that are harder to follow and analyze.",
                "severity": "low",
                "category": "control_flow_obfuscation"
            },
            "nested_conditional_complex": {
                "pattern": r'\?[^?]*\?[^?]*\?[^:]*:[^:]*:[^:]*',
                "description": "Highly nested ternary operators creating complex conditional expressions. This makes code extremely hard to read and understand, effectively obfuscating the control flow logic into a single, dense expression.",
                "severity": "medium",
                "category": "control_flow_obfuscation"
            },
            "switch_as_goto": {
                "pattern": r'switch\s*\([^)]*\)\s*\{[^}]*case[^}]*break[^}]*case[^}]*break[^}]*default[^}]*\}',
                "description": "Switch statement used as a goto mechanism with multiple cases and breaks. While switch statements are legitimate for multi-way branching, this pattern with complex case logic often indicates control flow flattening where structured code has been transformed into a state machine.",
                "severity": "low",
                "category": "control_flow_obfuscation"
            },
            "computed_property_access": {
                "pattern": r'\[[^\]]{10,}\]',
                "description": "Complex computed property access with long expressions inside brackets. This makes it difficult to statically determine which properties are being accessed, hiding the data flow and potentially concealing malicious operations.",
                "severity": "medium",
                "category": "structure_obfuscation"
            },
            "function_rebinding": {
                "pattern": r'\.[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*function',
                "description": "Function properties being reassigned to new function expressions. This dynamic function rebinding makes it impossible to statically analyze what functions are actually being called, creating uncertainty in the program's behavior.",
                "severity": "medium",
                "category": "runtime_obfuscation"
            },

            # String manipulation obfuscation
            "string_splitting": {
                "pattern": r'"[^"]*"\s*\+\s*"[^"]*"\s*\+\s*"[^"]*"',
                "description": "String concatenation of multiple literal parts. While sometimes legitimate for readability, this pattern is commonly used to hide complete strings from static analysis by splitting them into smaller, seemingly unrelated pieces.",
                "severity": "low",
                "category": "string_obfuscation"
            },
            "array_join_strings": {
                "pattern": r'\[[^\]]*"[^"]*"[^\]]*\]\.join\s*\(',
                "description": "Array of strings being joined together. This technique splits what would be a single string into an array of substrings, making it harder to detect malicious strings or URLs during static analysis.",
                "severity": "medium",
                "category": "string_obfuscation"
            },

            # Variable scope obfuscation
            "var_hoisting_abuse": {
                "pattern": r'\bvar\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^;]*;\s*\bfunction\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*\{[^}]*\bvar\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^;]*;',
                "description": "Variable hoisting abuse where variables are declared after being used or in confusing scopes. This exploits JavaScript's hoisting behavior to create code that appears to work but is hard to understand and maintain.",
                "severity": "low",
                "category": "variable_obfuscation"
            },

            # Anti-analysis patterns
            "debugger_prevention": {
                "pattern": r'\bdebugger\s*;\s*[^{}]*\{[^{}]*\}',
                "description": "Debugger statements hidden within code blocks or conditional expressions. This is an attempt to prevent debugging and analysis of the code, making it harder for security researchers to understand the program's behavior.",
                "severity": "high",
                "category": "anti_analysis"
            },
            "timing_checks": {
                "pattern": r'Date\.now\(\)|performance\.now\(\)|new\s+Date\(\)',
                "description": "Timing measurements that could be used for anti-analysis techniques. Code that checks execution time might be trying to detect if it's running in a debugger or analysis environment.",
                "severity": "medium",
                "category": "anti_analysis"
            }
        }

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
        """Analyze variable naming patterns for obfuscation indicators."""
        findings = []

        # Collect all variable/function names
        var_pattern = r'\b(?:var|let|const|def|function|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        assignment_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*[:=]\s*[^=]'

        all_names = []
        for line in lines:
            all_names.extend(re.findall(var_pattern, line))
            all_names.extend(re.findall(assignment_pattern, line))

        if not all_names:
            return findings

        # Analyze name characteristics
        name_lengths = [len(name) for name in all_names]
        avg_length = sum(name_lengths) / len(name_lengths)

        # Check for predominantly short names
        short_names = sum(1 for length in name_lengths if length <= 3)
        if len(all_names) > 10 and short_names / len(all_names) > 0.7:
            findings.append(Finding(
                file_path="",
                line_number=0,
                obfuscation_type="predominantly_short_names",
                description=f"This file uses an unusually high proportion of very short variable/function names. Out of {len(all_names)} total identifiers, {short_names} ({short_names/len(all_names)*100:.1f}%) are only 1-3 characters long. While some short names are acceptable (like 'i' for loop counters), this extreme ratio suggests systematic obfuscation where meaningful names have been replaced with cryptic abbreviations to make the code harder to understand and maintain.",
                severity="medium",
                evidence=f"Short names: {short_names}/{len(all_names)} ({short_names/len(all_names)*100:.1f}%)",
                confidence=0.8,
                full_line="",
                category="variable_obfuscation"
            ))

        # Check for very low average name length
        if avg_length < 4.0 and len(all_names) > 20:
            findings.append(Finding(
                file_path="",
                line_number=0,
                obfuscation_type="low_average_name_length",
                description=f"The average length of variable and function names in this file is abnormally short ({avg_length:.2f} characters across {len(all_names)} identifiers). Typical well-written code uses descriptive names that average 8-15 characters to convey meaning and purpose. This unusually short average strongly suggests the code has been processed through an obfuscation tool that systematically shortens all identifiers, making it extremely difficult for developers to understand what each variable or function actually represents.",
                severity="low",
                evidence=f"Average length: {avg_length:.2f}, Total names: {len(all_names)}",
                confidence=0.6,
                full_line="",
                category="variable_obfuscation"
            ))

        return findings

    def analyze_javascript_code(self, file_path: Path, content: str, lines: List[str]) -> List[Finding]:
        """Perform JavaScript-specific analysis."""
        findings = []

        # Check for common obfuscator patterns
        if "_0x" in content and "function" in content:
            # Likely obfuscator.io style
            hex_functions = len(re.findall(r'_0x[0-9a-fA-F]+\s*\(', content))
            if hex_functions > 5:
                findings.append(Finding(
                    file_path=str(file_path),
                    line_number=0,
                    obfuscation_type="obfuscator_io_pattern",
                    description="Detected obfuscator.io style obfuscation (hex function names)",
                    severity="high",
                    evidence=f"Found {hex_functions} hex-named functions",
                    confidence=0.95,
                    full_line="",
                    category="suspicious_patterns"
                ))

        # Check for self-defending code (anti-tampering)
        if "debugger" in content and ("void" in content or "return" in content):
            findings.append(Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="anti_debugging",
                description="Potential anti-debugging code detected",
                severity="high",
                evidence="debugger statements found",
                confidence=0.8,
                full_line="",
                category="runtime_obfuscation"
            ))

        # Check for domain locking (code that only runs on specific domains)
        domain_checks = re.findall(r'(location\.hostname|document\.domain|window\.location)', content)
        if len(domain_checks) > 2:
            findings.append(Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="domain_locking",
                description="Potential domain locking mechanism",
                severity="medium",
                evidence=f"Multiple domain checks: {len(domain_checks)}",
                confidence=0.7,
                full_line="",
                category="runtime_obfuscation"
            ))

        # Check for packed/encrypted code patterns
        if "eval(" in content and ("atob(" in content or "btoa(" in content):
            findings.append(Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="packed_code",
                description="Potential packed/encrypted code (eval with base64)",
                severity="high",
                evidence="eval() with base64 encoding detected",
                confidence=0.9,
                full_line="",
                category="malware_signatures"
            ))

        # Check for timing-based obfuscation
        timing_patterns = re.findall(r'setTimeout\s*\([^,]+,\s*\d+\)', content)
        if len(timing_patterns) > 10:
            findings.append(Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="timing_obfuscation",
                description="Excessive use of setTimeout (potential timing-based obfuscation)",
                severity="medium",
                evidence=f"Found {len(timing_patterns)} setTimeout calls",
                confidence=0.8,
                full_line="",
                category="runtime_obfuscation"
            ))

        return findings

    def analyze_python_ast(self, file_path: Path, content: str, lines: List[str] = None) -> List[Finding]:
        """Perform AST-based analysis for Python files."""
        findings = []

        try:
            import ast
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            # If AST parsing fails, it might be obfuscated code
            findings.append(Finding(
                file_path=str(file_path),
                line_number=0,
                obfuscation_type="syntax_error",
                description="File contains syntax errors (potential obfuscation)",
                severity="medium",
                evidence="AST parsing failed",
                confidence=0.7,
                full_line="",
                category="structure_obfuscation"
            ))
            return findings
        except Exception as e:
            # Other AST parsing errors
            return findings

        try:
            # Check for suspicious imports
            suspicious_imports = ['exec', 'eval', 'compile', 'subprocess', 'os.system', 'pickle.loads']
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in suspicious_imports or any(susp in alias.name for susp in suspicious_imports):
                            findings.append(Finding(
                                file_path=str(file_path),
                                line_number=getattr(node, 'lineno', 0),
                                obfuscation_type="suspicious_import",
                                description=f"Suspicious import: {alias.name}",
                                severity="high",
                                evidence=f"import {alias.name}",
                                confidence=0.9,
                                full_line=lines[getattr(node, 'lineno', 1) - 1] if lines and getattr(node, 'lineno', 0) > 0 and getattr(node, 'lineno', 0) <= len(lines) else "",
                                category="malware_signatures"
                            ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(susp in node.module for susp in suspicious_imports):
                        findings.append(Finding(
                            file_path=str(file_path),
                            line_number=getattr(node, 'lineno', 0),
                            obfuscation_type="suspicious_import",
                            description=f"Suspicious import from: {node.module}",
                            severity="high",
                            evidence=f"from {node.module} import ...",
                            confidence=0.9,
                            full_line=lines[getattr(node, 'lineno', 1) - 1] if lines and getattr(node, 'lineno', 0) > 0 and getattr(node, 'lineno', 0) <= len(lines) else "",
                            category="malware_signatures"
                        ))

            # Check for dynamic code execution
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['exec', 'eval', 'compile']:
                            findings.append(Finding(
                                file_path=str(file_path),
                                line_number=getattr(node, 'lineno', 0),
                                obfuscation_type="dynamic_code_execution",
                                description=f"Dynamic code execution via {node.func.id}()",
                                severity="high",
                                evidence=f"{node.func.id}() call",
                                confidence=1.0,
                                full_line=lines[getattr(node, 'lineno', 1) - 1] if lines and getattr(node, 'lineno', 0) > 0 and getattr(node, 'lineno', 0) <= len(lines) else "",
                                category="runtime_obfuscation"
                            ))

            # Control flow obfuscation detection

            # Check for opaque predicates (conditions that are always true/false but look complex)
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check for conditions that are always true/false
                    if self._is_always_true(node.test) or self._is_always_false(node.test):
                        findings.append(Finding(
                            file_path=str(file_path),
                            line_number=getattr(node, 'lineno', 0),
                            obfuscation_type="opaque_predicate",
                            description="Detected an opaque predicate - a conditional statement with a condition that is always true or always false, but written to appear complex. This creates dead code branches that confuse static analysis while having no effect on runtime behavior. Malware often uses opaque predicates to make reverse engineering more difficult.",
                            severity="medium",
                            evidence=f"if {self._get_node_source(node.test, content)}",
                            confidence=0.8,
                            full_line=lines[getattr(node, 'lineno', 1) - 1] if lines and getattr(node, 'lineno', 0) > 0 and getattr(node, 'lineno', 0) <= len(lines) else "",
                            category="control_flow_obfuscation"
                        ))

            # Check for infinite loops
            for node in ast.walk(tree):
                if isinstance(node, ast.While):
                    # Check for while True with no break
                    if self._is_always_true(node.test):
                        has_break = any(isinstance(child, ast.Break) for child in ast.walk(node.body))
                        if not has_break:
                            findings.append(Finding(
                                file_path=str(file_path),
                                line_number=getattr(node, 'lineno', 0),
                                obfuscation_type="infinite_loop",
                                description="Detected an infinite loop (while True with no break statement). While infinite loops can be legitimate in some contexts (like servers or event loops), they are commonly used in obfuscated code to create confusion or hide malicious behavior. The lack of any break condition makes static analysis difficult.",
                                severity="low",
                                evidence="while True: (no break found)",
                                confidence=0.7,
                                full_line=lines[getattr(node, 'lineno', 1) - 1] if lines and getattr(node, 'lineno', 0) > 0 and getattr(node, 'lineno', 0) <= len(lines) else "",
                                category="control_flow_obfuscation"
                            ))

            # Check for control flow flattening (using variables as state machines)
            state_variables = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            state_variables.add(target.id)
                elif isinstance(node, ast.If):
                    # Look for if statements that assign to state variables
                    if node.body and len(node.body) > 0 and isinstance(node.body[0], ast.Assign):
                        assign = node.body[0]
                        if len(assign.targets) > 0 and isinstance(assign.targets[0], ast.Name) and assign.targets[0].id in state_variables:
                            findings.append(Finding(
                                file_path=str(file_path),
                                line_number=getattr(node, 'lineno', 0),
                                obfuscation_type="control_flow_flattening",
                                description="Detected potential control flow flattening - using conditional statements to manage state variables instead of structured control flow. This technique transforms readable if/else chains into a state machine pattern, making the code much harder to understand and analyze.",
                                severity="medium",
                                evidence=f"State variable assignment in conditional: {assign.targets[0].id}",
                                confidence=0.6,
                                full_line=lines[getattr(node, 'lineno', 1) - 1] if lines and getattr(node, 'lineno', 0) > 0 and getattr(node, 'lineno', 0) <= len(lines) else "",
                                category="control_flow_obfuscation"
                            ))

            # Check for exception-based control flow
            exception_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Try, ast.ExceptHandler)))
            function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            if function_count > 0 and exception_count / function_count > 2:
                findings.append(Finding(
                    file_path=str(file_path),
                    line_number=0,
                    obfuscation_type="excessive_exceptions",
                    description=f"Excessive use of exception handling for control flow. Found {exception_count} exception-related constructs across {function_count} functions (ratio: {exception_count/function_count:.1f}). While exceptions are useful for error handling, using them for normal program flow (like 'try/except' instead of 'if/else') is a common obfuscation technique that makes code harder to follow and analyze.",
                    severity="low",
                    evidence=f"{exception_count} exceptions, {function_count} functions",
                    confidence=0.7,
                    full_line="",
                    category="control_flow_obfuscation"
                ))

            # Check for dead code (unreachable statements)
            # This is simplified - in practice, full reachability analysis would be more complex
            # Note: Full dead code detection requires control flow analysis which is complex

        except ImportError:
            # AST not available, skip
            pass

        return findings

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

    def _is_always_true(self, node: ast.AST) -> bool:
        """Check if an AST node always evaluates to True."""
        if isinstance(node, ast.Constant):
            return node.value is True
        elif isinstance(node, ast.NameConstant):  # For older Python versions
            return node.value is True
        elif isinstance(node, ast.Compare):
            # Handle comparison operations
            if len(node.ops) == 1:
                left_val = self._get_constant_value(node.left)
                right_val = self._get_constant_value(node.comparators[0])
                if left_val is not None and right_val is not None:
                    if isinstance(node.ops[0], ast.Eq):
                        return left_val == right_val
                    elif isinstance(node.ops[0], ast.NotEq):
                        return left_val != right_val
        elif isinstance(node, ast.BinOp):
            # Check for tautologies like x == x, 1 == 1, etc.
            if isinstance(node.op, (ast.Eq, ast.Is)):
                left_val = self._get_constant_value(node.left)
                right_val = self._get_constant_value(node.right)
                if left_val is not None and right_val is not None:
                    return left_val == right_val
                # Check for x == x pattern
                if ast.dump(node.left) == ast.dump(node.right):
                    return True
            elif isinstance(node.op, ast.NotEq):
                left_val = self._get_constant_value(node.left)
                right_val = self._get_constant_value(node.right)
                if left_val is not None and right_val is not None:
                    return left_val != right_val
        return False

    def _is_always_false(self, node: ast.AST) -> bool:
        """Check if an AST node always evaluates to False."""
        if isinstance(node, ast.Constant):
            return node.value is False
        elif isinstance(node, ast.NameConstant):  # For older Python versions
            return node.value is False
        elif isinstance(node, ast.Compare):
            # Handle comparison operations
            if len(node.ops) == 1:
                left_val = self._get_constant_value(node.left)
                right_val = self._get_constant_value(node.comparators[0])
                if left_val is not None and right_val is not None:
                    if isinstance(node.ops[0], ast.Eq):
                        return left_val != right_val
                    elif isinstance(node.ops[0], ast.NotEq):
                        return left_val == right_val
        elif isinstance(node, ast.BinOp):
            # Check for contradictions like 0 == 1, True == False, etc.
            if isinstance(node.op, (ast.Eq, ast.Is)):
                left_val = self._get_constant_value(node.left)
                right_val = self._get_constant_value(node.right)
                if left_val is not None and right_val is not None:
                    return left_val != right_val
            elif isinstance(node.op, ast.NotEq):
                left_val = self._get_constant_value(node.left)
                right_val = self._get_constant_value(node.right)
                if left_val is not None and right_val is not None:
                    return left_val == right_val
        return False

    def _get_constant_value(self, node: ast.AST):
        """Extract constant value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.NameConstant):  # For older Python versions
            return node.value
        elif isinstance(node, ast.Num):  # Even older Python
            return node.n
        elif isinstance(node, ast.Str):  # Even older Python
            return node.s
        return None

    def _get_node_source(self, node: ast.AST, source: str) -> str:
        """Extract source code for an AST node."""
        if hasattr(ast, 'get_source_segment'):
            try:
                result = ast.get_source_segment(source, node)
                if result:
                    return result
            except:
                pass
        return str(node)

    def analyze_file(self, file_path: Path) -> List[Finding]:
        """Analyze a single file for obfuscation patterns."""
        findings = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()

            # Regex pattern matching
            for line_num, line in enumerate(lines, 1):
                # Skip lines that are clearly CSS/Tailwind class declarations
                if self._is_css_class_line(line):
                    continue

                for pattern_name, pattern_info in self.patterns.items():
                    matches = re.findall(pattern_info["pattern"], line)
                    if matches:
                        # Filter matches
                        filtered_matches = []
                        for match in matches:
                            # Skip common legitimate words for variable-related patterns
                            if pattern_name in ["random_vars", "short_meaningless_vars", "single_char_vars", "obfuscated_vars"] and match.lower() in self.common_words:
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
                            findings.append(finding)

            # Advanced analysis - run independent checks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
                futures = [
                    executor.submit(self.detect_high_entropy_strings, lines),
                    executor.submit(self.analyze_variable_names, lines),
                    executor.submit(self.check_file_structure, file_path, lines)
                ]

                # Language-specific analysis (conditional)
                if file_path.suffix == '.py':
                    futures.append(executor.submit(self.analyze_python_ast, file_path, content, lines))
                elif file_path.suffix == '.js':
                    futures.append(executor.submit(self.analyze_javascript_code, file_path, content, lines))

                for future in concurrent.futures.as_completed(futures):
                    adv_findings = future.result()
                    for finding in adv_findings:
                        finding.file_path = str(file_path)
                        findings.append(finding)

        except Exception as e:
            # Skip files that can't be read
            pass

        return findings

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
            ".js": r'//|/\*|\*/',
            ".py": r'#',
            ".java": r'//|/\*|\*/',
            ".cpp": r'//|/\*|\*/',
            ".c": r'//|/\*|\*/',
            ".cs": r'//|/\*|\*/'
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
