# CLAUDE.md

This file defines project context and contribution rules for BreakAgent.

## Project

- Name: `BreakAgent`
- Goal: Adaptive AI agent that stress-tests APIs for security, robustness, and quality.
- MVP boundary: OpenAPI-driven CLI scanner with sandboxed execution, 6 test modules, diagnosis output, JSON/HTML reports, and `--previous-report` verification.
- Explicitly out of MVP: spec-less discovery, cross-scan memory/playbooks, multi-step chaining memory, live dashboard UI.

## Tech Stack

- Language: Python
- API framework (target app examples): FastAPI
- Agent orchestration: internal agent loop + planner interfaces (`rule` and `llm`)
- LLM SDK: OpenAI Python SDK (`openai`) for `llm` planner mode
- HTTP client: `httpx`
- CLI UX: Click + Rich
- Reporting: Jinja2 + structured JSON output
- Runtime isolation: Docker + network restrictions

## Repository Conventions

- Keep diffs minimal and explicit.
- Reuse shared module contracts/utilities; avoid per-module duplication.
- Prefer readable, boring solutions over clever abstractions.
- New abstractions require clear repeated need.

## Expected CLI Surface (MVP)

- `breakagent scan --spec <openapi.json> --base-url <url>`
- `breakagent scan --spec <openapi.json> --base-url <url> --previous-report <report.json>`

## Core MVP Modules

- Security: Auth, BOLA, Injection
- Robustness: EdgeCase, ErrorHandling
- Quality: Contract + ResponseQuality

## Safety and Trust Requirements

- All active scan traffic must run from sandboxed runtime.
- Enforce request/token/cost/time budgets.
- Treat API responses as untrusted input.
- Do not leak secrets/tokens in logs or reports.
- Preserve auditability for requests, responses, and agent decisions.

## Development Setup

Recommended local flow (adjust as implementation evolves):

1. Create virtualenv
2. Install dependencies
3. Run lint/type/test
4. Run scanner against local vulnerable demo API

## Commands

Use these canonical command intents as the project grows:

- Install: `pip install -e .[dev]`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy .`
- Tests: `pytest -q`
- Coverage: `pytest --cov=breakagent --cov-report=term-missing`
- LLM planner run: `breakagent scan --spec <spec> --base-url <url> --planner llm --llm-model gpt-5-mini`

If command names change, update this file in the same PR.

## Testing

Testing is non-negotiable. Every behavior change needs tests.

### Test Framework

- `pytest`
- `pytest-asyncio`
- `pytest-cov`
- HTTP mocking/tooling such as `respx`
- Docker-based integration tests for sandbox behavior

### Test Strategy

- Deterministic-by-default for CI:
  - Unit and mocked integration tests on PRs
  - No mandatory live model calls in default CI path
- Scheduled/triggered realism checks:
  - Nightly or release-candidate eval runs with live model/provider integration
  - Budget-capped and isolated from fast PR checks
- Regression rule:
  - Any production regression gets a dedicated regression test before merge.

### Coverage Expectations

- 100% coverage target for changed code paths.
- Cover happy path, edge cases, and error paths.
- Add E2E coverage for critical flows:
  - full scan path
  - verify (`--previous-report`) path
  - CI gating behavior

## Performance and Reliability

- Use bounded adaptive concurrency (global + per-host caps).
- Backoff/retry policy for transient failures (429/5xx).
- Stream report/audit output where possible to avoid memory spikes.
- Fail safely and clearly when budgets/timeouts are exceeded.

## Security Review Checklist (for PRs)

- Are trust boundaries explicit for new code paths?
- Are sensitive values redacted in logs/reports?
- Is sandbox enforcement preserved?
- Are prompt-injection-like API outputs treated as untrusted text?
- Are failure modes tested (timeout, cap breach, malformed input)?
- If `--planner llm` is used: is `OPENAI_API_KEY` sourced from env only (never hardcoded)?

## Distribution (MVP Contract)

- Python package install path (primary)
- Container image distribution path (secondary)
- CI/CD workflows must build and publish release artifacts
- Supported platform matrix must be explicit in release docs

## Documentation Rules

When behavior changes, update in the same PR:

- `README.md` (user-facing usage)
- `CLAUDE.md` (engineering conventions)
- `TODOS.md` (deferred work with context)
- `docs/TRADEOFFS.md` (architecture decisions, risks, interview tradeoffs)
- `docs/INTERVIEW_CHEATSHEET.md` (1-page interview narrative and decision soundbites)
- Architecture/design docs under `~/.gstack/projects/breakAgent/` as needed

## Non-Goals for MVP

- Discovery-only scanning without OpenAPI input
- Persistent playbook memory and framework fingerprinting
- Web dashboard/live attack graph UX
- Full enterprise multi-tenant controls

## Working Agreement

- Optimize for correctness and trust before speed.
- Ship in small, reviewable increments.
- Keep product claims aligned with implemented behavior.
