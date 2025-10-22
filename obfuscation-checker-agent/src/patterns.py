import re

class ObfuscationPatterns:
    def __init__(self):
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
            'json', 'xml', 'html', 'css', 'js', 'ts', 'jsx', 'tsx', 'vue', 'react', 'angular', 'svelte',
            # JavaScript statements and built-ins
            'debugger', 'console', 'alert', 'prompt', 'confirm'
            # [Previous words remain the same...]
            
            # Additional HTML/DOM terms
            'canvas', 'audio', 'video', 'source', 'track', 'figure', 'figcaption',
            'details', 'summary', 'dialog', 'menu', 'nav', 'aside', 'article',
            'section', 'main', 'header', 'footer', 'address', 'time', 'progress',
            'meter', 'output', 'input', 'label', 'select', 'option', 'datalist',
            'fieldset', 'legend', 'form', 'table', 'thead', 'tbody', 'tfoot', 'tr',
            'td', 'th', 'caption', 'col', 'colgroup', 'button', 'textarea',

            # Additional CSS properties
            'transition', 'animation', 'keyframes', 'duration', 'timing', 'delay',
            'iteration', 'direction', 'fill', 'play', 'pause', 'running', 'paused',
            'infinite', 'linear', 'ease', 'steps', 'cubic', 'bezier', 'spring',
            'bounce', 'elastic', 'perspective', 'backface', 'visibility',
            'overflow', 'clip', 'mask', 'blend', 'isolation', 'luminosity',
            
            # Programming concepts
            'memoize', 'curry', 'partial', 'compose', 'pipe', 'throttle', 'debounce',
            'singleton', 'factory', 'builder', 'prototype', 'decorator', 'observer',
            'mediator', 'command', 'iterator', 'generator', 'proxy', 'facade',
            'adapter', 'bridge', 'composite', 'flyweight', 'chain', 'interpreter',
            'memento', 'state', 'strategy', 'template', 'visitor',

            # Database terms
            'query', 'schema', 'table', 'column', 'row', 'index', 'primary', 'foreign',
            'key', 'constraint', 'unique', 'check', 'default', 'null', 'join', 'inner',
            'outer', 'left', 'right', 'full', 'cross', 'union', 'intersect', 'except',
            'group', 'having', 'order', 'limit', 'offset', 'fetch', 'cascade',
            
            # Web development
            'fetch', 'axios', 'request', 'response', 'status', 'headers', 'body',
            'params', 'query', 'cookie', 'session', 'token', 'auth', 'oauth',
            'jwt', 'bearer', 'basic', 'digest', 'cors', 'proxy', 'cache', 'etag',
            'expires', 'modified', 'content', 'type', 'length', 'encoding',
            
            # Testing terms
            'test', 'suite', 'spec', 'mock', 'stub', 'spy', 'assert', 'expect',
            'should', 'describe', 'context', 'before', 'after', 'each', 'all',
            'done', 'pending', 'skip', 'only', 'timeout', 'retry', 'fail', 'pass',
            
            # Build tools and deployment
            'build', 'deploy', 'release', 'stage', 'prod', 'dev', 'test', 'preview',
            'bundle', 'chunk', 'asset', 'source', 'map', 'hash', 'version', 'tag',
            'branch', 'merge', 'rebase', 'cherry', 'pick', 'squash', 'fixup',
            
            # Security terms
            'auth', 'token', 'secret', 'key', 'salt', 'hash', 'encrypt', 'decrypt',
            'sign', 'verify', 'cert', 'chain', 'trust', 'revoke', 'grant', 'deny',
            'allow', 'block', 'filter', 'sanitize', 'escape', 'validate',
            
            # Performance terms
            'cache', 'buffer', 'stream', 'chunk', 'batch', 'queue', 'stack', 'heap',
            'memory', 'cpu', 'thread', 'process', 'worker', 'pool', 'cluster',
            'shard', 'replica', 'master', 'slave', 'primary', 'secondary',
            
            # Common variable names
            'temp', 'tmp', 'aux', 'buf', 'cur', 'prev', 'next', 'start', 'end',
            'begin', 'finish', 'head', 'tail', 'front', 'back', 'top', 'bottom',
            'left', 'right', 'mid', 'center', 'inner', 'outer', 'upper', 'lower',

            # Math terms
            'sum', 'avg', 'min', 'max', 'count', 'mean', 'median', 'mode', 'range',
            'delta', 'diff', 'ratio', 'rate', 'total', 'partial', 'sqrt', 'pow',
            'exp', 'log', 'sin', 'cos', 'tan', 'abs', 'floor', 'ceil', 'round',

            # Time-related
            'time', 'date', 'year', 'month', 'day', 'hour', 'minute', 'second',
            'milli', 'micro', 'nano', 'timezone', 'utc', 'gmt', 'iso', 'unix',
            'epoch', 'duration', 'interval', 'period', 'schedule', 'cron',
            
            # Common abbreviations
            'dir', 'temp', 'doc', 'conf', 'log', 'info', 'err', 'warn', 'debug',
            'proc', 'arg', 'param', 'cfg', 'str', 'num', 'bool', 'obj', 'arr',
            'func', 'var', 'env', 'prod', 'dev', 'test', 'stmt', 'expr', 'impl'
        }

    def get_patterns(self):
        """Define regex patterns for detecting obfuscation."""
        patterns = {
            # Variable name obfuscation
            "single_char_vars": {
                "pattern": r'\b[a-zA-Z]\b(?=\s*[=;:])',
                "description": "Found single-letter variable names like 'a', 'b', 'x'. While sometimes acceptable for simple counters or math variables, this pattern is commonly used in obfuscated code to make it harder to understand the program's logic and purpose.",
                "severity": "low",
                "category": "variable_obfuscation"
            },
            "short_meaningless_vars": {
                "pattern": r'\b[a-zA-Z]{1,3}\b(?=\s*[=;:])',
                "description": "Detected very short variable names (1-3 characters) that don't convey meaning. Legitimate code usually uses descriptive names that explain what the variable represents, making code self-documenting and easier to maintain.",
                "severity": "low",
                "category": "variable_obfuscation"
            },
            "random_vars": {
                "pattern": r'\b[a-zA-Z]{4,10}(?=\s*[=;:])\b',
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
                "description": "Found hexadecimal escape sequences (\\\\xXX format) in strings. These are used to represent characters by their ASCII/hexadecimal values. While occasionally legitimate for encoding special characters, patterns of hex escapes often indicate attempts to obscure readable text or hide malicious payloads by making them appear as binary data rather than human-readable strings.",
                "severity": "medium",
                "category": "string_obfuscation"
            },
            "unicode_escapes": {
                "pattern": r'\\u[0-9a-fA-F]{4}',
                "description": "Identified Unicode escape sequences (\\\\uXXXX format) in the code. Unicode escapes can be legitimate for internationalization, but excessive use or unusual patterns may indicate attempts to hide readable text by representing it in a less obvious encoded format. This technique makes it harder to spot malicious strings during code review.",
                "severity": "medium",
                "category": "string_obfuscation"
            },
            "octal_escapes": {
                "pattern": r'\\[0-7]{1,3}',
                "description": "Detected octal escape sequences (\\\\XXX format where X is 0-7). These represent characters by their octal (base-8) ASCII values. While sometimes used for legitimate purposes like encoding control characters, this encoding method is often employed to make strings less readable and hide potentially malicious content from automated detection and human reviewers.",
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
                "pattern": r'\\?\\s*[^?]*\\?\\s*[^:]*:',
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
            
            "nested_conditional_complex": {
            "pattern": r'\?[^?]*\?[^?]*\?[^:]*:[^:]*:[^:]*',
                "description": "Highly nested ternary operators creating complex conditional expressions. This makes code extremely hard to read and understand, effectively obfuscating the control flow logic into a single, dense expression.",
                "severity": "medium",
                "category": "control_flow_obfuscation"
            },
            
            "computed_property_access": {
            "pattern": r'\b\w+\s*\[\s*[^\]]{10,}\s*\]',
            "description": "Complex computed property access with long expressions inside brackets following an identifier. This makes it difficult to statically determine which properties are being accessed, hiding the data flow and potentially concealing malicious operations.",
            "severity": "medium",
            "category": "structure_obfuscation"
            },
            "function_rebinding": {
            "pattern": r'\.[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*function',
                "description": "Function properties being reassigned to new function expressions. This dynamic function rebinding makes it impossible to statically analyze what functions are actually called, creating uncertainty in the program's behavior.",
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

        # Don't pre-compile patterns here - they will be compiled when needed
        # This allows the patterns to be serialized for multiprocessing
        return patterns
