"""Git repository cloning with security measures and automatic cleanup."""

import os
import re
import shutil
import tempfile
from contextlib import contextmanager

import git


class RepoError(Exception):
    """Error during repository operations."""


_GITHUB_HTTPS_PATTERN = re.compile(r"^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$")


def _validate_url(url: str) -> None:
    """Validate that the URL is a valid GitHub HTTPS URL."""
    if not isinstance(url, str) or not url.strip():
        raise RepoError("Repository URL must be a non-empty string.")

    if url.startswith("ssh://") or url.startswith("git@"):
        raise RepoError(
            f"SSH URLs are not supported: {url}. Use HTTPS: https://github.com/owner/repo"
        )

    if not _GITHUB_HTTPS_PATTERN.match(url):
        raise RepoError(
            f"Invalid GitHub URL: {url}. "
            "Only public GitHub HTTPS URLs are supported: https://github.com/owner/repo"
        )


@contextmanager
def clone_repo(url: str, timeout: int = 60):
    """Clone a GitHub repository to a temporary directory.

    Args:
        url: GitHub HTTPS URL to clone.
        timeout: Maximum seconds to wait for clone (default 60).

    Yields:
        Path to the cloned repository directory.

    Raises:
        RepoError: If URL is invalid or clone fails.
    """
    _validate_url(url)

    tmp_dir = tempfile.mkdtemp(prefix="roastmyrepo_")
    try:
        env = os.environ.copy()
        env["GIT_TEMPLATE_DIR"] = ""

        try:
            git.Repo.clone_from(
                url,
                tmp_dir,
                depth=1,
                env=env,
                kill_after_timeout=timeout,
            )
        except git.GitCommandError as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "could not read" in error_msg:
                raise RepoError(
                    f"Repository requires authentication: {url}. "
                    "Only public repositories are supported."
                ) from e
            if "timeout" in error_msg or "alarm" in error_msg:
                raise RepoError(
                    f"Clone timed out after {timeout} seconds for {url}."
                ) from e
            raise RepoError(f"Failed to clone repository: {e}") from e

        yield tmp_dir
    finally:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)
