"""Tests for dependencies analyzer."""

import os
import tempfile
import shutil

from roastmyrepo.analyzers.dependencies import DependenciesAnalyzer
from roastmyrepo.models import Category, Severity


def test_no_requirements_file():
    """Test that missing dependency files are flagged."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "app.py"), "w") as f:
            f.write("print('hello')\n")

        analyzer = DependenciesAnalyzer()
        findings = analyzer.analyze(tmp)

        no_deps = [f for f in findings if "no dependency file" in f.title.lower()]
        assert len(no_deps) > 0
        assert no_deps[0].severity == Severity.high
    finally:
        shutil.rmtree(tmp)


def test_unpinned_dependencies(messy_repo_path):
    """Test that dependencies without version specifiers are flagged."""
    analyzer = DependenciesAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    unpinned = [f for f in findings if "unpinned" in f.title.lower()]
    assert len(unpinned) > 0


def test_empty_requirements():
    """Test that an empty requirements file is flagged."""
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "requirements.txt"), "w") as f:
            f.write("# nothing here\n")

        analyzer = DependenciesAnalyzer()
        findings = analyzer.analyze(tmp)

        empty = [f for f in findings if "empty" in f.title.lower()]
        assert len(empty) > 0
    finally:
        shutil.rmtree(tmp)


def test_pinned_without_ranges(messy_repo_path):
    """Test that exact version pins without ranges are flagged."""
    analyzer = DependenciesAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    inflexible = [f for f in findings if "inflexible" in f.title.lower()]
    assert len(inflexible) > 0


def test_no_lock_file(messy_repo_path):
    """Test that missing lock file is flagged."""
    analyzer = DependenciesAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    no_lock = [f for f in findings if "lock file" in f.title.lower()]
    assert len(no_lock) > 0
