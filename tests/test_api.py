"""Tests for FastAPI API."""

import pytest
from fastapi.testclient import TestClient

from roastmyrepo.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_health(client):
    """Test that GET /health returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_invalid_url(client):
    """Test that invalid repo URLs return 400."""
    response = client.post("/analyze", json={"url": "not-a-url"})
    assert response.status_code == 400


def test_post_analyze_invalid_ssh(client):
    """Test that SSH URLs return 400."""
    response = client.post("/analyze", json={"url": "ssh://git@github.com/user/repo"})
    assert response.status_code == 400
