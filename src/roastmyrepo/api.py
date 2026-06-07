"""FastAPI application for RoastMyRepo."""

import time
from collections import defaultdict
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from roastmyrepo.formatter import format_report
from roastmyrepo.models import RepoReport
from roastmyrepo.pipeline import AnalysisPipeline
from roastmyrepo.repo import RepoError, clone_repo
from roastmyrepo.roaster import Roaster
from roastmyrepo.scorer import calculate_health_score

app = FastAPI(title="RoastMyRepo", version="0.1.0")

# Simple in-memory rate limiter
_rate_limits: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 10
RATE_WINDOW = 60


class AnalyzeRequest(BaseModel):
    url: str
    serious: bool = False


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    # Clean old entries
    _rate_limits[client_ip] = [
        t for t in _rate_limits[client_ip] if now - t < RATE_WINDOW
    ]

    if len(_rate_limits[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    _rate_limits[client_ip].append(now)
    response = await call_next(request)
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        with clone_repo(request.url) as repo_path:
            pipeline = AnalysisPipeline()
            findings, warnings = pipeline.run(repo_path)
            health_score = calculate_health_score(findings)
            roaster = Roaster(serious=request.serious, no_llm=True)
            roasts = roaster.roast(findings)

            report = RepoReport(
                repo_url=request.url,
                health_score=health_score,
                roasts=roasts,
                warnings=warnings,
                summary=f"Found {len(findings)} issues.",
                analyzed_at=datetime.now(UTC),
            )

            return report.model_dump()
    except RepoError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
