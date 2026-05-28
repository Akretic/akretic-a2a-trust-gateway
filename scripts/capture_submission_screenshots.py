"""Capture public submission screenshots from the Cloud Run demo."""

from __future__ import annotations

import json
import html
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright


DEMO_URL = "https://akretic-demo-ui-oes3slkexq-uc.a.run.app"
QUERY = "VendorNova procurement security policy"


def latest_evidence_report() -> Path:
    reports = sorted(
        Path("artifacts").glob("sample-evidence-report-*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not reports:
        raise RuntimeError("No sample evidence report found under artifacts/")
    return reports[0]


def render_evidence_preview(report_path: Path) -> Path:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    verification = report.get("verification", {})
    latest_model = summary.get("latest_model", {})
    rows = []
    for event in report.get("events", [])[:18]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(event.get('agent_id', '')))}</td>"
            f"<td>{html.escape(str(event.get('action', '')))}</td>"
            f"<td>{html.escape(str(event.get('resource_id', '')))}</td>"
            f"<td>{html.escape(str(event.get('outcome', '')))}</td>"
            f"<td>{html.escape(str(event.get('correlation_id', '')))}</td>"
            "</tr>"
        )
    denied_source_ids = ", ".join(latest_model.get("denied_source_ids") or [])
    permitted_source_ids = ", ".join(latest_model.get("permitted_source_ids") or [])
    html_text = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Evidence Report Preview</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 48px; color: #111827; background: #f8fafc; }}
    h1 {{ font-size: 32px; margin: 0 0 8px; }}
    h2 {{ font-size: 18px; margin-top: 28px; }}
    .subtle {{ color: #64748b; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 24px 0; }}
    .card {{ background: #fff; border: 1px solid #dbe4ef; border-radius: 8px; padding: 14px; }}
    .label {{ color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase; }}
    .value {{ display: block; margin-top: 6px; font-weight: 800; }}
    .ok {{ color: #047857; }}
    .warn {{ color: #b45309; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dbe4ef; }}
    th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #e5edf5; font-size: 12px; vertical-align: top; }}
    th {{ color: #64748b; font-size: 11px; text-transform: uppercase; }}
    code {{ background: #eef2ff; border: 1px solid #dbe4ef; border-radius: 6px; padding: 2px 5px; }}
  </style>
</head>
<body>
  <h1>Sample Evidence Report</h1>
  <p class="subtle">Public-safe preview generated from <code>{html.escape(report_path.name)}</code>.</p>
  <div class="grid">
    <div class="card"><span class="label">Run ID</span><span class="value">{html.escape(str(report.get('run_id', '')))}</span></div>
    <div class="card"><span class="label">Hash Chain</span><span class="value ok">{html.escape(str(verification.get('valid', False)).lower())}</span></div>
    <div class="card"><span class="label">Event Count</span><span class="value">{html.escape(str(verification.get('event_count', '')))}</span></div>
    <div class="card"><span class="label">Model Path</span><span class="value">{html.escape(str(latest_model.get('mode', '')))} / {html.escape(str(latest_model.get('model', '')))}</span></div>
  </div>
  <div class="grid">
    <div class="card"><span class="label">Permitted Source IDs</span><span class="value">{html.escape(permitted_source_ids)}</span></div>
    <div class="card"><span class="label">Denied Source IDs</span><span class="value warn">{html.escape(denied_source_ids)}</span></div>
    <div class="card"><span class="label">Approval</span><span class="value">approval_required, reviewer decision recorded</span></div>
    <div class="card"><span class="label">Boundary</span><span class="value">Denied text is not rendered in this preview.</span></div>
  </div>
  <h2>Evidence Events</h2>
  <table>
    <thead><tr><th>Agent</th><th>Action</th><th>Resource</th><th>Outcome</th><th>Correlation ID</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>
"""
    preview_path = Path(".akretic/evidence-report-preview.html")
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text(html_text, encoding="utf-8")
    return preview_path


def copy_bytes(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())


def main() -> None:
    artifacts_dir = Path("artifacts/screenshots")
    output_dir = Path("output/playwright")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})

        page.goto(DEMO_URL, wait_until="networkidle", timeout=60_000)
        home_path = artifacts_dir / "demo-home.png"
        page.screenshot(path=str(home_path), full_page=True)

        page.select_option("select[name='persona']", "procurement_user")
        page.fill("textarea[name='query']", QUERY)
        with page.expect_navigation(wait_until="networkidle", timeout=180_000):
            page.get_by_role("button", name="Start VendorNova Review").click()
        review_path = artifacts_dir / "demo-review-result.png"
        page.screenshot(path=str(review_path), full_page=True)

        evidence_preview = render_evidence_preview(latest_evidence_report())
        page.goto(evidence_preview.resolve().as_uri(), wait_until="networkidle", timeout=60_000)
        evidence_path = artifacts_dir / "evidence-report.png"
        page.screenshot(path=str(evidence_path), full_page=True)

        browser.close()

    copy_bytes(home_path, output_dir / "demo-home.png")
    copy_bytes(review_path, output_dir / "demo-review-result.png")

    metadata = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "demo_url": DEMO_URL,
        "screenshots": {
            "home": str(home_path),
            "review_result": str(review_path),
            "evidence_report": str(evidence_path),
        },
    }
    (output_dir / "screenshot-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
