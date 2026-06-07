# RoastMyRepo

Analyzes Python repositories for code quality issues and delivers findings with dry, actionable feedback. Available as a CLI tool and REST API.

## What It Does

Point it at a public GitHub repo. It clones, analyzes, and tells you what's wrong — with suggestions for fixing it.

```
$ roastmyrepo https://github.com/user/some-repo

  RoastMyRepo — Analysis Report

  Health Score: 62/100 (Needs Work)

  Naming (medium) — handlers.py:47
    14 functions named handle_*. Your codebase reads like someone
    explaining their day using only the word "handled."
    Fix: Use names that describe what's actually being handled.

  Security (critical) — config.py:12
    Hardcoded database password. Bold move.
    Fix: Move credentials to environment variables.

  Dead Code (low) — utils.py:1
    os imported but never used. It's just sitting there. Watching.
    Fix: Remove unused import: import os
```

The `--serious` flag strips the editorial voice and gives you raw analysis with fixes only.

## Tech Stack

**Core:** Python, Click (CLI), FastAPI (API)

**Analysis:** AST parsing, radon (cyclomatic complexity), custom analyzers

**Output:** Rich (terminal formatting), JSON mode

## Installation

```bash
git clone https://github.com/naeema-scopes/roastmyrepo.git
cd roastmyrepo
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

### Analyze a repo

```bash
roastmyrepo https://github.com/user/repo
```

### Serious mode (no editorial voice)

```bash
roastmyrepo https://github.com/user/repo --serious
```

Same analysis, same fixes, no commentary. Useful as a straight linting tool.

### JSON output

```bash
roastmyrepo https://github.com/user/repo --json
```

Outputs structured JSON with health score, findings, and fixes. Pipe it to `jq` or use it programmatically.

### Skip LLM (static analysis only)

```bash
roastmyrepo https://github.com/user/repo --no-llm
```

Runs all analyzers without calling any external LLM API. Faster, free, fully local.

## REST API

Start the API server:

```bash
uvicorn roastmyrepo.api:app --host 0.0.0.0 --port 8000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Analyze a repo. Body: `{"url": "https://github.com/user/repo", "serious": false}` |
| `GET` | `/health` | Health check |

### Example

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/user/repo"}'
```

The API returns the full analysis as JSON. Timeout is 120 seconds — for large repos, use the CLI instead.

Rate limited to 10 requests/minute per IP.

## What It Analyzes

| Analyzer | What It Checks | Severity |
|----------|---------------|----------|
| **Complexity** | Cyclomatic complexity (radon), function length | Medium-Critical |
| **Naming** | Single-char vars, generic names, inconsistent casing, prefix repetition | Low-Medium |
| **Dead Code** | Unused imports, unreferenced variables | Low |
| **Security** | Hardcoded secrets, eval/exec, shell=True, SQL injection | High-Critical |
| **Testing** | Missing test directory, untested modules, low test ratio | Medium-Critical |
| **Dependencies** | Missing requirements, unpinned versions, no lock file | Low-High |

## Health Score

Starts at 100. Deducts per finding: critical (-10), high (-5), medium (-2), low (-1). Floor at 0.

| Score | Rating |
|-------|--------|
| 80-100 | Healthy |
| 50-79 | Needs Work |
| 20-49 | Critical Condition |
| 0-19 | On Life Support |

## Configuration

Set `LLM_API_KEY` and `LLM_PROVIDER` (anthropic or openai) as environment variables for LLM-powered commentary.

```bash
export LLM_PROVIDER=anthropic
export LLM_API_KEY=your-key-here
```

## Language Support

Currently supports Python repositories. The AST-based analyzers and radon operate on Python files only. Non-Python files are skipped. If less than 50% of files are Python, the tool warns that results may be limited.

## Running Tests

```bash
pip install -e ".[dev]"
pytest -v
```

53 tests covering all 6 analyzers, the pipeline, scorer, roaster, CLI output, and API endpoints.

## License

MIT
