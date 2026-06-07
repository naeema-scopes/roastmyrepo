"""Shared test fixtures for RoastMyRepo tests."""

import os
import subprocess
import tempfile

import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def fixtures_dir():
    """Return the path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def clean_repo_path(fixtures_dir):
    """Return the path to the clean repo fixture."""
    return os.path.join(fixtures_dir, "clean_repo")


@pytest.fixture
def messy_repo_path(fixtures_dir):
    """Return the path to the messy repo fixture."""
    return os.path.join(fixtures_dir, "messy_repo")


@pytest.fixture
def insecure_repo_path(fixtures_dir):
    """Return the path to the insecure repo fixture."""
    return os.path.join(fixtures_dir, "insecure_repo")


@pytest.fixture
def js_repo_path(fixtures_dir):
    """Return the path to the JavaScript repo fixture."""
    return os.path.join(fixtures_dir, "js_repo")


@pytest.fixture
def local_bare_repo():
    """Create a local bare git repo for clone tests.

    This avoids hitting the network during tests.
    """
    tmp_dir = tempfile.mkdtemp(prefix="roastmyrepo_test_bare_")
    bare_path = os.path.join(tmp_dir, "test.git")

    # Create bare repo
    subprocess.run(["git", "init", "--bare", bare_path], check=True, capture_output=True)

    # Create a working clone to seed commits
    work_path = os.path.join(tmp_dir, "work")
    subprocess.run(["git", "clone", bare_path, work_path], check=True, capture_output=True)

    # Add a commit
    test_file = os.path.join(work_path, "hello.py")
    with open(test_file, "w") as f:
        f.write('print("hello")\n')

    subprocess.run(["git", "-C", work_path, "add", "."], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", work_path, "-c", "user.name=Test", "-c", "user.email=test@test.com",
         "commit", "-m", "Initial commit"],
        check=True, capture_output=True,
    )
    subprocess.run(["git", "-C", work_path, "push"], check=True, capture_output=True)

    yield bare_path

    # Cleanup
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
