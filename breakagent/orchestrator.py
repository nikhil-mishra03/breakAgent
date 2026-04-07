from __future__ import annotations

import time

from breakagent.agent import AgentRunner, AgentState
from breakagent.models import FindingStatus, ScanConfig, ScanResult, ScanSummary
from breakagent.modules import ALL_MODULES
from breakagent.parser import parse_openapi
from breakagent.planners import LLMPlanner, RulePlanner
from breakagent.report import read_json
from breakagent.scoring import compute_counts, exit_code
from breakagent.verify import apply_previous_report


def run_scan(config: ScanConfig) -> ScanResult:
    deadline = time.monotonic() + config.budgets.timeout_seconds

    endpoints = parse_openapi(config.spec_path)
    module_instances = [cls() for cls in ALL_MODULES]
    modules = {module.name: module for module in module_instances}
    module_order = [module.name for module in module_instances]

    state = AgentState(
        pending_modules=module_order.copy(),
        budget_remaining=config.budgets.request_budget,
        hypotheses=["openapi-driven-risk-assessment"],
    )
    if config.planner == "rule":
        planner = RulePlanner(module_order=module_order)
    elif config.planner == "llm":
        planner = LLMPlanner(module_order=module_order, model=config.llm_model)
    else:
        raise ValueError(f"Unsupported planner '{config.planner}'. Available planners: rule, llm")

    runner = AgentRunner(planner=planner, modules=modules)
    findings, agent_trace = runner.run(state=state, endpoints=endpoints, config=config, deadline=deadline)

    trace: list[str] = [
        f"planner={config.planner}",
        f"llm_model={config.llm_model}" if config.planner == "llm" else "",
        f"parsed_endpoints={len(endpoints)}",
        *agent_trace,
    ]
    trace = [line for line in trace if line]

    summary = ScanSummary(
        total_findings=len(findings),
        by_severity=compute_counts(findings),
        exit_code=exit_code(findings, config.fail_on),
    )

    result = ScanResult(
        base_url=str(config.base_url),
        findings=findings,
        summary=summary,
        budgets=config.budgets,
        trace=trace,
    )

    if config.previous_report:
        previous = read_json(config.previous_report)
        result = apply_previous_report(result, previous)
        result.summary.total_findings = len(result.findings)
        result.summary.by_severity = compute_counts(result.findings)
        open_findings = [f for f in result.findings if f.status != FindingStatus.FIXED]
        result.summary.exit_code = exit_code(open_findings, config.fail_on)

    return result
