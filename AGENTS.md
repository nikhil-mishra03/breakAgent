# Repository Guidelines

## Project Structure & Module Organization
- Core package: `breakagent/`
  - `cli.py`: CLI entrypoint (`breakagent scan ...`)
  - `orchestrator.py`: scan pipeline orchestration
  - `agent.py`: agent loop (`plan -> execute -> analyze -> adapt -> diagnose`)
  - `parser.py`: OpenAPI parsing
  - `models.py`: shared Pydantic models/config
  - `scoring.py`: severity counts and exit-code mapping
  - `report.py`, `verify.py`: report output and `--previous-report` logic
  - `modules/`: domain modules (`security.py`, `robustness.py`, `quality.py`)
  - `planners/`: planning strategies (`rule.py`, `llm.py`)
- Tests: `tests/` (unit/integration-style CLI tests)
- Fixtures: `fixtures/` (sample OpenAPI specs)
- Docs: `docs/` (`TRADEOFFS.md`, `INTERVIEW_CHEATSHEET.md`)

## Build, Test, and Development Commands
- Install dev environment:
  - `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'`
- Run tests:
  - `.venv/bin/pytest`
- Run scanner locally:
  - `.venv/bin/breakagent scan --spec fixtures/openapi.json --base-url http://localhost:8000`
- Run LLM planner mode (OpenAI SDK):
  - `OPENAI_API_KEY=... .venv/bin/breakagent scan --spec fixtures/openapi.json --base-url http://localhost:8000 --planner llm --llm-model gpt-5-mini`
- Generate explicit outputs:
  - `.venv/bin/breakagent scan ... --json-out /tmp/report.json --html-out /tmp/report.html`

## Coding Style & Naming Conventions
- Language: Python 3.10+
- Style: explicit, readable, minimal abstractions; avoid clever indirection.
- Naming:
  - modules/files: `snake_case.py`
  - classes: `PascalCase`
  - functions/variables: `snake_case`
  - constants: `UPPER_SNAKE_CASE`
- Keep module contracts DRY; shared logic belongs in common files, not duplicated across module implementations.

## Testing Guidelines
- Framework: `pytest` (+ `pytest-cov` installed in dev extras).
- Test files: `tests/test_*.py`; test names: `test_*`.
- Add tests for every changed code path (happy path, edge cases, and error paths).
- For regressions, add a dedicated regression test before merge.

## Commit & Pull Request Guidelines
- No stable git history exists yet in this workspace; use Conventional Commits going forward:
  - `feat: ...`, `fix: ...`, `test: ...`, `docs: ...`, `refactor: ...`
- PRs should include:
  - summary of behavior changes
  - test evidence (`pytest` output)
  - sample CLI command(s) used
  - doc updates (`README.md`, `CLAUDE.md`, `docs/*`) when behavior changes

## Security & Configuration Notes
- Treat API responses as untrusted input.
- Never log raw secrets/tokens.
- Preserve sandbox/budget assumptions from `CLAUDE.md`.
- LLM planner uses OpenAI Python SDK directly (no LangChain/LangGraph); keep API keys in env vars only (`OPENAI_API_KEY`).
- Keep MVP boundary intact: no spec-less discovery/dashboard/memory features in v1 changes.
