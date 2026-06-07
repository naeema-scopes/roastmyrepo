"""CLI entry point for RoastMyRepo."""

from datetime import UTC, datetime

import click

from roastmyrepo import __version__
from roastmyrepo.formatter import format_report
from roastmyrepo.models import RepoReport
from roastmyrepo.pipeline import AnalysisPipeline
from roastmyrepo.repo import RepoError, clone_repo
from roastmyrepo.roaster import Roaster
from roastmyrepo.scorer import calculate_health_score


@click.command()
@click.argument("repo_url", required=False)
@click.option("--serious", is_flag=True, help="Disable editorial voice, plain findings only.")
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON.")
@click.option("--no-llm", is_flag=True, help="Run analysis without LLM commentary.")
@click.version_option(version=__version__)
def main(repo_url: str | None, serious: bool, json_output: bool, no_llm: bool) -> None:
    """RoastMyRepo - AI-powered code quality analyzer.

    Analyze a GitHub repository for code quality issues with editorial commentary.

    Usage: roastmyrepo <repo_url>
    """
    if not repo_url:
        click.echo("Error: Please provide a GitHub repository URL.")
        click.echo("Usage: roastmyrepo https://github.com/user/repo")
        raise SystemExit(1)

    click.echo(f"Analyzing {repo_url}...")

    try:
        with clone_repo(repo_url) as repo_path:
            pipeline = AnalysisPipeline()
            findings, warnings = pipeline.run(repo_path)
            health_score = calculate_health_score(findings)
            roaster = Roaster(serious=serious, no_llm=no_llm)
            roasts = roaster.roast(findings)

            report = RepoReport(
                repo_url=repo_url,
                health_score=health_score,
                roasts=roasts,
                warnings=warnings,
                summary=f"Found {len(findings)} issues.",
                analyzed_at=datetime.now(UTC),
            )

            output_format = "json" if json_output else "text"
            click.echo(format_report(report, output_format))
    except RepoError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
