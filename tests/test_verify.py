from breakagent.models import (
    BudgetConfig,
    Confidence,
    Finding,
    ScanResult,
    ScanSummary,
    Severity,
)
from breakagent.verify import apply_previous_report


def _result_with_ids(ids: list[str]) -> ScanResult:
    findings = [
        Finding(
            finding_id=fid,
            title="x",
            module="m",
            category="security",
            severity=Severity.MEDIUM,
            confidence=Confidence.HIGH,
            description="d",
            reproduction="r",
            fix="f",
        )
        for fid in ids
    ]
    return ScanResult(
        base_url="http://localhost:8000/",
        findings=findings,
        summary=ScanSummary(total_findings=len(findings), by_severity={"medium": len(findings)}, exit_code=2),
        budgets=BudgetConfig(),
        trace=[],
    )


def test_apply_previous_report_duplicate_ids_are_not_duplicated_in_fixed_output():
    previous = _result_with_ids(["DUP-1", "DUP-1", "ONLY-PREV"])
    current = _result_with_ids(["DUP-1"])

    merged = apply_previous_report(current, previous)
    fixed_ids = [f.finding_id for f in merged.findings if f.status.value == "fixed"]

    assert fixed_ids.count("ONLY-PREV") == 1
    assert fixed_ids.count("DUP-1") == 0
