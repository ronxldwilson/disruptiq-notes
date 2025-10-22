import ast
from pathlib import Path
from typing import List

from findings import Finding

class ASTAnalyzer:
    def __init__(self, config):
        self.config = config

    def analyze_python_ast(self, file_path: Path, content: str, lines: List[str]) -> List[Finding]:
        """Perform Python AST-based analysis."""
        findings = []

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            # Skip files with syntax errors
            return findings

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
                            description="Detected an opaque predicate - a conditional statement with a condition that is always true or false, but written to appear complex. This creates dead code branches that confuse static analysis while having no effect on runtime behavior. Malware often uses opaque predicates to make reverse engineering more difficult.",
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
                try:
                    if ast.dump(node.left) == ast.dump(node.right):
                        return True
                except AttributeError:
                    pass  # Skip if AST nodes are malformed
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
        if hasattr(ast, 'get_source_segment') and hasattr(node, '_fields'):
            try:
                result = ast.get_source_segment(source, node)
                if result:
                    return result
            except:
                pass
        return str(node)
