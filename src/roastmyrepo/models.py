"""Data models for RoastMyRepo analysis results."""

from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    """Analysis finding categories."""

    complexity = "complexity"
    naming = "naming"
    dead_code = "dead_code"
    security = "security"
    testing = "testing"
    dependencies = "dependencies"


class Severity(str, Enum):
    """Finding severity levels."""

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Finding(BaseModel):
    """A single code quality finding from an analyzer."""

    file_path: str
    line: int
    category: Category
    severity: Severity
    title: str
    description: str
    code_snippet: Optional[str] = None
    suggested_fix: str = ""


class Roast(BaseModel):
    """A finding paired with editorial commentary."""

    finding: Finding
    editorial: str = ""
    suggested_fix: str = ""


class HealthScore(BaseModel):
    """Overall repository health score."""

    overall: int = Field(ge=0, le=100, default=100)
    breakdown: dict[str, int] = Field(default_factory=dict)


class RepoReport(BaseModel):
    """Complete analysis report for a repository."""

    repo_url: str
    health_score: HealthScore
    roasts: list[Roast] = Field(default_factory=list)
    summary: str = ""
    warnings: list[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
