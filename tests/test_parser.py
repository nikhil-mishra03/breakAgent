from pathlib import Path

from breakagent.parser import parse_openapi

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_openapi_reads_endpoints():
    endpoints = parse_openapi(str(FIXTURES / "openapi.json"))
    assert len(endpoints) == 4
    assert any(e.path == "/admin/users" and e.method == "get" for e in endpoints)
