"""Analyzers for code quality detection."""

from roastmyrepo.analyzers.complexity import ComplexityAnalyzer
from roastmyrepo.analyzers.dead_code import DeadCodeAnalyzer
from roastmyrepo.analyzers.dependencies import DependenciesAnalyzer
from roastmyrepo.analyzers.naming import NamingAnalyzer
from roastmyrepo.analyzers.security import SecurityAnalyzer
from roastmyrepo.analyzers.testing import TestingAnalyzer

ALL_ANALYZERS = [
    ComplexityAnalyzer,
    NamingAnalyzer,
    DeadCodeAnalyzer,
    SecurityAnalyzer,
    TestingAnalyzer,
    DependenciesAnalyzer,
]

__all__ = [
    "ComplexityAnalyzer",
    "NamingAnalyzer",
    "DeadCodeAnalyzer",
    "SecurityAnalyzer",
    "TestingAnalyzer",
    "DependenciesAnalyzer",
    "ALL_ANALYZERS",
]
