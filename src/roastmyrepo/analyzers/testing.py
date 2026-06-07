"""Test coverage gap detection."""

import os

from roastmyrepo.analyzers.base import BaseAnalyzer
from roastmyrepo.models import Category, Finding, Severity


class TestingAnalyzer(BaseAnalyzer):
    """Detects test coverage gaps by analyzing file structure."""

    def analyze(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []

        # Gather source files (non-test .py files)
        source_files = []
        test_files = []

        for filepath in self._iter_python_files(repo_path):
            rel_path = os.path.relpath(filepath, repo_path)
            basename = os.path.basename(rel_path)

            if basename.startswith("test_") or basename.endswith("_test.py"):
                test_files.append(rel_path)
            elif basename == "__init__.py" or basename == "conftest.py":
                continue
            elif basename == "setup.py":
                continue
            else:
                source_files.append(rel_path)

        # Check for tests directory
        has_tests_dir = any(
            d in os.listdir(repo_path)
            for d in ("tests", "test")
            if os.path.isdir(os.path.join(repo_path, d))
        )

        if not has_tests_dir and not test_files:
            findings.append(
                Finding(
                    file_path=".",
                    line=0,
                    category=Category.testing,
                    severity=Severity.critical,
                    title="No test directory found",
                    description="No tests/ directory or test files found in this repository.",
                    suggested_fix="Create a tests/ directory and add test files.",
                )
            )
            return findings

        if not source_files:
            return findings

        # Check test-to-source ratio
        ratio = len(test_files) / len(source_files) if source_files else 1.0
        if ratio < 0.5:
            findings.append(
                Finding(
                    file_path=".",
                    line=0,
                    category=Category.testing,
                    severity=Severity.high,
                    title=f"Low test-to-source ratio ({ratio:.0%})",
                    description=(
                        f"Only {len(test_files)} test files for {len(source_files)} source files "
                        f"({ratio:.0%} ratio). Aim for at least 50%."
                    ),
                    suggested_fix="Add more test files to improve coverage.",
                )
            )

        # Check for untested modules
        test_basenames = set()
        for tf in test_files:
            base = os.path.basename(tf)
            if base.startswith("test_"):
                test_basenames.add(base[5:])  # remove "test_" prefix
            elif base.endswith("_test.py"):
                test_basenames.add(base[:-8] + ".py")

        for src in source_files:
            base = os.path.basename(src)
            if base not in test_basenames:
                findings.append(
                    Finding(
                        file_path=src,
                        line=0,
                        category=Category.testing,
                        severity=Severity.medium,
                        title=f"No test file for '{base}'",
                        description=f"Source file '{src}' has no corresponding test file.",
                        suggested_fix=f"Add test file: test_{base} for {base}",
                    )
                )

        return findings
