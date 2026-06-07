"""CLI output formatting with Rich."""

import json

from roastmyrepo.models import RepoReport, Severity


def _health_rating(score: int) -> str:
    """Convert numeric score to text rating."""
    if score >= 80:
        return "Healthy"
    elif score >= 60:
        return "Needs Work"
    elif score >= 40:
        return "Critical Condition"
    else:
        return "On Life Support"


def _severity_color(severity: Severity) -> str:
    """Map severity to Rich color name."""
    return {
        Severity.critical: "red",
        Severity.high: "yellow",
        Severity.medium: "cyan",
        Severity.low: "dim",
    }.get(severity, "white")


def format_report(report: RepoReport, output_format: str = "text") -> str:
    """Format a RepoReport for output.

    Args:
        report: The analysis report to format.
        output_format: 'text' for Rich-styled terminal output, 'json' for JSON.

    Returns:
        Formatted string.
    """
    if output_format == "json":
        return report.model_dump_json(indent=2)

    lines: list[str] = []
    score = report.health_score.overall
    rating = _health_rating(score)

    lines.append("")
    lines.append(f"  Repository: {report.repo_url}")
    lines.append(f"  Health Score: {score}/100 - {rating}")
    lines.append("")

    if report.warnings:
        for warning in report.warnings:
            lines.append(f"  WARNING: {warning}")
        lines.append("")

    if not report.roasts:
        lines.append("  No issues found. This code is suspiciously clean.")
        lines.append("")
        return "\n".join(lines)

    # Group by category
    by_category: dict[str, list] = {}
    for roast in report.roasts:
        cat = roast.finding.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(roast)

    for category, roasts in by_category.items():
        lines.append(f"  [{category.upper()}]")
        for roast in roasts:
            f = roast.finding
            severity = f.severity.value.upper()
            lines.append(f"    [{severity}] {f.title}")
            lines.append(f"      File: {f.file_path}:{f.line}")
            lines.append(f"      {f.description}")
            if roast.editorial:
                lines.append(f"      Editorial: {roast.editorial}")
            if roast.suggested_fix:
                lines.append(f"      Fix: {roast.suggested_fix}")
            lines.append("")

    # Summary
    lines.append("  SUMMARY")
    if report.summary:
        lines.append(f"  {report.summary}")
    total = len(report.roasts)
    critical = sum(1 for r in report.roasts if r.finding.severity == Severity.critical)
    high = sum(1 for r in report.roasts if r.finding.severity == Severity.high)
    lines.append(f"  Total issues: {total} ({critical} critical, {high} high)")
    lines.append(f"  Score: {score}/100 ({rating})")
    lines.append("")

    return "\n".join(lines)
