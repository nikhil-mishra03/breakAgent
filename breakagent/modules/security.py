from __future__ import annotations

import re
from typing import TYPE_CHECKING

from breakagent.models import Confidence, Endpoint, Finding, Severity
from breakagent.modules.base import BaseModule

if TYPE_CHECKING:
    from breakagent.models import ScanConfig

_PATH_PARAM_RE = re.compile(r"\{[^}]+\}")


class AuthModule(BaseModule):
    name = "auth"

    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for ep in endpoints:
            if ep.path.startswith("/admin") and not ep.requires_auth:
                findings.append(
                    self._make_finding(
                        ep,
                        finding_id=f"AUTH-{ep.method}-{ep.path}",
                        title="Potential missing authentication on admin endpoint",
                        category="security",
                        severity=Severity.HIGH,
                        confidence=Confidence.MEDIUM,
                        description="Admin-like endpoint appears unauthenticated in spec.",
                        reproduction=f"curl -i -X {ep.method.upper()} {{base_url}}{ep.path}",
                        fix="Require authentication/authorization middleware on this route.",
                        owasp="API2:2023",
                    )
                )
        return findings


class BolaModule(BaseModule):
    name = "bola"

    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for ep in endpoints:
            param_match = _PATH_PARAM_RE.search(ep.path)
            if param_match and not ep.requires_auth:
                probe_path = _PATH_PARAM_RE.sub("1", ep.path)
                findings.append(
                    self._make_finding(
                        ep,
                        finding_id=f"BOLA-{ep.method}-{ep.path}",
                        title=f"Potential BOLA risk on {param_match.group()} endpoint",
                        category="security",
                        severity=Severity.HIGH,
                        confidence=Confidence.MEDIUM,
                        description="Object-level endpoint appears reachable without authentication.",
                        reproduction=f"curl -i -X {ep.method.upper()} {{base_url}}{probe_path}",
                        fix="Enforce object-level authorization checks using caller identity.",
                        owasp="API1:2023",
                    )
                )
        return findings


class InjectionModule(BaseModule):
    name = "injection"

    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for ep in endpoints:
            _INJECTION_PARAMS = {"query", "search", "filter", "username", "password", "email", "q"}
            if any(p.lower() in _INJECTION_PARAMS for p in ep.parameters):
                findings.append(
                    self._make_finding(
                        ep,
                        finding_id=f"INJ-{ep.method}-{ep.path}",
                        title="Input parameter likely needs injection hardening",
                        category="security",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.LOW,
                        description="Query-like parameters should be validated and escaped defensively.",
                        reproduction=(
                            f"curl -i -G {{base_url}}{ep.path} --data-urlencode "
                            "\"query=' OR 1=1 --\""
                        ),
                        fix="Apply strict input validation and parameterized data access.",
                        owasp="API8:2023",
                    )
                )
        return findings
