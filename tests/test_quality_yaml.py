from breakagent.modules.quality import ResponseQualityModule
from breakagent.parser import parse_openapi


def test_response_quality_handles_yaml_numeric_200_key(tmp_path):
    spec = tmp_path / "openapi.yaml"
    spec.write_text(
        """
openapi: 3.0.0
info:
  title: YAML API
  version: "1.0"
paths:
  /yaml:
    get:
      responses:
        200: {}
""".strip(),
        encoding="utf-8",
    )

    endpoints = parse_openapi(str(spec))
    findings = ResponseQualityModule().run(endpoints)
    assert findings, "Expected response-quality finding for missing 200 description in YAML spec"
