import json

from breakagent.agent import AgentState
from breakagent.planners.llm import LLMPlanner


class _FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _FakeResponsesAPI:
    def __init__(self, output_text: str) -> None:
        self._output_text = output_text

    def create(self, **kwargs):  # noqa: ANN003
        return _FakeResponse(self._output_text)


class _FakeClient:
    def __init__(self, output_text: str) -> None:
        self.responses = _FakeResponsesAPI(output_text)


def test_llm_planner_falls_back_without_key_or_client():
    planner = LLMPlanner(module_order=["auth", "bola"], api_key="")
    state = AgentState(pending_modules=["auth", "bola"], budget_remaining=100)
    actions = planner.plan(state)

    assert len(actions) == 1
    assert actions[0].module == "auth"
    assert actions[0].reason == "llm_unavailable_fallback"


def test_llm_planner_uses_model_output_with_fake_client():
    payload = json.dumps({"module": "bola", "reason": "id_paths_detected"})
    planner = LLMPlanner(module_order=["auth", "bola"], client=_FakeClient(payload))
    state = AgentState(pending_modules=["auth", "bola"], budget_remaining=100)

    actions = planner.plan(state)
    assert len(actions) == 1
    assert actions[0].module == "bola"
    assert actions[0].reason.startswith("llm:")


def test_llm_planner_invalid_module_output_falls_back():
    payload = json.dumps({"module": "nonexistent", "reason": "bad"})
    planner = LLMPlanner(module_order=["auth", "bola"], client=_FakeClient(payload))
    state = AgentState(pending_modules=["auth", "bola"], budget_remaining=100)

    actions = planner.plan(state)
    assert len(actions) == 1
    assert actions[0].module == "auth"
    assert actions[0].reason == "llm_invalid_module_fallback"
