"""Base analyzer abstract class."""

import os
from abc import ABC, abstractmethod

from roastmyrepo.models import Finding


class BaseAnalyzer(ABC):
    """Abstract base class for all code analyzers."""

    @abstractmethod
    def analyze(self, repo_path: str) -> list[Finding]:
        """Analyze a repository and return findings.

        Args:
            repo_path: Path to the root of the repository to analyze.

        Returns:
            List of Finding objects describing issues found.
        """

    def _iter_python_files(self, repo_path: str):
        """Yield absolute paths to all .py files in the repo."""
        for root, _dirs, files in os.walk(repo_path):
            # Skip hidden directories and __pycache__
            parts = root.split(os.sep)
            if any(p.startswith(".") or p == "__pycache__" for p in parts):
                continue
            for fname in sorted(files):
                if fname.endswith(".py"):
                    yield os.path.join(root, fname)
