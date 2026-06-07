"""Dead code detection: unused imports and variables via AST."""

import ast
import os

from roastmyrepo.analyzers.base import BaseAnalyzer
from roastmyrepo.models import Category, Finding, Severity


class _UsageCollector(ast.NodeVisitor):
    """Collect all Name references in an AST."""

    def __init__(self):
        self.used_names: set[str] = set()

    def visit_Name(self, node):
        self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # Track the root name in attribute chains like `os.path.join`
        if isinstance(node.value, ast.Name):
            self.used_names.add(node.value.id)
        self.generic_visit(node)


class DeadCodeAnalyzer(BaseAnalyzer):
    """Detects unused imports and variables."""

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

            findings.extend(self._check_unused_imports(tree, rel_path))
            findings.extend(self._check_unused_variables(tree, source, rel_path))
        return findings

    def _check_unused_imports(self, tree: ast.AST, rel_path: str) -> list[Finding]:
        findings = []
        imports: list[tuple[str, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split(".")[0]
                    imports.append((name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    name = alias.asname if alias.asname else alias.name
                    imports.append((name, node.lineno))

        # Collect all name usages
        collector = _UsageCollector()
        collector.visit(tree)

        # Check each import against usages (excluding the import node's own Name)
        for name, line in imports:
            if name.startswith("_"):
                continue
            # Count occurrences: an import creates one Name node, so if used elsewhere
            # we need to check if the name appears in non-import contexts
            usage_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == name:
                    # Check if this Name node is NOT part of an import statement
                    if node.lineno != line:
                        usage_count += 1
                elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    if node.value.id == name and node.value.lineno != line:
                        usage_count += 1

            if usage_count == 0:
                findings.append(
                    Finding(
                        file_path=rel_path,
                        line=line,
                        category=Category.dead_code,
                        severity=Severity.low,
                        title=f"Unused import: '{name}'",
                        description=f"Import '{name}' is never used in this file.",
                        suggested_fix=f"Remove unused import: `import {name}`",
                    )
                )
        return findings

    def _check_unused_variables(self, tree: ast.AST, source: str, rel_path: str) -> list[Finding]:
        findings = []
        assignments: list[tuple[str, int]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        assignments.append((name, node.lineno))

        # Collect all name references
        collector = _UsageCollector()
        collector.visit(tree)

        for name, line in assignments:
            # Skip dunder variables and underscore throwaway
            if name.startswith("__") and name.endswith("__"):
                continue
            if name == "_":
                continue
            if name.startswith("_"):
                continue

            # Count how many times this name is referenced (excluding the assignment line itself)
            ref_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == name and node.lineno != line:
                    ref_count += 1

            if ref_count == 0:
                findings.append(
                    Finding(
                        file_path=rel_path,
                        line=line,
                        category=Category.dead_code,
                        severity=Severity.low,
                        title=f"Unused variable: '{name}'",
                        description=f"Variable '{name}' is assigned but never used.",
                        suggested_fix=f"Remove or use the variable `{name}`.",
                    )
                )
        return findings
