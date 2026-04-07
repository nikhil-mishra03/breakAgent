from breakagent.agent import AgentState
from breakagent.planners import RulePlanner


def test_rule_planner_uses_configured_order():
    planner = RulePlanner(module_order=["auth", "bola", "injection"])
    state = AgentState(pending_modules=["auth", "bola", "injection"], budget_remaining=100)

    actions = planner.plan(state)
    assert len(actions) == 1
    assert actions[0].module == "auth"
    assert actions[0].reason == "deterministic_order"


def test_rule_planner_prioritizes_injection_after_bola_signal():
    planner = RulePlanner(module_order=["auth", "bola", "edgecase", "injection"])
    state = AgentState(
        pending_modules=["edgecase", "injection"],
        budget_remaining=100,
        module_findings={"bola": 2},
    )

    actions = planner.plan(state)
    assert len(actions) == 1
    assert actions[0].module == "injection"
    assert actions[0].reason == "bola_signal_detected"
