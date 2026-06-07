"""Tests for dead code analyzer."""

from roastmyrepo.analyzers.dead_code import DeadCodeAnalyzer
from roastmyrepo.models import Category


def test_flags_unused_imports(messy_repo_path):
    """Test that unused imports are flagged."""
    analyzer = DeadCodeAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    import_findings = [
        f for f in findings
        if "unused import" in f.title.lower()
    ]
    assert len(import_findings) > 0


def test_flags_unused_variables(messy_repo_path):
    """Test that assigned-but-never-used variables are flagged."""
    analyzer = DeadCodeAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    var_findings = [
        f for f in findings
        if "unused variable" in f.title.lower()
    ]
    assert len(var_findings) > 0


def test_ignores_dunder_vars(messy_repo_path):
    """Test that __all__, __name__ etc. are not flagged."""
    analyzer = DeadCodeAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    dunder_findings = [
        f for f in findings
        if "__all__" in f.title or "__name__" in f.title
    ]
    assert len(dunder_findings) == 0


def test_ignores_underscore_vars(messy_repo_path):
    """Test that _ throwaway and _private vars are not flagged."""
    analyzer = DeadCodeAnalyzer()
    findings = analyzer.analyze(messy_repo_path)

    underscore_findings = [
        f for f in findings
        if f.title == "Unused variable: '_'" or f.title == "Unused variable: '_private'"
    ]
    assert len(underscore_findings) == 0
