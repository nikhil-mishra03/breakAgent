from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from breakagent.models import Confidence, Endpoint, Finding, Severity

if TYPE_CHECKING:
    from breakagent.models import ScanConfig


class BaseModule(ABC):
    name: ClassVar[str]

    @abstractmethod
    def run(self, endpoints: list[Endpoint], config: ScanConfig | None = None) -> list[Finding]:
        raise NotImplementedError

    def _make_finding(
        self,
        ep: Endpoint,
        *,
        finding_id: str,
        title: str,
        category: str,
        severity: Severity,
        confidence: Confidence,
        description: str,
        reproduction: str,
        fix: str,
        owasp: str | None = None,
    ) -> Finding:
        return Finding(
            finding_id=finding_id,
            title=title,
            module=self.name,
            category=category,
            severity=severity,
            confidence=confidence,
            description=description,
            reproduction=reproduction,
            fix=fix,
            owasp=owasp,
            endpoint=f"{ep.method.upper()} {ep.path}",
        )
