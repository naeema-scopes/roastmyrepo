"""Analysis pipeline that orchestrates all analyzers."""

import os

from roastmyrepo.analyzers import ALL_ANALYZERS
from roastmyrepo.models import Finding


class AnalysisPipeline:
    """Runs all analyzers and aggregates findings."""

    def __init__(self, analyzer_classes=None):
        self.analyzer_classes = analyzer_classes or ALL_ANALYZERS

    def run(self, repo_path: str) -> tuple[list[Finding], list[str]]:
        """Run all analyzers on the given repository.

        Args:
            repo_path: Path to the repository root.

        Returns:
            Tuple of (deduplicated findings sorted by severity, warnings list).
        """
        warnings: list[str] = []

        # Check Python file ratio
        py_ratio = self._python_file_ratio(repo_path)
        if py_ratio < 0.5:
            warnings.append(
                "This repo appears to be primarily non-Python. "
                "Analysis results may be limited."
            )

        all_findings: list[Finding] = []
        for analyzer_cls in self.analyzer_classes:
            analyzer = analyzer_cls()
            try:
                findings = analyzer.analyze(repo_path)
                all_findings.extend(findings)
            except Exception:
                # Don't let a single analyzer crash the pipeline
                continue

        # Deduplicate by (file_path, line, title)
        seen: set[tuple[str, int, str]] = set()
        unique: list[Finding] = []
        for f in all_findings:
            key = (f.file_path, f.line, f.title)
            if key not in seen:
                seen.add(key)
                unique.append(f)

        # Sort by severity (critical first), then file path
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        unique.sort(key=lambda f: (severity_order.get(f.severity.value, 4), f.file_path))

        return unique, warnings

    @staticmethod
    def _python_file_ratio(repo_path: str) -> float:
        """Calculate the ratio of Python files to total files."""
        total = 0
        python = 0
        for root, _dirs, files in os.walk(repo_path):
            parts = root.split(os.sep)
            if any(p.startswith(".") or p == "__pycache__" or p == "node_modules" for p in parts):
                continue
            for f in files:
                if f.startswith("."):
                    continue
                total += 1
                if f.endswith(".py"):
                    python += 1
        if total == 0:
            return 0.0
        return python / total
