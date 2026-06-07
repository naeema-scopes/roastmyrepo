"""Tests for security analyzer."""

from roastmyrepo.analyzers.security import SecurityAnalyzer
from roastmyrepo.models import Category, Severity


def test_flags_hardcoded_secrets(insecure_repo_path):
    """Test that hardcoded API keys and passwords are flagged."""
    analyzer = SecurityAnalyzer()
    findings = analyzer.analyze(insecure_repo_path)

    secret_findings = [
        f for f in findings
        if "hardcoded" in f.title.lower()
    ]
    assert len(secret_findings) > 0
    # All secrets should be critical severity
    assert all(f.severity == Severity.critical for f in secret_findings)


def test_flags_sql_formatting(insecure_repo_path):
    """Test that SQL queries with f-strings or .format() are flagged."""
    analyzer = SecurityAnalyzer()
    findings = analyzer.analyze(insecure_repo_path)

    sql_findings = [
        f for f in findings
        if "sql injection" in f.title.lower()
    ]
    assert len(sql_findings) > 0


def test_flags_eval_exec(insecure_repo_path):
    """Test that eval() and exec() usage is flagged."""
    analyzer = SecurityAnalyzer()
    findings = analyzer.analyze(insecure_repo_path)

    eval_findings = [
        f for f in findings
        if "eval" in f.title.lower() or "exec" in f.title.lower()
    ]
    assert len(eval_findings) > 0
    assert all(f.severity == Severity.critical for f in eval_findings)


def test_flags_shell_injection(insecure_repo_path):
    """Test that subprocess with shell=True is flagged."""
    analyzer = SecurityAnalyzer()
    findings = analyzer.analyze(insecure_repo_path)

    shell_findings = [
        f for f in findings
        if "shell" in f.title.lower()
    ]
    assert len(shell_findings) > 0
