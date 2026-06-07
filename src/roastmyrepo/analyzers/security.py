"""Security vulnerability pattern detection."""

import ast
import os
import re

from roastmyrepo.analyzers.base import BaseAnalyzer
from roastmyrepo.models import Category, Finding, Severity

# Patterns for hardcoded secrets
SECRET_PATTERNS = [
    (re.compile(r"""(?:api[_-]?key|apikey)\s*=\s*['"][A-Za-z0-9_\-]{16,}['"]""", re.IGNORECASE), "API key"),
    (re.compile(r"""(?:password|passwd|pwd)\s*=\s*['"][^'"]{4,}['"]""", re.IGNORECASE), "password"),
    (re.compile(r"""(?:secret|token)\s*=\s*['"][A-Za-z0-9_\-]{8,}['"]""", re.IGNORECASE), "secret/token"),
    (re.compile(r"""(?:aws_access_key_id)\s*=\s*['"]AKIA[A-Z0-9]{16}['"]""", re.IGNORECASE), "AWS access key"),
]

# SQL-related patterns
SQL_KEYWORDS = re.compile(r"\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b", re.IGNORECASE)


class SecurityAnalyzer(BaseAnalyzer):
    """Detects security vulnerability patterns in code."""

    def analyze(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []
        for filepath in self._iter_python_files(repo_path):
            rel_path = os.path.relpath(filepath, repo_path)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
            except OSError:
                continue

            findings.extend(self._check_hardcoded_secrets(source, rel_path))

            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue

            findings.extend(self._check_eval_exec(tree, rel_path))
            findings.extend(self._check_shell_injection(tree, rel_path))
            findings.extend(self._check_sql_injection(tree, source, rel_path))
        return findings

    def _check_hardcoded_secrets(self, source: str, rel_path: str) -> list[Finding]:
        findings = []
        lines = source.split("\n")
        for lineno, line in enumerate(lines, 1):
            for pattern, secret_type in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            file_path=rel_path,
                            line=lineno,
                            category=Category.security,
                            severity=Severity.critical,
                            title=f"Hardcoded {secret_type} detected",
                            description=f"Possible hardcoded {secret_type} found in source code.",
                            code_snippet=line.strip(),
                            suggested_fix="Move secrets to environment variables.",
                        )
                    )
        return findings

    def _check_eval_exec(self, tree: ast.AST, rel_path: str) -> list[Finding]:
        findings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                    func_name = node.func.id
                if func_name:
                    findings.append(
                        Finding(
                            file_path=rel_path,
                            line=node.lineno,
                            category=Category.security,
                            severity=Severity.critical,
                            title=f"Use of {func_name}()",
                            description=(
                                f"Use of {func_name}() can execute arbitrary code. "
                                "Avoid unless absolutely necessary."
                            ),
                            suggested_fix=f"Replace {func_name}() with a safer alternative.",
                        )
                    )
        return findings

    def _check_shell_injection(self, tree: ast.AST, rel_path: str) -> list[Finding]:
        findings = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # Check for subprocess calls with shell=True
            func_name = self._get_call_name(node)
            if func_name and "subprocess" in func_name:
                for kw in node.keywords:
                    if kw.arg == "shell":
                        if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            findings.append(
                                Finding(
                                    file_path=rel_path,
                                    line=node.lineno,
                                    category=Category.security,
                                    severity=Severity.high,
                                    title="subprocess with shell=True",
                                    description=(
                                        "Using subprocess with shell=True can lead to "
                                        "shell injection vulnerabilities."
                                    ),
                                    suggested_fix=(
                                        "Use subprocess with shell=False and pass arguments as a list."
                                    ),
                                )
                            )
        return findings

    def _check_sql_injection(self, tree: ast.AST, source: str, rel_path: str) -> list[Finding]:
        findings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):  # f-string
                # Reconstruct a rough version to check for SQL
                try:
                    line = source.split("\n")[node.lineno - 1]
                except (IndexError, AttributeError):
                    continue
                if SQL_KEYWORDS.search(line):
                    findings.append(
                        Finding(
                            file_path=rel_path,
                            line=node.lineno,
                            category=Category.security,
                            severity=Severity.high,
                            title="Possible SQL injection via f-string",
                            description="SQL query constructed using f-string formatting.",
                            code_snippet=line.strip(),
                            suggested_fix="Use parameterized queries instead of string formatting.",
                        )
                    )
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "format":
                    try:
                        line = source.split("\n")[node.lineno - 1]
                    except (IndexError, AttributeError):
                        continue
                    if SQL_KEYWORDS.search(line):
                        findings.append(
                            Finding(
                                file_path=rel_path,
                                line=node.lineno,
                                category=Category.security,
                                severity=Severity.high,
                                title="Possible SQL injection via .format()",
                                description="SQL query constructed using .format() string formatting.",
                                code_snippet=line.strip(),
                                suggested_fix="Use parameterized queries instead of string formatting.",
                            )
                        )
        return findings

    @staticmethod
    def _get_call_name(node: ast.Call) -> str | None:
        """Extract dotted name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return None
