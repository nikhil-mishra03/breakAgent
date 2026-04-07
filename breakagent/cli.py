from __future__ import annotations

import click
from rich.console import Console

from breakagent.models import BudgetConfig, ScanConfig, Severity
from breakagent.orchestrator import run_scan
from breakagent.parser import SpecParseError
from breakagent.report import write_html, write_json

console = Console()


@click.group()
def cli() -> None:
    """BreakAgent CLI."""


@cli.command()
@click.option("--spec", "spec_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--base-url", required=True, type=str)
@click.option("--previous-report", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--json-out", default="breakagent-report.json", show_default=True, type=click.Path(dir_okay=False, writable=True))
@click.option("--html-out", default="breakagent-report.html", show_default=True, type=click.Path(dir_okay=False, writable=True))
@click.option("--fail-on", type=click.Choice([s.value for s in Severity]), default=Severity.MEDIUM.value)
@click.option("--request-budget", default=500, show_default=True, type=int)
@click.option("--token-budget", default=15000, show_default=True, type=int)
@click.option("--cost-cap-usd", default=0.15, show_default=True, type=float)
@click.option("--timeout-seconds", default=180, show_default=True, type=int)
@click.option("--planner", type=click.Choice(["rule", "llm"]), default="rule", show_default=True)
@click.option("--llm-model", default="gpt-5-mini", show_default=True, type=str)
def scan(
    spec_path: str,
    base_url: str,
    previous_report: str | None,
    json_out: str,
    html_out: str,
    fail_on: str,
    request_budget: int,
    token_budget: int,
    cost_cap_usd: float,
    timeout_seconds: int,
    planner: str,
    llm_model: str,
) -> None:
    """Run MVP scan against an OpenAPI spec and base URL."""
    try:
        config = ScanConfig(
            spec_path=spec_path,
            base_url=base_url,
            previous_report=previous_report,
            planner=planner,
            llm_model=llm_model,
            fail_on=Severity(fail_on),
            budgets=BudgetConfig(
                request_budget=request_budget,
                token_budget=token_budget,
                cost_cap_usd=cost_cap_usd,
                timeout_seconds=timeout_seconds,
            ),
        )

        result = run_scan(config)
        write_json(result, json_out)
        write_html(result, html_out)

        console.print(f"[bold]BreakAgent scan completed[/bold] -> findings: {result.summary.total_findings}")
        console.print(f"JSON report: {json_out}")
        console.print(f"HTML report: {html_out}")

        raise SystemExit(result.summary.exit_code)
    except SpecParseError as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
