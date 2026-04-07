import json

from click.testing import CliRunner

from breakagent.cli import cli


def test_cli_scan_writes_reports(tmp_path):
    runner = CliRunner()
    json_out = tmp_path / "report.json"
    html_out = tmp_path / "report.html"

    result = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            "fixtures/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--json-out",
            str(json_out),
            "--html-out",
            str(html_out),
        ],
    )

    assert result.exit_code in {1, 2}
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert "findings" in payload
    assert html_out.exists()


def test_cli_verify_marks_fixed(tmp_path):
    runner = CliRunner()
    prev_json = tmp_path / "prev.json"
    prev_html = tmp_path / "prev.html"

    first = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            "fixtures/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--json-out",
            str(prev_json),
            "--html-out",
            str(prev_html),
        ],
    )
    assert first.exit_code in {1, 2}

    spec_path = tmp_path / "clean_openapi.json"
    spec_path.write_text(
        '{"openapi":"3.0.0","info":{"title":"x","version":"1"},"paths":{"/ok":{"get":{"security":[{"b":[]}],"responses":{"200":{"description":"ok"},"400":{"description":"bad"}}}}}}',
        encoding="utf-8",
    )

    out_json = tmp_path / "out.json"
    out_html = tmp_path / "out.html"
    second = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            str(spec_path),
            "--base-url",
            "http://localhost:8000",
            "--previous-report",
            str(prev_json),
            "--json-out",
            str(out_json),
            "--html-out",
            str(out_html),
        ],
    )
    assert second.exit_code in {0, 1, 2}

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert any(item["status"] == "fixed" for item in payload["findings"])


def test_cli_verify_summary_consistency_after_fixed_merge(tmp_path):
    runner = CliRunner()
    prev_json = tmp_path / "prev.json"
    prev_html = tmp_path / "prev.html"

    first = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            "fixtures/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--json-out",
            str(prev_json),
            "--html-out",
            str(prev_html),
        ],
    )
    assert first.exit_code in {1, 2}

    cleaner_spec = tmp_path / "clean_openapi.json"
    cleaner_spec.write_text(
        '{"openapi":"3.0.0","info":{"title":"x","version":"1"},'
        '"paths":{"/ok":{"get":{"security":[{"bearerAuth":[]}],'
        '"responses":{"200":{"description":"ok"},"400":{"description":"bad"}}}}}}',
        encoding="utf-8",
    )

    out_json = tmp_path / "out.json"
    out_html = tmp_path / "out.html"
    second = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            str(cleaner_spec),
            "--base-url",
            "http://localhost:8000",
            "--previous-report",
            str(prev_json),
            "--json-out",
            str(out_json),
            "--html-out",
            str(out_html),
        ],
    )
    assert second.exit_code in {0, 1, 2}

    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["summary"]["total_findings"] == len(payload["findings"])
    counts = payload["summary"]["by_severity"]
    recomputed = {key: 0 for key in counts}
    for finding in payload["findings"]:
        recomputed[finding["severity"]] += 1
    assert counts == recomputed


def test_cli_malformed_spec_fails_with_clean_message(tmp_path):
    runner = CliRunner()
    bad_spec = tmp_path / "bad.json"
    bad_spec.write_text('{"openapi": "3.0.0", "paths": ', encoding="utf-8")

    result = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            str(bad_spec),
            "--base-url",
            "http://localhost:8000",
        ],
    )

    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "OpenAPI" in result.output or "spec" in result.output


def test_cli_fail_on_thresholds_are_deterministic(tmp_path):
    runner = CliRunner()
    spec = "fixtures/openapi.json"
    base_args = [
        "scan",
        "--spec",
        spec,
        "--base-url",
        "http://localhost:8000",
        "--json-out",
        str(tmp_path / "report.json"),
        "--html-out",
        str(tmp_path / "report.html"),
    ]

    critical = runner.invoke(cli, base_args + ["--fail-on", "critical"])
    high = runner.invoke(cli, base_args + ["--fail-on", "high"])
    medium = runner.invoke(cli, base_args + ["--fail-on", "medium"])
    info = runner.invoke(cli, base_args + ["--fail-on", "info"])

    assert critical.exit_code == 1
    assert high.exit_code == 2
    assert medium.exit_code == 2
    assert info.exit_code == 2


def test_cli_md_summary_generates_markdown_without_affecting_exit(tmp_path):
    runner = CliRunner()
    json_out = tmp_path / "report.json"
    html_out = tmp_path / "report.html"
    md_out = tmp_path / "summary.md"

    base_result = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            "fixtures/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--json-out",
            str(json_out),
            "--html-out",
            str(html_out),
            "--fail-on",
            "high",
        ],
    )

    with_summary = runner.invoke(
        cli,
        [
            "scan",
            "--spec",
            "fixtures/openapi.json",
            "--base-url",
            "http://localhost:8000",
            "--json-out",
            str(json_out),
            "--html-out",
            str(html_out),
            "--md-summary",
            "--summary-out",
            str(md_out),
            "--fail-on",
            "high",
        ],
    )

    assert with_summary.exit_code == base_result.exit_code
    assert md_out.exists()
    assert "BreakAgent Summary" in md_out.read_text(encoding="utf-8")
