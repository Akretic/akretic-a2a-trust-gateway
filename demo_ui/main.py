from __future__ import annotations

import html
import json
import os

import httpx
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from agents.root_orchestrator.main import run_vendor_review_workflow
from common.a2a_client import cloud_run_auth_headers

app = FastAPI(title="Akretic Demo UI")

BASE_CSS = """
:root {
  color-scheme: light;
  --bg: #f6f7f9;
  --surface: #ffffff;
  --ink: #111827;
  --muted: #5b6575;
  --line: #d9dee7;
  --accent: #0f766e;
  --accent-dark: #115e59;
  --warn: #b45309;
  --deny: #b91c1c;
  --ok: #166534;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--accent-dark); }
.shell { max-width: 1180px; margin: 0 auto; padding: 28px 24px 44px; }
.topbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 16px 0 24px;
  border-bottom: 1px solid var(--line);
}
.brand { font-size: 23px; font-weight: 760; letter-spacing: 0; }
.status-pill {
  border: 1px solid #a7d7cb;
  background: #e8f6f2;
  color: #0f513f;
  border-radius: 999px;
  padding: 7px 11px;
  font-size: 13px;
  font-weight: 650;
  white-space: nowrap;
}
.hero, .panel, .metric {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
}
.hero { margin-top: 24px; padding: 26px; }
.hero h1, .page-title h1 { margin: 0 0 10px; font-size: 34px; line-height: 1.08; letter-spacing: 0; }
.hero p, .page-title p { margin: 0; color: var(--muted); line-height: 1.55; max-width: 760px; }
.form-grid { display: grid; grid-template-columns: 220px 1fr; gap: 16px; margin-top: 24px; align-items: end; }
label { display: block; margin-bottom: 7px; color: #263244; font-size: 13px; font-weight: 700; }
select, textarea, input {
  width: 100%;
  border: 1px solid #c8d0dc;
  border-radius: 6px;
  padding: 10px 11px;
  background: #fff;
  color: var(--ink);
  font: inherit;
}
textarea { min-height: 112px; resize: vertical; }
button {
  border: 0;
  border-radius: 6px;
  background: var(--accent);
  color: #fff;
  padding: 10px 14px;
  font-weight: 750;
  cursor: pointer;
}
button:hover { background: var(--accent-dark); }
.page-title { margin: 24px 0 18px; }
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }
.metric { padding: 14px; min-height: 86px; }
.metric span { display: block; color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }
.metric strong { display: block; margin-top: 8px; font-size: 18px; overflow-wrap: anywhere; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.panel { padding: 18px; margin-bottom: 16px; }
.panel h2 { margin: 0 0 12px; font-size: 19px; letter-spacing: 0; }
.panel p { line-height: 1.55; }
.source-list { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 0; list-style: none; }
.source-list li {
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  border-radius: 999px;
  padding: 7px 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}
.decision { color: var(--warn); font-weight: 780; }
.valid { color: var(--ok); font-weight: 780; }
pre {
  max-height: 360px;
  overflow: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #0f172a;
  color: #e5eefb;
  border-radius: 8px;
  padding: 14px;
  font-size: 12px;
  line-height: 1.45;
}
.approval-form {
  display: grid;
  grid-template-columns: 190px 140px 1fr auto;
  gap: 10px;
  align-items: end;
}
.footer-nav { margin-top: 22px; }
@media (max-width: 820px) {
  .shell { padding: 20px 14px 32px; }
  .topbar, .form-grid, .grid, .metrics, .approval-form { grid-template-columns: 1fr; display: grid; }
  .hero h1, .page-title h1 { font-size: 27px; }
}
"""


def _approval_url() -> str:
    return os.getenv("APPROVAL_EVIDENCE_URL", "http://127.0.0.1:8104")


def _json_pre(value: object) -> str:
    return html.escape(json.dumps(value, indent=2, sort_keys=True))


