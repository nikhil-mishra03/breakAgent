from breakagent.models import ScanConfig
from breakagent.orchestrator import run_scan


def test_run_scan_returns_result_with_trace():
    cfg = ScanConfig(spec_path="fixtures/openapi.json", base_url="http://localhost:8000")
    result = run_scan(cfg)

    assert result.summary.total_findings >= 1
    assert result.trace
    assert result.trace[0].startswith("planner=")
    assert any(line.startswith("phase=plan") for line in result.trace)
    assert any("phase=execute module=auth" in line for line in result.trace)
    assert result.trace[-1] == "phase=diagnose"


def test_run_scan_executes_all_modules_once_in_trace():
    cfg = ScanConfig(spec_path="fixtures/openapi.json", base_url="http://localhost:8000")
    result = run_scan(cfg)
    module_lines = [line for line in result.trace if line.startswith("phase=execute module=")]

    module_names = [line.split("module=")[1] for line in module_lines]
    assert module_names == [
        "auth",
        "bola",
        "injection",
        "edgecase",
        "errorhandling",
        "contract",
        "responsequality",
    ]


def test_run_scan_with_llm_planner_falls_back_without_key():
    cfg = ScanConfig(spec_path="fixtures/openapi.json", base_url="http://localhost:8000", planner="llm")
    result = run_scan(cfg)

    assert result.summary.total_findings >= 1
    assert any("planner=llm" in line for line in result.trace)
    assert any("phase=execute module=auth" in line for line in result.trace)
