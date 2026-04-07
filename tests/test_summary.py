from breakagent.models import ScanConfig
from breakagent.orchestrator import run_scan
from breakagent.summary import generate_summary_md


def test_generate_summary_md_deterministic_fallback_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = run_scan(ScanConfig(spec_path="fixtures/openapi.json", base_url="http://localhost:8000"))
    cfg = ScanConfig(
        spec_path="fixtures/openapi.json",
        base_url="http://localhost:8000",
        md_summary_enabled=True,
    )

    md, mode = generate_summary_md(result, cfg)
    assert mode == "deterministic_fallback"
    assert "# BreakAgent Summary" in md
    assert "Source of truth is the JSON findings report" in md
    assert "Top Findings" in md


def test_generate_summary_contains_finding_ids(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = run_scan(ScanConfig(spec_path="fixtures/openapi.json", base_url="http://localhost:8000"))
    md, _ = generate_summary_md(result, ScanConfig(spec_path="fixtures/openapi.json", base_url="http://localhost:8000"))

    first_id = result.findings[0].finding_id
    assert first_id in md
