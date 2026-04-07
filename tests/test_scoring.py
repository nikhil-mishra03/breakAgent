from breakagent.models import Confidence, Finding, Severity
from breakagent.scoring import compute_counts, exit_code


def _finding(severity: Severity) -> Finding:
    return Finding(
        finding_id=f"id-{severity.value}",
        title="x",
        module="m",
        category="security",
        severity=severity,
        confidence=Confidence.HIGH,
        description="d",
        reproduction="r",
        fix="f",
    )


def test_exit_code_threshold_behavior():
    findings = [_finding(Severity.LOW)]
    assert exit_code(findings, Severity.MEDIUM) == 1

    findings = [_finding(Severity.HIGH)]
    assert exit_code(findings, Severity.MEDIUM) == 2


def test_counts_include_all_levels():
    counts = compute_counts([_finding(Severity.HIGH), _finding(Severity.INFO)])
    assert counts["high"] == 1
    assert counts["info"] == 1
    assert counts["critical"] == 0
