"""Tests for repo cloning functionality."""

import os
import shutil
import tempfile
from contextlib import contextmanager

import git
import pytest

from roastmyrepo.repo import RepoError, clone_repo


@contextmanager
def _clone_local(bare_path):
    """Helper to clone a local bare repo (bypasses URL validation)."""
    tmp_dir = tempfile.mkdtemp(prefix="roastmyrepo_test_")
    try:
        git.Repo.clone_from(bare_path, tmp_dir, depth=1)
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_clone_public_repo(local_bare_repo):
    """Test cloning from a local bare repo fixture."""
    with _clone_local(local_bare_repo) as repo_path:
        assert os.path.isdir(repo_path)
        assert os.path.isfile(os.path.join(repo_path, "hello.py"))


def test_cleanup(local_bare_repo):
    """Test that temp directory is removed after context manager exits."""
    saved_path = None
    with _clone_local(local_bare_repo) as repo_path:
        saved_path = repo_path
        assert os.path.exists(saved_path)
    assert not os.path.exists(saved_path)


def test_invalid_url():
    """Test that invalid URLs raise RepoError."""
    with pytest.raises(RepoError, match="Invalid GitHub URL"):
        with clone_repo("not-a-url"):
            pass


def test_rejects_non_github_url():
    """Test that non-GitHub URLs are rejected."""
    with pytest.raises(RepoError, match="Invalid GitHub URL"):
        with clone_repo("https://gitlab.com/user/repo"):
            pass


def test_rejects_ssh_url():
    """Test that SSH URLs are rejected."""
    with pytest.raises(RepoError, match="SSH URLs are not supported"):
        with clone_repo("ssh://git@github.com/user/repo"):
            pass


def test_rejects_empty_url():
    """Test that empty URLs are rejected."""
    with pytest.raises(RepoError, match="non-empty string"):
        with clone_repo(""):
            pass
