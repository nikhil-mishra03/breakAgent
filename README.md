# BreakAgent

MVP scaffolding for an OpenAPI-driven CLI scanner.

## Quickstart

```bash
pip install -e .[dev]
breakagent scan --spec fixtures/openapi.json --base-url http://localhost:8000
```

## Planner Modes

- Rule planner (default, deterministic):
  ```bash
  breakagent scan --spec fixtures/openapi.json --base-url http://localhost:8000 --planner rule
  ```
- LLM planner (OpenAI SDK):
  ```bash
  OPENAI_API_KEY=... breakagent scan --spec fixtures/openapi.json --base-url http://localhost:8000 --planner llm --llm-model gpt-5-mini
  ```

If `OPENAI_API_KEY` is missing, `--planner llm` falls back to deterministic planning.

## Optional Markdown Summary

Generate an easy-to-read executive markdown summary from the JSON findings:

```bash
breakagent scan --spec fixtures/openapi.json --base-url http://localhost:8000 --md-summary
```

Optional overrides (not required):

```bash
--summary-model gpt-5-mini
--summary-max-tokens 1200
--summary-cost-cap-usd 0.03
```

If not provided, internal defaults are used.
