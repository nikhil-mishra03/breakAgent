from breakagent.models import ScanConfig
from breakagent.orchestrator import run_scan
from breakagent.report import read_json, write_json


def test_report_json_roundtrip_preserves_scan_result(tmp_path):
    result = run_scan(ScanConfig(spec_path="fixtures/openapi.json", base_url="http://localhost:8000"))
    out = tmp_path / "report.json"

    write_json(result, str(out))
    loaded = read_json(str(out))

    assert loaded.model_dump() == result.model_dump()
