from __future__ import annotations

from collections import Counter

from breakagent.models import Finding, Severity

SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFO,
]


def compute_counts(findings: list[Finding]) -> dict[str, int]:
    counts = Counter(f.severity.value for f in findings)
    return {level.value: counts.get(level.value, 0) for level in SEVERITY_ORDER}


def exit_code(findings: list[Finding], fail_on: Severity) -> int:
    threshold_idx = SEVERITY_ORDER.index(fail_on)
    for finding in findings:
        if SEVERITY_ORDER.index(finding.severity) <= threshold_idx:
            return 2
    return 0 if not findings else 1
