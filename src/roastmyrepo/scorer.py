"""Health score calculation."""

from roastmyrepo.models import Category, Finding, HealthScore, Severity

SEVERITY_DEDUCTIONS = {
    Severity.critical: 10,
    Severity.high: 5,
    Severity.medium: 2,
    Severity.low: 1,
}


def calculate_health_score(findings: list[Finding]) -> HealthScore:
    """Calculate repository health score from findings.

    Starts at 100, deducts points per finding based on severity.
    Floor at 0.

    Args:
        findings: List of findings from the analysis pipeline.

    Returns:
        HealthScore with overall score and per-category breakdown.
    """
    overall = 100
    category_deductions: dict[str, int] = {}

    for finding in findings:
        deduction = SEVERITY_DEDUCTIONS.get(finding.severity, 1)
        overall -= deduction

        cat_key = finding.category.value
        if cat_key not in category_deductions:
            category_deductions[cat_key] = 0
        category_deductions[cat_key] += deduction

    overall = max(0, overall)

    # Per-category scores: start at 100, subtract deductions
    breakdown: dict[str, int] = {}
    for cat in Category:
        deduction = category_deductions.get(cat.value, 0)
        breakdown[cat.value] = max(0, 100 - deduction)

    return HealthScore(overall=overall, breakdown=breakdown)
