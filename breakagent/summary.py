from __future__ import annotations

import json
import os
from collections import Counter

from breakagent.models import ScanConfig, ScanResult


def _deterministic_summary(result: ScanResult) -> str:
    by_module = Counter(f.module for f in result.findings)
    by_severity = Counter(f.severity.value for f in result.findings)
    top = result.findings[:8]

    lines = [
        "# BreakAgent Summary",
        "",
        "> Assistant-generated summary. Source of truth is the JSON findings report.",
        "",
        "## Snapshot",
        f"- Target: `{result.base_url}`",
        f"- Total findings: **{result.summary.total_findings}**",
        f"- Exit code: **{result.summary.exit_code}**",
        f"- Severity mix: {', '.join(f'{k}={v}' for k, v in by_severity.items()) or 'none'}",
        f"- Module mix: {', '.join(f'{k}={v}' for k, v in by_module.items()) or 'none'}",
        "",
        "## Top Findings (by report order)",
    ]
    if not top:
        lines.append("- No findings detected.")
    else:
        for finding in top:
            lines.append(
                f"- `{finding.finding_id}` [{finding.severity.value}] {finding.title} "
                f"({finding.endpoint or 'n/a'})"
            )

    lines.extend(
        [
            "",
            "## Recommended Next Actions",
            "1. Triage high severity findings first, then medium.",
            "2. Validate each finding using its reproduction command.",
            "3. Fix and rerun with `--previous-report` to verify closure.",
        ]
    )
    return "\n".join(lines) + "\n"


def _llm_summary(result: ScanResult, config: ScanConfig) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    compact = {
        "target": result.base_url,
        "summary": result.summary.model_dump(),
        "findings": [
            {
                "id": f.finding_id,
                "severity": f.severity.value,
                "module": f.module,
                "title": f.title,
                "endpoint": f.endpoint,
                "fix": f.fix,
            }
            for f in result.findings
        ],
    }
    prompt = (
        "Write a concise markdown executive summary for API scan findings. "
        "Every finding claim must reference finding IDs. "
        "Include sections: Snapshot, Priority Risks, 3 Immediate Actions. "
        "Do not invent facts beyond provided JSON."
    )

    response = client.responses.create(
        model=config.summary_model,
        input=[
            {"role": "system", "content": "You are a precise security report editor."},
            {"role": "user", "content": prompt + "\n\nDATA:\n" + json.dumps(compact)},
        ],
        max_output_tokens=config.summary_max_tokens,
    )
    text = (getattr(response, "output_text", "") or "").strip()
    return text or None


def generate_summary_md(result: ScanResult, config: ScanConfig) -> tuple[str, str]:
    """
    Returns (markdown, mode) where mode is one of: llm, deterministic_fallback.
    """
    try:
        md = _llm_summary(result, config)
        if md:
            header = (
                "# BreakAgent Summary\n\n"
                "> Assistant-generated summary. Source of truth is the JSON findings report.\n\n"
            )
            return header + md.strip() + "\n", "llm"
    except Exception:
        # Non-blocking: summary generation must never break scan output path.
        pass

    return _deterministic_summary(result), "deterministic_fallback"
