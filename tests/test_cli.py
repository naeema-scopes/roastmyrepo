"""Tests for CLI output and formatting."""

import json

from roastmyrepo.formatter import format_report
from roastmyrepo.models import (
    Category,
    Finding,
    HealthScore,
    RepoReport,
    Roast,
    Severity,
)


def _make_report(score=75, roasts=None, warnings=None):
    """Helper to create a RepoReport."""
    if roasts is None:
        finding = Finding(
            file_path="app.py",
            line=10,
            category=Category.complexity,
            severity=Severity.high,
            title="Complex function",
            description="Function is too complex.",
            suggested_fix="Break it up.",
        )
        roasts = [Roast(finding=finding, editorial="", suggested_fix="Break it up.")]

    return RepoReport(
        repo_url="https://github.com/test/repo",
        health_score=HealthScore(overall=score, breakdown={"complexity": score}),
        roasts=roasts,
        warnings=warnings or [],
        summary="Test summary.",
    )


def test_text_output_includes_health_score():
    """Test that text output contains the health score."""
    report = _make_report(score=75)
    output = format_report(report, "text")

    assert "75/100" in output
    assert "Needs Work" in output


def test_text_output_severity_labels():
    """Test that severity labels appear in output."""
    report = _make_report()
    output = format_report(report, "text")

    assert "HIGH" in output


def test_json_output_valid():
    """Test that JSON output is valid parseable JSON."""
    report = _make_report()
    output = format_report(report, "json")

    parsed = json.loads(output)
    assert parsed["repo_url"] == "https://github.com/test/repo"
    assert parsed["health_score"]["overall"] == 75


def test_summary_section():
    """Test that output includes a summary section."""
    report = _make_report()
    output = format_report(report, "text")

    assert "SUMMARY" in output
    assert "Total issues" in output


def test_health_rating_categories():
    """Test health rating text for different score ranges."""
    assert "Healthy" in format_report(_make_report(score=90), "text")
    assert "Needs Work" in format_report(_make_report(score=65), "text")
    assert "Critical Condition" in format_report(_make_report(score=45), "text")
    assert "On Life Support" in format_report(_make_report(score=20), "text")
