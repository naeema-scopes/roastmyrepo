"""Naming pattern analysis via AST."""

import ast
import os
import re
from collections import Counter

from roastmyrepo.analyzers.base import BaseAnalyzer
from roastmyrepo.models import Category, Finding, Severity

GENERIC_NAMES = {"data", "temp", "tmp", "result", "results", "handle", "val", "value", "obj", "item"}
SINGLE_CHAR_EXCEPTIONS = {"_", "i", "j", "k", "x", "y", "e"}  # common loop/except vars


class _NameCollector(ast.NodeVisitor):
    """AST visitor that collects variable, function, and class names."""

    def __init__(self):
        self.variables: list[tuple[str, int]] = []
        self.functions: list[tuple[str, int]] = []
        self.classes: list[tuple[str, int]] = []
        self._loop_targets: set[str] = set()
        self._comprehension_targets: set[str] = set()

    def visit_FunctionDef(self, node):
        self.functions.append((node.name, node.lineno))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.functions.append((node.name, node.lineno))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.append((node.name, node.lineno))
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self._loop_targets.add(node.target.id)
        self.generic_visit(node)

    def visit_ListComp(self, node):
        for gen in node.generators:
            if isinstance(gen.target, ast.Name):
                self._comprehension_targets.add(gen.target.id)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        for gen in node.generators:
            if isinstance(gen.target, ast.Name):
                self._comprehension_targets.add(gen.target.id)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        for gen in node.generators:
            if isinstance(gen.target, ast.Name):
                self._comprehension_targets.add(gen.target.id)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        for gen in node.generators:
            if isinstance(gen.target, ast.Name):
                self._comprehension_targets.add(gen.target.id)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append((target.id, node.lineno))
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.append((node.target.id, node.lineno))
        self.generic_visit(node)


class NamingAnalyzer(BaseAnalyzer):
    """Analyzes naming patterns for quality issues."""

    def analyze(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []
        for filepath in self._iter_python_files(repo_path):
            rel_path = os.path.relpath(filepath, repo_path)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source)
            except (OSError, SyntaxError):
                continue

            collector = _NameCollector()
            collector.visit(tree)

            findings.extend(self._check_single_char(collector, rel_path))
            findings.extend(self._check_generic_names(collector, rel_path))
            findings.extend(self._check_casing_consistency(collector, rel_path))
            findings.extend(self._check_prefix_repetition(collector, rel_path))
        return findings

    def _check_single_char(self, collector: _NameCollector, rel_path: str) -> list[Finding]:
        findings = []
        exempt = collector._loop_targets | collector._comprehension_targets | {"_"}
        for name, line in collector.variables:
            if len(name) == 1 and name not in exempt:
                findings.append(
                    Finding(
                        file_path=rel_path,
                        line=line,
                        category=Category.naming,
                        severity=Severity.low,
                        title=f"Single-character variable name '{name}'",
                        description=(
                            f"Variable '{name}' is a single character. "
                            "Use a descriptive name to improve readability."
                        ),
                        suggested_fix="Rename variable to describe its purpose.",
                    )
                )
        return findings

    def _check_generic_names(self, collector: _NameCollector, rel_path: str) -> list[Finding]:
        findings = []
        name_counts: Counter = Counter()
        name_lines: dict[str, int] = {}
        for name, line in collector.variables:
            lower = name.lower()
            if lower in GENERIC_NAMES:
                name_counts[lower] += 1
                if lower not in name_lines:
                    name_lines[lower] = line

        for name, count in name_counts.items():
            if count >= 2:
                findings.append(
                    Finding(
                        file_path=rel_path,
                        line=name_lines[name],
                        category=Category.naming,
                        severity=Severity.low,
                        title=f"Generic variable name '{name}' used {count} times",
                        description=(
                            f"The generic name '{name}' is used {count} times in this file. "
                            "Use more descriptive names to improve clarity."
                        ),
                        suggested_fix="Use descriptive names that convey meaning.",
                    )
                )
        return findings

    def _check_casing_consistency(self, collector: _NameCollector, rel_path: str) -> list[Finding]:
        findings = []
        snake_count = 0
        camel_count = 0
        all_names = [(n, l) for n, l in collector.functions + collector.variables
                     if not n.startswith("_") and len(n) > 1]

        for name, _line in all_names:
            if "_" in name and name == name.lower():
                snake_count += 1
            elif re.match(r"^[a-z]+[A-Z]", name):
                camel_count += 1

        if snake_count > 0 and camel_count > 0:
            findings.append(
                Finding(
                    file_path=rel_path,
                    line=1,
                    category=Category.naming,
                    severity=Severity.medium,
                    title="Inconsistent naming convention",
                    description=(
                        f"File mixes snake_case ({snake_count} names) and "
                        f"camelCase ({camel_count} names). Pick one convention."
                    ),
                    suggested_fix="Use consistent snake_case naming throughout the file.",
                )
            )
        return findings

    def _check_prefix_repetition(self, collector: _NameCollector, rel_path: str) -> list[Finding]:
        findings = []
        prefix_counts: Counter = Counter()
        for name, _line in collector.functions:
            parts = name.split("_")
            if len(parts) >= 2:
                prefix_counts[parts[0]] += 1

        for prefix, count in prefix_counts.items():
            if count >= 5:
                findings.append(
                    Finding(
                        file_path=rel_path,
                        line=1,
                        category=Category.naming,
                        severity=Severity.low,
                        title=f"Excessive prefix repetition: '{prefix}_*' ({count} functions)",
                        description=(
                            f"{count} functions start with '{prefix}_'. "
                            "Consider grouping them into a class or module."
                        ),
                        suggested_fix=(
                            f"Consider grouping '{prefix}_*' functions into a class or separate module."
                        ),
                    )
                )
        return findings
