from __future__ import annotations

from breakagent.agent import AgentAction, AgentState


class RulePlanner:
    """Deterministic planner used for MVP and test stability."""

    def __init__(self, module_order: list[str]) -> None:
        self.module_order = module_order

    def plan(self, state: AgentState) -> list[AgentAction]:
        if not state.pending_modules:
            return []

        # Adaptive hint: after BOLA findings, prioritize injection checks if still pending.
        if state.module_findings.get("bola", 0) > 0 and "injection" in state.pending_modules:
            return [
                AgentAction(
                    kind="run_module",
                    module="injection",
                    reason="bola_signal_detected",
                )
            ]

        for module_name in self.module_order:
            if module_name in state.pending_modules:
                return [
                    AgentAction(
                        kind="run_module",
                        module=module_name,
                        reason="deterministic_order",
                    )
                ]

        return [
            AgentAction(
                kind="run_module",
                module=state.pending_modules[0],
                reason="fallback_pending_head",
            )
        ]
