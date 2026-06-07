"""Cyclomatic complexity and function length analysis."""

import ast
import os

from radon.complexity import cc_visit

from roastmyrepo.analyzers.base import BaseAnalyzer
from roastmyrepo.models import Category, Finding, Severity


class ComplexityAnalyzer(BaseAnalyzer):
    """Analyzes cyclomatic complexity and function length."""

    CC_HIGH = 10
    CC_CRITICAL = 20
    LENGTH_MEDIUM = 50
    LENGTH_HIGH = 100

    def analyze(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []
        for filepath in self._iter_python_files(repo_path):
            rel_path = os.path.relpath(filepath, repo_path)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
            except OSError:
                continue

            findings.extend(self._check_complexity(source, rel_path))
            findings.extend(self._check_function_length(source, rel_path))
        return findings

    def _check_complexity(self, source: str, rel_path: str) -> list[Finding]:
        findings = []
        try:
            blocks = cc_visit(source)
        except Exception:
            return findings

        for block in blocks:
            if block.complexity > self.CC_CRITICAL:
                severity = Severity.critical
            elif block.complexity > self.CC_HIGH:
                severity = Severity.high
            else:
                continue

            findings.append(
                Finding(
                    file_path=rel_path,
                    line=block.lineno,
                    category=Category.complexity,
                    severity=severity,
                    title=f"High cyclomatic complexity ({block.complexity}) in '{block.name}'",
                    description=(
                        f"Function '{block.name}' has a cyclomatic complexity of "
                        f"{block.complexity}. Aim for complexity under {self.CC_HIGH}."
                    ),
                    suggested_fix="Extract helper functions to reduce cyclomatic complexity.",
                )
            )
        return findings

    def _check_function_length(self, source: str, rel_path: str) -> list[Finding]:
        findings = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return findings

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.body:
                    continue
                start = node.lineno
                end = max(getattr(n, "end_lineno", n.lineno) for n in ast.walk(node) if hasattr(n, "lineno"))
                length = end - start + 1

                if length > self.LENGTH_HIGH:
                    severity = Severity.high
                elif length > self.LENGTH_MEDIUM:
                    severity = Severity.medium
                else:
                    continue

                findings.append(
                    Finding(
                        file_path=rel_path,
                        line=start,
                        category=Category.complexity,
                        severity=severity,
                        title=f"Long function '{node.name}' ({length} lines)",
                        description=(
                            f"Function '{node.name}' is {length} lines long. "
                            f"Consider breaking it into smaller, focused functions."
                        ),
                        suggested_fix="Break this function into smaller, focused functions.",
                    )
                )
        return findings