def _page(title: str, content: str, *, status: str = "P0 Cloud Run demo") -> str:
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{html.escape(title)}</title>
        <style>{BASE_CSS}</style>
      </head>
      <body>
        <main class="shell">
          <header class="topbar">
            <div class="brand">Akretic A2A Trust Gateway</div>
            <div class="status-pill">{html.escape(status)}</div>
          </header>
          {content}
        </main>
      </body>
    </html>
    """


def _source_list(source_ids: list[str]) -> str:
    if not source_ids:
        return "<p>No sources returned.</p>"
    items = "".join(f"<li>{html.escape(source_id)}</li>" for source_id in source_ids)
    return f'<ul class="source-list">{items}</ul>'


async def run_review_from_ui(persona: str, query: str) -> dict:
    root_url = os.getenv("ROOT_ORCHESTRATOR_URL")
    if not root_url:
        return await run_vendor_review_workflow({"persona": persona, "query": query}, x_akretic_persona=persona)

    headers = cloud_run_auth_headers(root_url, {"x-akretic-persona": persona})
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            f"{root_url.rstrip('/')}/run_vendor_review",
            json={"persona": persona, "query": query},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def decide_approval_from_ui(
    *,
    run_id: str,
    approval_id: str,
    reviewer_persona: str,
    status: str,
    reason: str,
) -> tuple[object, object]:
    approval_url = _approval_url().rstrip("/")
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{approval_url}/decide_approval",
            json={"approval_id": approval_id, "status": status, "reason": reason},
            headers=cloud_run_auth_headers(approval_url, {"x-akretic-persona": reviewer_persona}),
        )
        if response.status_code >= 400:
            decision: object = {"status_code": response.status_code, "error": response.text}
        else:
            decision = response.json()
        verification_response = await client.get(
            f"{approval_url}/verify/{run_id}",
            headers=cloud_run_auth_headers(approval_url, {"x-akretic-persona": "security_reviewer"}),
        )
        verification = verification_response.json()
    return decision, verification


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "demo-ui"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _page(
        "Akretic A2A Trust Gateway",
        """
        <section class="hero">
        <h1>Akretic A2A Trust Gateway</h1>
        <p>Challenge prototype: policy-mediated A2A vendor-risk review.</p>
        <form method="post" action="/run">
          <div class="form-grid">
            <div>
              <label>Persona</label>
              <select name="persona">
                <option value="procurement_user">procurement_user</option>
                <option value="security_reviewer">security_reviewer</option>
                <option value="legal_reviewer">legal_reviewer</option>
                <option value="admin">admin</option>
              </select>
            </div>
            <div>
              <label>Query</label>
              <textarea name="query">VendorNova procurement security policy</textarea>
            </div>
          </div>
          <p><button type="submit">Start VendorNova Review</button></p>
        </form>
        </section>
        """,
    )


@app.post("/run", response_class=HTMLResponse)
async def run(persona: str = Form(...), query: str = Form(...)) -> str:
    result = await run_review_from_ui(persona, query)
    approval = result.get("approval_request")
    approval_html = ""
    if approval:
        approval_html = f"""
        <section class="panel">
        <h2>Approval Request</h2>
        <pre>{_json_pre(approval)}</pre>
        <form class="approval-form" method="post" action="/approval/decide">
          <input type="hidden" name="run_id" value="{html.escape(result['run_id'])}">
          <input type="hidden" name="approval_id" value="{html.escape(approval['approval_id'])}">
          <div>
            <label>Reviewer persona</label>
            <select name="reviewer_persona">
              <option value="security_reviewer">security_reviewer</option>
              <option value="procurement_user">procurement_user</option>
            </select>
          </div>
          <div>
            <label>Decision</label>
            <select name="status">
              <option value="approved">approved</option>
              <option value="rejected">rejected</option>
            </select>
          </div>
          <div>
            <label>Reason</label>
            <input name="reason" value="demo reviewer decision">
          </div>
          <button type="submit">Record reviewer decision</button>
        </form>
        </section>
        """
    permitted_source_ids = [chunk["source_id"] for chunk in result["retrieval"]["chunks"]]
    denied_source_ids = [source["source_id"] for source in result["retrieval"]["denied_sources"]]
    verification = result["verification"]
    return _page(
        "VendorNova Review",
        f"""
        <section class="page-title">
          <h1>VendorNova Review</h1>
          <p>{html.escape(result['summary'])}</p>
        </section>
        <section class="metrics">
          <div class="metric"><span>Run ID</span><strong>{html.escape(result['run_id'])}</strong></div>
          <div class="metric"><span>Persona</span><strong>{html.escape(persona)}</strong></div>
          <div class="metric"><span>External action</span><strong class="decision">{html.escape(result['export_decision']['outcome'])}</strong></div>
          <div class="metric"><span>Evidence chain</span><strong class="valid">{html.escape(str(verification.get('valid')).lower())}</strong></div>
        </section>
        <section class="grid">
          <div class="panel">
            <h2>Permitted Sources</h2>
            {_source_list(permitted_source_ids)}
          </div>
          <div class="panel">
            <h2>Denied Sources</h2>
            {_source_list(denied_source_ids)}
          </div>
        </section>
        <section class="grid">
          <div class="panel">
            <h2>Policy Decision</h2>
            <p><strong>{html.escape(result['export_decision']['outcome'])}</strong>: {html.escape(result['export_decision']['reason'])}</p>
          </div>
          <div class="panel">
            <h2>Export Result</h2>
            <pre>{_json_pre(result['export_result'])}</pre>
          </div>
        </section>
        {approval_html}
        <section class="panel">
        <h2>Evidence Verification</h2>
        <pre>{_json_pre(result['verification'])}</pre>
        </section>
        <p class="footer-nav"><a href="/">Back</a></p>
        """,
    )


@app.post("/approval/decide", response_class=HTMLResponse)
async def decide_approval(
    run_id: str = Form(...),
    approval_id: str = Form(...),
    reviewer_persona: str = Form(...),
    status: str = Form(...),
    reason: str = Form(...),
) -> str:
    decision, verification = await decide_approval_from_ui(
        run_id=run_id,
        approval_id=approval_id,
        reviewer_persona=reviewer_persona,
        status=status,
        reason=reason,
    )

    return _page(
        "Approval Decision",
        f"""
        <section class="page-title">
          <h1>Approval Decision</h1>
          <p>Run ID: {html.escape(run_id)}. Reviewer persona: {html.escape(reviewer_persona)}.</p>
        </section>
        <section class="panel">
        <h2>Decision Result</h2>
        <pre>{_json_pre(decision)}</pre>
        </section>
        <section class="panel">
        <h2>Evidence Verification</h2>
        <pre>{_json_pre(verification)}</pre>
        </section>
        <p class="footer-nav"><a href="/">Back</a></p>
        """,
    )
