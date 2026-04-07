from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Protocol

from breakagent.models import Endpoint, Finding, ScanConfig, Severity
from breakagent.modules.base import BaseModule


@dataclass
class AgentAction:
    kind: str
    module: str
    reason: str


@dataclass
class AgentState:
    pending_modules: list[str]
    budget_remaining: int
    completed_modules: list[str] = field(default_factory=list)
    module_findings: dict[str, int] = field(default_factory=dict)
    hypotheses: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)


class Planner(Protocol):
    def plan(self, state: AgentState) -> list[AgentAction]:
        ...


class AgentRunner:
    def __init__(self, planner: Planner, modules: dict[str, BaseModule]) -> None:
        self.planner = planner
        self.modules = modules

    def run(
        self,
        state: AgentState,
        endpoints: list[Endpoint],
        config: ScanConfig,
        deadline: float,
    ) -> tuple[list[Finding], list[str]]:
        findings: list[Finding] = []
        while state.pending_modules:
            state.trace.append("phase=plan")
            actions = self.planner.plan(state)
            if not actions:
                break

            for action in actions:
                if action.kind != "run_module":
                    continue
                module = self.modules.get(action.module)
                if module is None or action.module not in state.pending_modules:
                    continue

                if time.monotonic() >= deadline:
                    state.trace.append("budget=timeout_exceeded")
                    state.pending_modules.clear()
                    break
                if state.budget_remaining <= 0:
                    state.trace.append("budget=request_budget_exceeded")
                    state.pending_modules.clear()
                    break

                state.trace.append(f"phase=execute module={action.module}")
                module_findings = module.run(endpoints, config)
                findings.extend(module_findings)

                state.trace.append(f"phase=analyze module={action.module} findings={len(module_findings)}")
                state.module_findings[action.module] = len(module_findings)
                state.evidence.append(
                    f"module={action.module} findings={len(module_findings)} "
                    f"high_or_critical={sum(1 for f in module_findings if f.severity in {Severity.HIGH, Severity.CRITICAL})}"
                )

                state.completed_modules.append(action.module)
                state.pending_modules.remove(action.module)
                state.budget_remaining = max(0, state.budget_remaining - len(endpoints))
                state.trace.append(
                    f"phase=adapt module={action.module} pending={len(state.pending_modules)} "
                    f"budget_remaining={state.budget_remaining}"
                )

        state.trace.append("phase=diagnose")
        return findings, state.trace
