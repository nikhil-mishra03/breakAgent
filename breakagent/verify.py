from __future__ import annotations

from breakagent.models import FindingStatus, ScanResult


def apply_previous_report(current: ScanResult, previous: ScanResult) -> ScanResult:
    prev_ids = {f.finding_id for f in previous.findings}
    current_ids = {f.finding_id for f in current.findings}

    prev_by_id = {f.finding_id: f for f in previous.findings}
    fixed_ids = prev_ids - current_ids
    for finding in current.findings:
        finding.status = FindingStatus.OPEN

    for fixed_id in sorted(fixed_ids):
        current.findings.append(
            prev_by_id[fixed_id].model_copy(update={"status": FindingStatus.FIXED})
        )

    return current
