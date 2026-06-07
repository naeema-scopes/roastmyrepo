"""Tests for health score calculation."""

from roastmyrepo.models import Category, Finding, Severity
from roastmyrepo.scorer import calculate_health_score


def _make_finding(category=Category.complexity, severity=Severity.low):
    """Helper to create a Finding."""
    return Finding(
        file_path="test.py",
        line=1,
        category=category,
        severity=severity,
        title="Test finding",
        description="Test description",
    )


def test_health_score_perfect():
    """Test that a clean repo scores 100."""
    score = calculate_health_score([])
    assert score.overall == 100


def test_health_score_terrible():
    """Test that many issues result in a low score."""
    findings = [
        _make_finding(severity=Severity.critical) for _ in range(15)
    ]
    score = calculate_health_score(findings)
    assert score.overall == 0


def test_score_breakdown():
    """Test that per-category scores are correct."""
    findings = [
        _make_finding(category=Category.complexity, severity=Severity.high),
        _make_finding(category=Category.complexity, severity=Severity.high),
        _make_finding(category=Category.security, severity=Severity.critical),
    ]
    score = calculate_health_score(findings)

    assert score.breakdown["complexity"] == 90  # 100 - 5 - 5
    assert score.breakdown["security"] == 90  # 100 - 10
    assert score.breakdown["naming"] == 100  # no findings


def test_score_floor_at_zero():
    """Test that score never goes below 0."""
    findings = [
        _make_finding(severity=Severity.critical) for _ in range(20)
    ]
    score = calculate_health_score(findings)
    assert score.overall == 0


def test_severity_deductions():
    """Test correct deductions per severity level."""
    # One of each
    findings = [
        _make_finding(severity=Severity.critical),
        _make_finding(severity=Severity.high),
        _make_finding(severity=Severity.medium),
        _make_finding(severity=Severity.low),
    ]
    score = calculate_health_score(findings)
    # 100 - 10 - 5 - 2 - 1 = 82
    assert score.overall == 82
