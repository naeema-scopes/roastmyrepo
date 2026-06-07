"""LLM roast generation with editorial voice."""

from roastmyrepo.models import Finding, Roast


class Roaster:
    """Generates editorial commentary for code findings.

    In serious mode or when no LLM is available, returns findings
    with the analyzer's template-based suggested fixes and no editorial.
    """

    def __init__(self, serious: bool = False, no_llm: bool = True):
        self.serious = serious
        self.no_llm = no_llm

    def roast(self, findings: list[Finding]) -> list[Roast]:
        """Generate roasts for a list of findings.

        Args:
            findings: List of findings to add commentary to.

        Returns:
            List of Roast objects with editorial and fix suggestions.
        """
        if self.serious or self.no_llm:
            return self._serious_roasts(findings)

        # LLM mode: stub for now, falls back to serious mode
        return self._serious_roasts(findings)

    def _serious_roasts(self, findings: list[Finding]) -> list[Roast]:
        """Generate plain roasts without editorial commentary."""
        roasts = []
        for finding in findings:
            roasts.append(
                Roast(
                    finding=finding,
                    editorial="",
                    suggested_fix=finding.suggested_fix,
                )
            )
        return roasts
