"""Tests for complexity analyzer."""

from roastmyrepo.analyzers.complexity import ComplexityAnalyzer
from roastmyrepo.models import Category, Severity


def test_flags_high_complexity(messy_repo_path):
    """Test that functions with CC > 10 are flagged."""
    analyzer = ComplexityAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    complexity_findings = [
        f for f in findings
        if f.category == Category.complexity and "cyclomatic complexity" in f.title.lower()
    ]
    assert len(complexity_findings) > 0
    # mega_function should be flagged
    assert any("mega_function" in f.title for f in complexity_findings)


def test_flags_long_function(messy_repo_path):
    """Test that functions with 50+ lines are flagged."""
    analyzer = ComplexityAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    long_findings = [
        f for f in findings
        if f.category == Category.complexity and "long function" in f.title.lower()
    ]
    assert len(long_findings) > 0
    assert any("long_function_example" in f.title for f in long_findings)


def test_ignores_simple_functions(clean_repo_path):
    """Test that simple functions are not flagged."""
    analyzer = ComplexityAnalyzer()
    findings = analyzer.analyze(clean_repo_path)

    # Clean repo has only simple functions
    assert len(findings) == 0


def test_reports_correct_line_numbers(messy_repo_path):
    """Test that findings point to actual function locations."""
    analyzer = ComplexityAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    for finding in findings:
        assert finding.line > 0
        assert finding.file_path.endswith(".py")
