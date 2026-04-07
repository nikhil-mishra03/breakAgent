from __future__ import annotations

import json
import os
from typing import Any

from breakagent.agent import AgentAction, AgentState


class LLMPlanner:
    """Planner that uses OpenAI SDK and falls back to deterministic behavior."""

    def __init__(
        self,
        module_order: list[str],
        model: str = "gpt-5-mini",
        *,
        client: Any | None = None,
        api_key: str | None = None,
    ) -> None:
        self.module_order = module_order
        self.model = model
        self.client = client
        effective_key = os.getenv("OPENAI_API_KEY") if api_key is None else api_key
        self.enabled = bool(client) or bool(effective_key)

        if self.enabled and self.client is None:
            from openai import OpenAI

            self.client = OpenAI(api_key=effective_key)

    def _fallback(self, state: AgentState, reason: str) -> list[AgentAction]:
        for module_name in self.module_order:
            if module_name in state.pending_modules:
                return [AgentAction(kind="run_module", module=module_name, reason=reason)]
        if state.pending_modules:
            return [AgentAction(kind="run_module", module=state.pending_modules[0], reason=reason)]
        return []

    def plan(self, state: AgentState) -> list[AgentAction]:
        if not state.pending_modules:
            return []
        if not self.enabled:
            return self._fallback(state, "llm_unavailable_fallback")

        prompt = {
            "pending_modules": state.pending_modules,
            "completed_modules": state.completed_modules,
            "module_findings": state.module_findings,
            "budget_remaining": state.budget_remaining,
            "instruction": (
                "Choose exactly one module from pending_modules and return strict JSON "
                '{"module":"<name>","reason":"<short_reason>"}.'
            ),
        }

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a cautious API security planner. "
                            "Pick one next module from the provided pending_modules only."
                        ),
                    },
                    {"role": "user", "content": json.dumps(prompt)},
                ],
                max_output_tokens=120,
            )
            text = getattr(response, "output_text", "") or ""
            if not text:
                return self._fallback(state, "llm_empty_output_fallback")

            parsed = json.loads(text)
            module = parsed.get("module")
            reason = parsed.get("reason", "llm_selected")
            if module not in state.pending_modules:
                return self._fallback(state, "llm_invalid_module_fallback")
            return [AgentAction(kind="run_module", module=module, reason=f"llm:{reason}")]
        except Exception:
            return self._fallback(state, "llm_exception_fallback")
