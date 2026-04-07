from __future__ import annotations

from typing import TYPE_CHECKING

from breakagent.models import Confidence, Endpoint, Finding, Severity
from breakagent.modules.base import BaseModule

if TYPE_CHECKING:
    from breakagent.models import ScanConfig


class EdgeCaseModule(BaseModule):
    name = "edgecase"

    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for ep in endpoints:
            if ep.method in {"post", "put", "patch"} and not ep.responses:
                findings.append(
                    self._make_finding(
                        ep,
                        finding_id=f"EDGE-{ep.method}-{ep.path}",
                        title="Write endpoint has no declared response behavior",
                        category="robustness",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.MEDIUM,
                        description="Missing response metadata often correlates with weak edge-case handling.",
                        reproduction=f"curl -i -X {ep.method.upper()} {{base_url}}{ep.path} -d '{{}}'",
                        fix="Document and implement explicit responses for malformed and boundary payloads.",
                    )
                )
        return findings


class ErrorHandlingModule(BaseModule):
    name = "errorhandling"

    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for ep in endpoints:
            has_4xx_or_5xx = any(str(code).startswith(("4", "5")) for code in ep.responses.keys())
            if not has_4xx_or_5xx:
                findings.append(
                    self._make_finding(
                        ep,
                        finding_id=f"ERR-{ep.method}-{ep.path}",
                        title="No explicit 4xx/5xx error responses documented",
                        category="robustness",
                        severity=Severity.LOW,
                        confidence=Confidence.MEDIUM,
                        description="Error contract is undefined, making failures harder to debug and handle.",
                        reproduction=f"curl -i -X {ep.method.upper()} {{base_url}}{ep.path}",
                        fix="Define consistent 4xx/5xx response schemas and status mappings.",
                    )
                )
        return findings
