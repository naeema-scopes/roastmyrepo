"""Tests for LLM roast generation."""

from roastmyrepo.models import Category, Finding, Severity
from roastmyrepo.roaster import Roaster


def _make_finding(**kwargs):
    defaults = {
        "file_path": "test.py",
        "line": 10,
        "category": Category.complexity,
        "severity": Severity.high,
        "title": "Complex function",
        "description": "Function is too complex.",
        "suggested_fix": "Break it up into smaller functions.",
    }
    defaults.update(kwargs)
    return Finding(**defaults)


def test_generates_editorial_for_finding():
    """Test that roaster returns a Roast object for each finding."""
    roaster = Roaster(serious=False, no_llm=True)
    findings = [_make_finding()]
    roasts = roaster.roast(findings)

    assert len(roasts) == 1
    assert roasts[0].finding == findings[0]


def test_generates_suggested_fix():
    """Test that suggested_fix comes from the finding's analyzer fix."""
    roaster = Roaster(serious=False, no_llm=True)
    findings = [_make_finding(suggested_fix="Refactor this function.")]
    roasts = roaster.roast(findings)

    assert roasts[0].suggested_fix == "Refactor this function."


def test_serious_mode_uses_analyzer_fixes():
    """Test that serious mode returns empty editorial and uses analyzer fix."""
    roaster = Roaster(serious=True)
    findings = [_make_finding(suggested_fix="Use smaller functions.")]
    roasts = roaster.roast(findings)

    assert roasts[0].editorial == ""
    assert roasts[0].suggested_fix == "Use smaller functions."


def test_handles_empty_findings():
    """Test that an empty findings list returns empty roasts."""
    roaster = Roaster(serious=False, no_llm=True)
    roasts = roaster.roast([])
    assert roasts == []


def test_batch_multiple_findings():
    """Test that multiple findings are all processed."""
    roaster = Roaster(serious=True)
    findings = [_make_finding() for _ in range(5)]
    roasts = roaster.roast(findings)

    assert len(roasts) == 5
