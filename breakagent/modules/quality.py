from __future__ import annotations

from typing import TYPE_CHECKING

from breakagent.models import Confidence, Endpoint, Finding, Severity
from breakagent.modules.base import BaseModule

if TYPE_CHECKING:
    from breakagent.models import ScanConfig


class ContractModule(BaseModule):
    name = "contract"

    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for ep in endpoints:
            if not ep.responses:
                findings.append(
                    self._make_finding(
                        ep,
                        finding_id=f"CONTRACT-{ep.method}-{ep.path}",
                        title="Endpoint missing OpenAPI responses",
                        category="quality",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.HIGH,
                        description="Contract is incomplete; runtime behavior cannot be verified against spec.",
                        reproduction="Run contract tests against this endpoint; expected schema is undefined.",
                        fix="Add explicit response status codes and schemas in OpenAPI spec.",
                    )
                )
        return findings


class ResponseQualityModule(BaseModule):
    name = "responsequality"

    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for ep in endpoints:
            resp_200 = ep.responses.get("200", {})
            if "200" in ep.responses and "description" not in resp_200:
                findings.append(
                    self._make_finding(
                        ep,
                        finding_id=f"RESPQ-{ep.method}-{ep.path}",
                        title="Success response lacks description",
                        category="quality",
                        severity=Severity.INFO,
                        confidence=Confidence.MEDIUM,
                        description="Response documentation quality is weak; consumers may misinterpret fields.",
                        reproduction="Inspect OpenAPI response object for missing human-readable contract details.",
                        fix="Add response descriptions and error-code guidance for consumers.",
                    )
                )
        return findings
