"""Tests for naming analyzer."""

from roastmyrepo.analyzers.naming import NamingAnalyzer
from roastmyrepo.models import Category


def test_flags_single_char_vars(messy_repo_path):
    """Test that single-char variables (outside loops/comprehensions) are flagged."""
    analyzer = NamingAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    single_char = [
        f for f in findings
        if "single-character" in f.title.lower()
    ]
    assert len(single_char) > 0


def test_flags_generic_names(messy_repo_path):
    """Test that generic names like 'data', 'temp', 'result' are flagged."""
    analyzer = NamingAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    generic = [
        f for f in findings
        if "generic" in f.title.lower()
    ]
    assert len(generic) > 0


def test_flags_inconsistent_casing(messy_repo_path):
    """Test that mix of snake_case and camelCase is flagged."""
    analyzer = NamingAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    casing = [
        f for f in findings
        if "inconsistent" in f.title.lower()
    ]
    assert len(casing) > 0


def test_counts_name_repetition(messy_repo_path):
    """Test that 5+ functions with same prefix are flagged."""
    analyzer = NamingAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    repetition = [
        f for f in findings
        if "prefix repetition" in f.title.lower()
    ]
    assert len(repetition) > 0
    assert any("handle" in f.title.lower() for f in repetition)
