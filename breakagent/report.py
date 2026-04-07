from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Template

from breakagent.models import ScanResult

_HTML_TEMPLATE = Template(
    """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>BreakAgent Report</title></head>
  <body>
    <h1>BreakAgent Report</h1>
    <p>Target: {{ result.base_url }}</p>
    <p>Total findings: {{ result.summary.total_findings }}</p>
    <table border="1" cellspacing="0" cellpadding="6">
      <thead><tr><th>ID</th><th>Severity</th><th>Module</th><th>Title</th></tr></thead>
      <tbody>
      {% for f in result.findings %}
      <tr>
        <td>{{ f.finding_id }}</td>
        <td>{{ f.severity }}</td>
        <td>{{ f.module }}</td>
        <td>{{ f.title }}</td>
      </tr>
      {% endfor %}
      </tbody>
    </table>
  </body>
</html>
"""
)


def _safe_output_path(output_path: str) -> Path:
    p = Path(output_path)
    if ".." in p.parts:
        raise ValueError(f"Output path must not contain '..': {output_path}")
    return p


def write_json(result: ScanResult, output_path: str) -> None:
    _safe_output_path(output_path).write_text(result.model_dump_json(indent=2), encoding="utf-8")


def write_html(result: ScanResult, output_path: str) -> None:
    html = _HTML_TEMPLATE.render(result=result.model_dump())
    _safe_output_path(output_path).write_text(html, encoding="utf-8")


def read_json(path: str) -> ScanResult:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ScanResult.model_validate(payload)
