"""Dependency hygiene analysis."""

import os
import re

from roastmyrepo.analyzers.base import BaseAnalyzer
from roastmyrepo.models import Category, Finding, Severity

LOCK_FILES = [
    "requirements.lock",
    "poetry.lock",
    "Pipfile.lock",
    "pdm.lock",
    "uv.lock",
]

DEP_FILES = [
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
]


class DependenciesAnalyzer(BaseAnalyzer):
    """Analyzes dependency hygiene."""

    def analyze(self, repo_path: str) -> list[Finding]:
        findings: list[Finding] = []

        # Check for dependency file existence
        found_dep_files = [f for f in DEP_FILES if os.path.isfile(os.path.join(repo_path, f))]

        if not found_dep_files:
            findings.append(
                Finding(
                    file_path=".",
                    line=0,
                    category=Category.dependencies,
                    severity=Severity.high,
                    title="No dependency file found",
                    description=(
                        "No requirements.txt, pyproject.toml, or setup.py found. "
                        "Dependencies should be declared explicitly."
                    ),
                    suggested_fix=(
                        "Add a requirements.txt or declare dependencies in pyproject.toml."
                    ),
                )
            )
            return findings

        # Check requirements.txt for pinning issues
        req_path = os.path.join(repo_path, "requirements.txt")
        if os.path.isfile(req_path):
            findings.extend(self._check_requirements(req_path))

        # Check for lock file
        has_lock = any(os.path.isfile(os.path.join(repo_path, lf)) for lf in LOCK_FILES)
        if not has_lock:
            findings.append(
                Finding(
                    file_path=".",
                    line=0,
                    category=Category.dependencies,
                    severity=Severity.low,
                    title="No lock file found",
                    description=(
                        "No dependency lock file (e.g., poetry.lock, requirements.lock) found. "
                        "Lock files ensure reproducible builds."
                    ),
                    suggested_fix="Generate a lock file for reproducible dependency resolution.",
                )
            )

        return findings

    def _check_requirements(self, req_path: str) -> list[Finding]:
        findings = []
        try:
            with open(req_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            return findings

        non_empty = [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("-")
        ]

        if not non_empty:
            findings.append(
                Finding(
                    file_path="requirements.txt",
                    line=1,
                    category=Category.dependencies,
                    severity=Severity.medium,
                    title="Empty requirements file",
                    description="requirements.txt exists but contains no dependencies.",
                    suggested_fix="Add project dependencies to requirements.txt.",
                )
            )
            return findings

        for lineno, line in enumerate(non_empty, 1):
            # Strip extras markers like [security]
            dep = re.split(r"[;\[]", line)[0].strip()
            if not dep:
                continue

            # Check for unpinned dependencies (no version specifier at all)
            if not re.search(r"[><=!~]", dep):
                findings.append(
                    Finding(
                        file_path="requirements.txt",
                        line=lineno,
                        category=Category.dependencies,
                        severity=Severity.medium,
                        title=f"Unpinned dependency: {dep}",
                        description=f"Dependency '{dep}' has no version specifier.",
                        suggested_fix=f"Pin dependency: {dep}>=X.Y",
                    )
                )
            # Check for exact pin with no range
            elif re.match(r"^[\w\-\.]+==[\d\.]+$", dep):
                findings.append(
                    Finding(
                        file_path="requirements.txt",
                        line=lineno,
                        category=Category.dependencies,
                        severity=Severity.medium,
                        title=f"Inflexible version pin: {dep}",
                        description=(
                            f"Dependency '{dep}' is pinned to an exact version. "
                            "Consider using version ranges for flexibility."
                        ),
                        suggested_fix="Use version ranges instead of exact pins for flexibility.",
                    )
                )

        return findings
