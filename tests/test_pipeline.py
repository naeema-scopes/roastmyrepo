"""Tests for the analysis pipeline."""

from roastmyrepo.pipeline import AnalysisPipeline


def test_pipeline_runs_all_analyzers(messy_repo_path):
    """Test that all analyzers are called and findings are aggregated."""
    pipeline = AnalysisPipeline()
    findings, warnings = pipeline.run(messy_repo_path)

    assert len(findings) > 0
    # Should have findings from multiple categories
    categories = set(f.category.value for f in findings)
    assert len(categories) >= 2


def test_pipeline_deduplicates(messy_repo_path):
    """Test that duplicate findings are removed."""
    pipeline = AnalysisPipeline()
    findings, _ = pipeline.run(messy_repo_path)

    # Check no exact duplicates exist
    seen = set()
    for f in findings:
        key = (f.file_path, f.line, f.title)
        assert key not in seen, f"Duplicate finding: {key}"
        seen.add(key)


def test_pipeline_warns_non_python_repo(js_repo_path):
    """Test that pipeline warns when repo has mostly non-Python files."""
    pipeline = AnalysisPipeline()
    findings, warnings = pipeline.run(js_repo_path)

    assert any("non-Python" in w for w in warnings)


def test_non_python_repo_no_crash(js_repo_path):
    """Test that pipeline completes without errors on a JavaScript-only repo."""
    pipeline = AnalysisPipeline()
    findings, warnings = pipeline.run(js_repo_path)
    # Should not raise any exceptions
    assert isinstance(findings, list)
    assert isinstance(warnings, list)


def test_mixed_repo_analyzes_python_only(fixtures_dir):
    """Test that a repo with both Python and JS files only analyzes Python files."""
    import os
    import tempfile
    import shutil

    tmp = tempfile.mkdtemp()
    try:
        # Create mixed repo
        with open(os.path.join(tmp, "app.py"), "w") as f:
            f.write("import os\nimport sys\nprint('hello')\n")
        with open(os.path.join(tmp, "index.js"), "w") as f:
            f.write("console.log('hello');\n")

        pipeline = AnalysisPipeline()
        findings, warnings = pipeline.run(tmp)

        # Findings should only reference .py files
        for finding in findings:
            if finding.file_path != ".":
                assert finding.file_path.endswith(".py"), (
                    f"Non-Python file in findings: {finding.file_path}"
                )
    finally:
        shutil.rmtree(tmp)
