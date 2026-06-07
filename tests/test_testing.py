"""Tests for testing coverage gap analyzer."""

import os
import tempfile
import shutil

from roastmyrepo.analyzers.testing import TestingAnalyzer
from roastmyrepo.models import Category, Severity


def test_detects_no_test_directory():
    """Test that missing tests/ directory is flagged."""
    tmp = tempfile.mkdtemp()
    try:
        # Create a source file with no tests
        with open(os.path.join(tmp, "app.py"), "w") as f:
            f.write("print('hello')\n")

        analyzer = TestingAnalyzer()
        findings = analyzer.analyze(tmp)

        no_test = [f for f in findings if "no test directory" in f.title.lower()]
        assert len(no_test) > 0
        assert no_test[0].severity == Severity.critical
    finally:
        shutil.rmtree(tmp)


def test_detects_untested_modules(messy_repo_path):
    """Test that source modules with no corresponding test file are flagged."""
    analyzer = TestingAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    # messy_repo has no tests/ dir so it should flag "no test directory"
    # or it should find untested modules
    assert len(findings) > 0


def test_detects_low_test_ratio():
    """Test that low test-to-source ratio is flagged."""
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "tests"))
        # Create 4 source files and 1 test file
        for name in ["app.py", "utils.py", "models.py", "views.py"]:
            with open(os.path.join(tmp, name), "w") as f:
                f.write(f"# {name}\n")

        with open(os.path.join(tmp, "tests", "test_app.py"), "w") as f:
            f.write("def test_something(): pass\n")

        analyzer = TestingAnalyzer()
        findings = analyzer.analyze(tmp)

        ratio_findings = [f for f in findings if "ratio" in f.title.lower()]
        assert len(ratio_findings) > 0
    finally:
        shutil.rmtree(tmp)
