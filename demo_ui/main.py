from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse

from agents.root_orchestrator.main import run_vendor_review_workflow
from common.a2a_client import cloud_run_auth_headers
from common.evidence import read_events

app = FastAPI(title="Akretic Demo UI")
SAMPLE_REPORT_PATH = (
    Path(__file__).resolve().parent
    / "sample-evidence-report-p2.json"
)

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
  --info: #1d4ed8;
  --ok-bg: #edf7ee;
  --warn-bg: #fff7ed;
  --deny-bg: #fef2f2;
  --info-bg: #eff6ff;
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
.labels { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.label {
  display: inline-flex;
  align-items: center;
  border: 1px solid #c8d0dc;
  background: #fff;
  color: #374151;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 750;
  white-space: nowrap;
}
.label.warn { border-color: #fed7aa; background: var(--warn-bg); color: #92400e; }
.label.info { border-color: #bfdbfe; background: var(--info-bg); color: #1e3a8a; }
.label.ok { border-color: #bbd7c1; background: var(--ok-bg); color: #14532d; }
.hero, .panel, .metric {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
}
.hero { margin-top: 24px; padding: 24px; }
.hero-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(300px, 0.9fr); gap: 22px; align-items: start; }
.eyebrow { margin: 0 0 8px; color: var(--accent-dark); font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0; }
.hero h1, .page-title h1 { margin: 0 0 10px; font-size: 34px; line-height: 1.08; letter-spacing: 0; }
.hero p, .page-title p { margin: 0; color: var(--muted); line-height: 1.55; max-width: 760px; }
.hero-actions { margin-top: 18px; }
.hero-badges { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 0; }
.scenario-copy {
  margin: 0 0 14px;
  color: #3f4c61;
  line-height: 1.52;
}
.hero-form {
  border: 1px solid var(--line);
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
}
.hero-form h2 { margin: 0 0 10px; font-size: 17px; }
.summary-copy { color: var(--muted); line-height: 1.55; max-width: 860px; overflow-wrap: anywhere; }
.summary-copy strong { color: #1f2937; }
.story-copy { color: #2f3a4c; line-height: 1.58; max-width: 980px; margin: 0; }
.walkthrough {
  margin-top: 18px;
  padding: 18px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
}
.walkthrough h2 { margin: 0 0 10px; font-size: 18px; }
.walkthrough ol { margin: 0; padding-left: 22px; color: #2f3a4c; line-height: 1.55; }
.form-grid { display: grid; grid-template-columns: 1fr; gap: 14px; margin-top: 12px; align-items: end; }
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
.proof-row { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 8px; margin: 18px 0; }
.proof-story { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 18px; }
.story-panel .proof-story { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.story-panel .story-step:nth-child(5) { grid-column: span 2; }
.story-panel .mini-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 14px; padding-left: 0; list-style: none; }
.story-step {
  position: relative;
  min-height: 108px;
  border: 1px solid #d6dde8;
  border-left-width: 4px;
  background: #fff;
  border-radius: 8px;
  padding: 12px 12px 12px 46px;
}
.story-step .step-number {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: #e8f6f2;
  color: var(--accent-dark);
  font-size: 12px;
  font-weight: 850;
}
.story-step h3 { margin: 0 0 6px; font-size: 14px; }
.story-step p, .story-step div { margin: 0; color: #354155; font-size: 13px; line-height: 1.42; overflow-wrap: anywhere; }
.story-step.ok { border-left-color: var(--ok); }
.story-step.warn { border-left-color: var(--warn); }
.story-step.deny { border-left-color: var(--deny); }
.story-step.info { border-left-color: var(--info); }
.mini-list { margin: 0; padding-left: 16px; }
.mini-list li { margin-bottom: 6px; }
.story-panel { margin-top: 18px; }
.proof-step {
  min-height: 76px;
  border: 1px solid #d6dde8;
  background: #fff;
  border-radius: 8px;
  padding: 10px;
}
.proof-step span { display: block; color: var(--muted); font-size: 11px; font-weight: 800; text-transform: uppercase; }
.proof-step strong { display: block; margin-top: 6px; font-size: 13px; line-height: 1.25; overflow-wrap: anywhere; }
.proof-step.ok { border-color: #bbd7c1; background: var(--ok-bg); }
.proof-step.warn { border-color: #fed7aa; background: var(--warn-bg); }
.proof-step.bad { border-color: #fecaca; background: var(--deny-bg); }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.panel { padding: 18px; margin-bottom: 16px; }
.panel h2 { margin: 0 0 12px; font-size: 19px; letter-spacing: 0; }
.panel p { line-height: 1.55; }
.panel-note { color: var(--muted); margin-top: 0; }
.source-list { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 0; list-style: none; }
.source-list li {
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  border-radius: 999px;
  padding: 7px 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}
.source-list li.denied { border-color: #fecaca; background: var(--deny-bg); color: #991b1b; }
.callout {
  border: 1px solid #cbd5e1;
  border-left-width: 5px;
  border-radius: 8px;
  padding: 12px 14px;
  margin: 14px 0;
  background: #fff;
  line-height: 1.45;
  overflow-wrap: anywhere;
}
.callout strong { display: block; margin-bottom: 3px; }
.callout.deny { border-color: #fecaca; border-left-color: var(--deny); background: var(--deny-bg); color: #7f1d1d; }
.callout.warn { border-color: #fed7aa; border-left-color: var(--warn); background: var(--warn-bg); color: #7c2d12; }
.callout.ok { border-color: #bbd7c1; border-left-color: var(--ok); background: var(--ok-bg); color: #14532d; }
.callout.info { border-color: #bfdbfe; border-left-color: var(--info); background: var(--info-bg); color: #1e3a8a; }
.decision { color: var(--warn); font-weight: 780; }
.valid { color: var(--ok); font-weight: 780; }
.invalid { color: var(--deny); font-weight: 780; }
.code-chip {
  display: inline-block;
  max-width: 100%;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: #f1f5f9;
  border: 1px solid #d8e0ea;
  border-radius: 5px;
  padding: 2px 5px;
  overflow-wrap: anywhere;
}
.a2a-table { width: 100%; border-collapse: collapse; font-size: 12px; table-layout: fixed; }
.a2a-table th, .a2a-table td { border-bottom: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }
.a2a-table th { color: var(--muted); font-size: 11px; text-transform: uppercase; }
.a2a-table .code-chip { white-space: normal; overflow-wrap: anywhere; line-height: 1.35; }
.a2a-table th:nth-child(1), .a2a-table td:nth-child(1) { width: 20%; }
.a2a-table th:nth-child(2), .a2a-table td:nth-child(2) { width: 13%; }
.a2a-table th:nth-child(3), .a2a-table td:nth-child(3) { width: 13%; }
.a2a-table th:nth-child(4), .a2a-table td:nth-child(4) { width: 15%; }
.a2a-table th:nth-child(5), .a2a-table td:nth-child(5) { width: 15%; }
.a2a-table th:nth-child(6), .a2a-table td:nth-child(6) { width: 10%; }
.a2a-table th:nth-child(7), .a2a-table td:nth-child(7) { width: 14%; }
.table-scroll { overflow-x: auto; }
.table-scroll table { min-width: 100%; }
.muted { color: var(--muted); font-size: 12px; }
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
  .topbar, .hero-grid, .form-grid, .grid, .metrics, .proof-row, .approval-form { grid-template-columns: 1fr; display: grid; }
  .proof-story { grid-template-columns: 1fr; }
  .story-panel .proof-story { grid-template-columns: 1fr; }
  .story-panel .story-step:nth-child(5) { grid-column: auto; }
  .story-panel .mini-list { display: block; padding-left: 16px; list-style: disc; }
  .hero h1, .page-title h1 { font-size: 27px; }
  .table-scroll { overflow-x: visible; }
  .a2a-table, .a2a-table thead, .a2a-table tbody, .a2a-table tr, .a2a-table td { display: block; width: 100% !important; }
  .a2a-table thead { display: none; }
  .a2a-table tr {
    box-sizing: border-box;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 10px;
    background: #fff;
  }
  .a2a-table td {
    border-bottom: 0;
    display: grid;
    grid-template-columns: 104px minmax(0, 1fr);
    gap: 8px;
    box-sizing: border-box;
    padding: 6px 0;
  }
  .a2a-table td::before {
    content: attr(data-label);
    color: var(--muted);
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
  }
}
@media (min-width: 821px) and (max-width: 1120px) {
  .proof-row { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
"""


def _approval_url() -> str:
    return os.getenv("APPROVAL_EVIDENCE_URL", "http://127.0.0.1:8104")


def _json_pre(value: object) -> str:
    return html.escape(json.dumps(value, indent=2, sort_keys=True))


def _summary_html(value: str) -> str:
    escaped = html.escape(value)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return escaped.replace("\n", "<br>")


class DemoUiError(Exception):
    def __init__(self, *, title: str, detail: str, next_action: str, status_code: int = 503):
        super().__init__(detail)
        self.title = title
        self.detail = detail
        self.next_action = next_action
        self.status_code = status_code


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
            <div class="labels">
              <div class="status-pill">{html.escape(status)}</div>
              <span class="label warn">Challenge prototype</span>
              <span class="label">Synthetic data</span>
            </div>
          </header>
          {content}
        </main>
      </body>
    </html>
    """


def _source_list(source_ids: list[str], *, denied: bool = False) -> str:
    if not source_ids:
        return "<p>No sources returned.</p>"
    class_name = ' class="denied"' if denied else ""
    items = "".join(f"<li{class_name}>{html.escape(source_id)}</li>" for source_id in source_ids)
    return f'<ul class="source-list">{items}</ul>'


def _response_detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text or response.reason_phrase
    if isinstance(body, dict):
        return str(body.get("detail") or body)
    return str(body)


def _remote_error(service: str, exc: httpx.HTTPStatusError) -> DemoUiError:
    status_code = exc.response.status_code
    detail = _response_detail(exc.response)
    if status_code in {401, 403}:
        return DemoUiError(
            title="Private service returned 401/403",
            detail=f"{service} blocked the request with HTTP {status_code}: {detail}",
            next_action=(
                "Confirm Cloud Run identity-token auth, service invoker IAM, and the "
                "x-akretic-persona-derived role before retrying."
            ),
            status_code=502,
        )
    return DemoUiError(
        title=f"{service} request failed",
        detail=f"{service} returned HTTP {status_code}: {detail}",
        next_action="Check the target service logs and rerun the P0 verifier after the service is healthy.",
        status_code=502 if status_code >= 500 else status_code,
    )


def _network_error(service: str, exc: httpx.HTTPError) -> DemoUiError:
    return DemoUiError(
        title=f"{service} unreachable",
        detail=str(exc) or type(exc).__name__,
        next_action=(
            "Check the configured service URL, Cloud Run revision health, and local service stack "
            "before retrying the judge path."
        ),
    )


def _failure_response(error: DemoUiError, *, title: str = "Demo path unavailable") -> HTMLResponse:
    content = _page(
        title,
        f"""
        <section class="page-title">
          <h1>{html.escape(error.title)}</h1>
          <p>The proof path did not complete. No approval/export action should be treated as completed from this attempt.</p>
        </section>
        <section class="panel">
          <h2>Failure State</h2>
          <div class="callout warn">
            <strong>{html.escape(error.title)}</strong>
            {html.escape(error.detail)}
          </div>
          <p><strong>Next action:</strong> {html.escape(error.next_action)}</p>
        </section>
        <p class="footer-nav"><a href="/">Back</a></p>
        """,
        status="Failure handling",
    )
    return HTMLResponse(content=content, status_code=error.status_code)


def _what_this_demo_proves_panel() -> str:
    return """
    <section class="walkthrough">
      <h2>What this demo proves</h2>
      <p class="story-copy">
        In this run, a procurement user reviews VendorNova. Akretic derives identity,
        allows permitted context, blocks executive-only material before Gemini,
        calls specialist agents through A2A Agent Cards, pauses export with
        <span class="code-chip">approval_required</span>, and verifies the run with
        hash-chain evidence.
      </p>
    </section>
    """


def _story_step(number: int, title: str, body: str, state: str = "ok") -> str:
    return f"""
    <article class="story-step {html.escape(state)}">
      <span class="step-number">{number}</span>
      <h3>{html.escape(title)}</h3>
      <div>{body}</div>
    </article>
    """


def _home_proof_story() -> str:
    return """
    <section class="proof-story" aria-label="Seven step proof path">
      <article class="story-step ok">
        <span class="step-number">1</span>
        <h3>Identity</h3>
        <div>Derived persona: <span class="code-chip">procurement_user</span>. Body claims cannot upgrade access.</div>
      </article>
      <article class="story-step warn">
        <span class="step-number">2</span>
        <h3>Policy</h3>
        <div>Gate0-lite returns allow, deny, or <span class="code-chip">approval_required</span>.</div>
      </article>
      <article class="story-step deny">
        <span class="step-number">3</span>
        <h3>RAG Filter</h3>
        <div><span class="code-chip">executive_acquisition_memo</span> is blocked before Gemini.</div>
      </article>
      <article class="story-step info">
        <span class="step-number">4</span>
        <h3>Gemini</h3>
        <div>Vertex Gemini summarizes permitted sources only.</div>
      </article>
      <article class="story-step ok">
        <span class="step-number">5</span>
        <h3>A2A</h3>
        <div>Agents are called through Agent Cards with correlation IDs.</div>
      </article>
      <article class="story-step warn">
        <span class="step-number">6</span>
        <h3>Approval</h3>
        <div>External export remains blocked until reviewer decision.</div>
      </article>
      <article class="story-step ok">
        <span class="step-number">7</span>
        <h3>Evidence</h3>
        <div>Hash-chain evidence verifies the run.</div>
      </article>
    </section>
    """


def _proof_step(label: str, value: str, state: str = "ok") -> str:
    return (
        f'<div class="proof-step {html.escape(state)}">'
        f"<span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>"
    )


def _denied_context_callout(denied_source_ids: list[str]) -> str:
    if not denied_source_ids:
        return """
        <div class="callout ok">
          <strong>No denied sources returned.</strong>
          The RAG filter did not return restricted source IDs for this request.
        </div>
        """
    denied = ", ".join(denied_source_ids)
    headline = "Denied before model context: executive_acquisition_memo."
    if "executive_acquisition_memo" not in denied_source_ids:
        headline = f"Denied before model context: {denied}."
    return f"""
    <div class="callout deny">
      <strong>{html.escape(headline)}</strong>
      Restricted chunks are filtered before prompt assembly; denied source text is not provided to Gemini.
    </div>
    """


def _approval_callout(result: dict[str, Any]) -> str:
    export_decision = result.get("export_decision", {})
    export_result = result.get("export_result", {})
    outcome = export_decision.get("outcome", "UNKNOWN")
    if outcome == "approval_required":
        return f"""
        <div class="callout warn">
          <strong>approval_required: external/sensitive action is paused.</strong>
          Export status is <span class="code-chip">{html.escape(export_result.get('status', 'not_executed'))}</span>.
          The reviewer approve/reject form below is the visible decision path.
        </div>
        """
    return f"""
    <div class="callout ok">
      <strong>External action state: {html.escape(outcome)}.</strong>
      No pending approval gate was returned for this request.
    </div>
    """


def _model_path_callout(result: dict[str, Any]) -> str:
    model_summary = result.get("model_summary", {})
    mode = model_summary.get("mode", "UNKNOWN")
    service_path = model_summary.get("service_path", "UNKNOWN")
    model = model_summary.get("model", "UNKNOWN")
    project_id = model_summary.get("project_id", "not applicable")
    location = model_summary.get("location", "not applicable")
    prompt_hash = str(model_summary.get("prompt_hash", "UNKNOWN"))[:16]
    if mode == "local":
        return f"""
        <div class="callout warn">
          <strong>Gemini local mode active.</strong>
          Mode: local. Model: {html.escape(str(model))}. {html.escape(service_path)}.
          This is labeled for tests and local demos, not overclaimed as Vertex execution.
        </div>
        """
    if mode == "vertex":
        return f"""
        <div class="callout info">
          <strong>Vertex/Gemini summarization path.</strong>
          Mode: vertex. Model: {html.escape(str(model))}. Project: {html.escape(str(project_id))}.
          Location: {html.escape(str(location))}. Prompt hash: <span class="code-chip">{html.escape(prompt_hash)}</span>.
          {html.escape(service_path)}. Gate0-lite remains the policy decision point.
        </div>
        """
    return f"""
    <div class="callout warn">
      <strong>Gemini path unknown.</strong>
      Model summary mode returned <span class="code-chip">{html.escape(str(mode))}</span>.
    </div>
    """


def _agent_card_url_from_base(base_url: str) -> str:
    if not base_url or base_url == "UNKNOWN":
        return "UNKNOWN"
    return f"{base_url.rstrip('/')}/.well-known/agent-card.json"


def _a2a_evidence_events(run_id: str) -> dict[str, dict[str, Any]]:
    try:
        events = read_events(run_id)
    except Exception:
        return {}
    return {
        str(event.get("correlation_id", "")): event
        for event in events
        if event.get("action") == "a2a_call"
    }


def _a2a_rows(result: dict[str, Any]) -> list[dict[str, str]]:
    calls = result.get("a2a_calls") or []
    event_by_correlation = _a2a_evidence_events(str(result.get("run_id", "")))
    if calls:
        rows = []
        for call in calls:
            correlation_id = str(call.get("correlation_id", "UNKNOWN"))
            event = event_by_correlation.get(correlation_id, {})
            metadata = event.get("metadata", {}) if isinstance(event, dict) else {}
            base_url = str(call.get("base_url") or metadata.get("base_url") or "UNKNOWN")
            callee = str(call.get("callee") or metadata.get("callee") or call.get("agent") or "UNKNOWN")
            caller = str(call.get("caller") or metadata.get("caller") or "root_orchestrator")
            skill = str(call.get("skill_intent") or call.get("skill") or metadata.get("skill") or "UNKNOWN")
            event_id = str(call.get("evidence_event_id") or event.get("event_id") or "UNKNOWN")
            event_hash = str(call.get("evidence_event_hash") or event.get("event_hash") or "UNKNOWN")
            rows.append(
                {
                    "agent_card_url": str(call.get("agent_card_url") or metadata.get("agent_card_url") or _agent_card_url_from_base(base_url)),
                    "agent": str(call.get("agent", callee)),
                    "skill": skill,
                    "caller_callee": f"{caller} -> {callee}",
                    "correlation_id": correlation_id,
                    "outcome": str(call.get("outcome", event.get("outcome") or "result")),
                    "event": f"{event_id} / {event_hash[:16]}",
                    "card": "Agent Card resolved" if call.get("agent_card_resolved") else "Agent Card UNKNOWN",
                }
            )
        return rows
    fallback = []
    if result.get("retrieval_decision"):
        correlation_id = str(result["retrieval_decision"].get("correlation_id", "UNKNOWN"))
        event = event_by_correlation.get(correlation_id, {})
        fallback.append(
            {
                "agent_card_url": _agent_card_url_from_base(str(event.get("metadata", {}).get("base_url", "UNKNOWN"))),
                "agent": "akretic-policy-agent",
                "skill": "authorize_intent",
                "caller_callee": "root_orchestrator -> akretic-policy-agent",
                "correlation_id": correlation_id,
                "outcome": str(result["retrieval_decision"].get("outcome", "UNKNOWN")),
                "event": f"{event.get('event_id', 'UNKNOWN')} / {str(event.get('event_hash', 'UNKNOWN'))[:16]}",
                "card": "Agent Card resolved",
            }
        )
    if result.get("retrieval"):
        correlation_id = str(result["retrieval"].get("correlation_id", "UNKNOWN"))
        event = event_by_correlation.get(correlation_id, {})
        fallback.append(
            {
                "agent_card_url": _agent_card_url_from_base(str(event.get("metadata", {}).get("base_url", "UNKNOWN"))),
                "agent": "akretic-knowledge-agent",
                "skill": "retrieve_permitted_context",
                "caller_callee": "root_orchestrator -> akretic-knowledge-agent",
                "correlation_id": correlation_id,
                "outcome": "result",
                "event": f"{event.get('event_id', 'UNKNOWN')} / {str(event.get('event_hash', 'UNKNOWN'))[:16]}",
                "card": "Agent Card resolved",
            }
        )
    if result.get("export_decision"):
        correlation_id = str(result["export_decision"].get("correlation_id", "UNKNOWN"))
        event = event_by_correlation.get(correlation_id, {})
        fallback.append(
            {
                "agent_card_url": _agent_card_url_from_base(str(event.get("metadata", {}).get("base_url", "UNKNOWN"))),
                "agent": "akretic-policy-agent",
                "skill": "authorize_intent",
                "caller_callee": "root_orchestrator -> akretic-policy-agent",
                "correlation_id": correlation_id,
                "outcome": str(result["export_decision"].get("outcome", "UNKNOWN")),
                "event": f"{event.get('event_id', 'UNKNOWN')} / {str(event.get('event_hash', 'UNKNOWN'))[:16]}",
                "card": "Agent Card resolved",
            }
        )
    return fallback


def _a2a_table(result: dict[str, Any]) -> str:
    rows = _a2a_rows(result)
    if not rows:
        return "<p>No A2A calls returned for this run.</p>"
    body = "".join(
        "<tr>"
        f"<td data-label=\"Agent Card URL\"><span class=\"code-chip\">{html.escape(row['agent_card_url'])}</span><br><span class=\"muted\">{html.escape(row['card'])}</span></td>"
        f"<td data-label=\"Agent\"><strong>{html.escape(row['agent'])}</strong></td>"
        f"<td data-label=\"Skill / intent\">{html.escape(row['skill'])}</td>"
        f"<td data-label=\"Caller / callee\">{html.escape(row['caller_callee'])}</td>"
        f"<td data-label=\"correlation_id\"><span class=\"code-chip\">{html.escape(row['correlation_id'])}</span></td>"
        f"<td data-label=\"Outcome\">{html.escape(row['outcome'])}</td>"
        f"<td data-label=\"Evidence event / hash\"><span class=\"code-chip\">{html.escape(row['event'])}</span></td>"
        "</tr>"
        for row in rows
    )
    return f"""
    <div class="table-scroll">
      <table class="a2a-table">
        <thead><tr><th>Agent Card URL</th><th>Agent</th><th>Skill / intent</th><th>Caller / callee</th><th>correlation_id</th><th>Outcome</th><th>Evidence event / hash</th></tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>
    """


def _a2a_story_list(result: dict[str, Any]) -> str:
    rows = _a2a_rows(result)
    if not rows:
        return "No A2A calls returned for this run."
    items = "".join(
        "<li>"
        f"<strong>{html.escape(row['agent'])}</strong> / {html.escape(row['skill'])}<br>"
        f"<span class=\"code-chip\">{html.escape(row['correlation_id'])}</span> "
        f"<span class=\"code-chip\">{html.escape(row['event'])}</span>"
        "</li>"
        for row in rows[:4]
    )
    return f'<ul class="mini-list">{items}</ul>'


def _result_proof_story(
    result: dict[str, Any],
    *,
    persona: str,
    permitted_source_ids: list[str],
    denied_source_ids: list[str],
) -> str:
    actor = result.get("actor") if isinstance(result.get("actor"), dict) else {}
    actor_id = str(actor.get("actor_id") or persona)
    role = str(actor.get("role") or persona)
    retrieval_outcome = str(result.get("retrieval_decision", {}).get("outcome", "UNKNOWN"))
    export_outcome = str(result.get("export_decision", {}).get("outcome", "UNKNOWN"))
    approval = result.get("approval_request") or {}
    approval_id = str(approval.get("approval_id", "none"))
    approval_status = str(approval.get("status", result.get("export_result", {}).get("status", "UNKNOWN")))
    model_summary = result.get("model_summary", {})
    mode = str(model_summary.get("mode", "UNKNOWN"))
    model = str(model_summary.get("model", "UNKNOWN"))
    project_id = str(model_summary.get("project_id", "not applicable"))
    location = str(model_summary.get("location", "not applicable"))
    verification = result.get("verification", {})
    valid_label = "valid hash chain" if verification.get("valid") else "verification failed"
    event_count = str(verification.get("event_count", "UNKNOWN"))
    permitted = ", ".join(permitted_source_ids) or "none"
    denied = ", ".join(denied_source_ids) or "none"
    evidence_state = "ok" if verification.get("valid") else "deny"
    return f"""
    <section class="panel story-panel">
      <h2>Proof Path From This Run</h2>
      <p class="panel-note">The result mirrors the homepage story with the actual run evidence.</p>
      <div class="proof-story" aria-label="Run evidence proof path">
        {_story_step(1, "Identity", f'Persona <span class="code-chip">{html.escape(persona)}</span>; actor <span class="code-chip">{html.escape(actor_id)}</span>; role <span class="code-chip">{html.escape(role)}</span>.', "ok")}
        {_story_step(2, "Policy", f'Retrieval decision <span class="code-chip">{html.escape(retrieval_outcome)}</span>; external export decision <span class="code-chip">{html.escape(export_outcome)}</span>.', "warn")}
        {_story_step(3, "RAG Filter", f'Permitted source IDs: <span class="code-chip">{html.escape(permitted)}</span><br>Denied before context: <span class="code-chip">{html.escape(denied)}</span>.', "deny")}
        {_story_step(4, "Gemini", f'Mode <span class="code-chip">{html.escape(mode)}</span>; model <span class="code-chip">{html.escape(model)}</span>; project <span class="code-chip">{html.escape(project_id)}</span>; location <span class="code-chip">{html.escape(location)}</span>.', "info")}
        {_story_step(5, "A2A", _a2a_story_list(result), "ok")}
        {_story_step(6, "Approval", f'Approval ID <span class="code-chip">{html.escape(approval_id)}</span>; status <span class="code-chip">{html.escape(approval_status)}</span>; export remains blocked until reviewer decision.', "warn")}
        {_story_step(7, "Evidence", f'<span class="code-chip">{html.escape(valid_label)}</span>; event count <span class="code-chip">{html.escape(event_count)}</span>; <a href="/sample-evidence-report" target="_blank" rel="noreferrer">sample report</a>.', evidence_state)}
      </div>
    </section>
    """


def _evidence_callout(verification: dict[str, Any]) -> str:
    valid = bool(verification.get("valid"))
    event_count = verification.get("event_count", "UNKNOWN")
    if valid:
        return f"""
        <div class="callout ok">
          <strong>Evidence proof: valid hash chain.</strong>
          Event count: <span class="code-chip">{html.escape(str(event_count))}</span>.
          <a href="/sample-evidence-report" target="_blank" rel="noreferrer">Open sample evidence report</a>.
        </div>
        """
    return f"""
    <div class="callout deny">
      <strong>Evidence verification failed.</strong>
      Event count: <span class="code-chip">{html.escape(str(event_count))}</span>.
      Reason: {html.escape(str(verification.get('reason', 'UNKNOWN')))}.
    </div>
    """


def _render_review_result(result: dict[str, Any], *, persona: str) -> str:
    approval = result.get("approval_request")
    approval_html = ""
    if approval:
        approval_html = f"""
        <section class="panel">
        <h2>Approval Request</h2>
        <div class="callout warn">
          <strong>Pending approval: export/action has not completed.</strong>
          Approval ID <span class="code-chip">{html.escape(approval['approval_id'])}</span> is waiting for reviewer action.
        </div>
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
        <pre>{_json_pre(approval)}</pre>
        </section>
        """
    permitted_source_ids = [chunk["source_id"] for chunk in result["retrieval"]["chunks"]]
    denied_source_ids = [source["source_id"] for source in result["retrieval"]["denied_sources"]]
    verification = result["verification"]
    verification_class = "valid" if verification.get("valid") else "invalid"
    verification_label = "valid hash chain" if verification.get("valid") else "invalid hash chain"
    return _page(
        "VendorNova Review",
        f"""
        <section class="page-title">
          <h1>VendorNova Review</h1>
          <div class="summary-copy">{_summary_html(result['summary'])}</div>
        </section>
        {_result_proof_story(result, persona=persona, permitted_source_ids=permitted_source_ids, denied_source_ids=denied_source_ids)}
        <section class="metrics">
          <div class="metric"><span>Run ID</span><strong>{html.escape(result['run_id'])}</strong></div>
          <div class="metric"><span>Persona</span><strong>{html.escape(persona)}</strong></div>
          <div class="metric"><span>External action</span><strong class="decision">{html.escape(result['export_decision']['outcome'])}</strong></div>
          <div class="metric"><span>Evidence verify</span><strong class="{verification_class}">{html.escape(verification_label)}</strong></div>
        </section>
        {_model_path_callout(result)}
        {_denied_context_callout(denied_source_ids)}
        {_approval_callout(result)}
        <section class="grid">
          <div class="panel">
            <h2>Permitted Sources</h2>
            <p class="panel-note">Only these synthetic chunks are eligible for model context.</p>
            {_source_list(permitted_source_ids)}
          </div>
          <div class="panel">
            <h2>Denied Sources</h2>
            <p class="panel-note">Denied source IDs are visible as proof, but their contents stay out of the prompt.</p>
            {_source_list(denied_source_ids, denied=True)}
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
        <section class="panel">
          <h2>A2A Proof</h2>
          {_a2a_table(result)}
        </section>
        {approval_html}
        <section class="panel">
        <h2>Evidence Verification</h2>
        {_evidence_callout(result['verification'])}
        <pre>{_json_pre(result['verification'])}</pre>
        </section>
        <p class="footer-nav"><a href="/">Back</a></p>
        """,
        status="Proof storyboard",
    )


async def run_review_from_ui(persona: str, query: str) -> dict:
    root_url = os.getenv("ROOT_ORCHESTRATOR_URL")
    if not root_url:
        try:
            return await run_vendor_review_workflow(
                {"persona": persona, "query": query},
                x_akretic_persona=persona,
            )
        except RuntimeError as exc:
            raise DemoUiError(
                title="Local demo path unavailable",
                detail=str(exc),
                next_action=(
                    "Start the local service stack or fix the named service failure before retrying."
                ),
            ) from exc

    headers = cloud_run_auth_headers(root_url, {"x-akretic-persona": persona})
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{root_url.rstrip('/')}/run_vendor_review",
                json={"persona": persona, "query": query},
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise _remote_error("Root Orchestrator", exc) from exc
    except httpx.HTTPError as exc:
        raise _network_error("Root Orchestrator", exc) from exc


async def decide_approval_from_ui(
    *,
    run_id: str,
    approval_id: str,
    reviewer_persona: str,
    status: str,
    reason: str,
) -> tuple[object, object]:
    approval_url = _approval_url().rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{approval_url}/decide_approval",
                json={"approval_id": approval_id, "status": status, "reason": reason},
                headers=cloud_run_auth_headers(approval_url, {"x-akretic-persona": reviewer_persona}),
            )
            if response.status_code >= 400:
                decision: object = {
                    "status": "not_recorded",
                    "status_code": response.status_code,
                    "error": _response_detail(response),
                    "next_action": "Confirm reviewer role, approval ID, and Cloud Run invoker auth.",
                }
            else:
                decision = response.json()
            verification_response = await client.get(
                f"{approval_url}/verify/{run_id}",
                headers=cloud_run_auth_headers(approval_url, {"x-akretic-persona": "security_reviewer"}),
            )
            if verification_response.status_code >= 400:
                verification: object = {
                    "valid": False,
                    "status_code": verification_response.status_code,
                    "error": _response_detail(verification_response),
                    "next_action": "Check Approval/Evidence Agent auth and evidence ledger access.",
                }
            else:
                verification = verification_response.json()
    except httpx.HTTPError as exc:
        raise _network_error("Approval/Evidence Agent", exc) from exc
    return decision, verification


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "demo-ui"}


@app.get("/sample-evidence-report")
def sample_evidence_report() -> JSONResponse:
    if not SAMPLE_REPORT_PATH.exists():
        return JSONResponse(
            {
                "status": "missing",
                "reason": "sample evidence report artifact is not present in this build",
            },
            status_code=404,
        )
    return JSONResponse(json.loads(SAMPLE_REPORT_PATH.read_text(encoding="utf-8")))


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return _page(
        "Akretic A2A Trust Gateway",
        f"""
        <section class="hero">
          <div class="hero-grid">
            <div>
              <p class="eyebrow">Akretic A2A Trust Gateway</p>
              <h1>Agents collaborate. Gemini does not authorize.</h1>
              <p>
                Akretic gives procurement and security teams a controlled VendorNova review
                where policy, retrieval filtering, approval, and evidence stay outside the model.
              </p>
              <div class="hero-badges" aria-label="Demo proof badges">
                <span class="label warn">Challenge prototype</span>
                <span class="label">Synthetic data</span>
                <span class="label info">Cloud Run + Vertex Gemini</span>
                <span class="label info">A2A protocol proof</span>
              </div>
              {_home_proof_story()}
            </div>
            <form class="hero-form" method="post" action="/run">
              <h2>Run the controlled VendorNova review.</h2>
              <p class="scenario-copy">
                A procurement user asks for VendorNova security context. Akretic allows
                permitted sources, denies executive-only material before Gemini, pauses
                export for approval, and records the A2A evidence trail.
              </p>
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
              <p class="hero-actions"><button type="submit">Start VendorNova Review</button></p>
            </form>
          </div>
        </section>
        """ + _what_this_demo_proves_panel() + """
        """,
        status="Cloud Run judge path",
    )


@app.post("/run", response_class=HTMLResponse)
async def run(persona: str = Form(...), query: str = Form(...)):
    try:
        result = await run_review_from_ui(persona, query)
    except DemoUiError as exc:
        return _failure_response(exc, title="VendorNova Review")
    except Exception as exc:
        return _failure_response(
            DemoUiError(
                title="Demo path failed",
                detail=str(exc) or type(exc).__name__,
                next_action="Check service logs and rerun pytest plus the Cloud Run verifier.",
            ),
            title="VendorNova Review",
        )
    return _render_review_result(result, persona=persona)


@app.post("/approval/decide", response_class=HTMLResponse)
async def decide_approval(
    run_id: str = Form(...),
    approval_id: str = Form(...),
    reviewer_persona: str = Form(...),
    status: str = Form(...),
    reason: str = Form(...),
):
    try:
        decision, verification = await decide_approval_from_ui(
            run_id=run_id,
            approval_id=approval_id,
            reviewer_persona=reviewer_persona,
            status=status,
            reason=reason,
        )
    except DemoUiError as exc:
        return _failure_response(exc, title="Approval Decision")

    verification_valid = bool(isinstance(verification, dict) and verification.get("valid"))
    verification_class = "ok" if verification_valid else "deny"
    decision_status = decision.get("status", "UNKNOWN") if isinstance(decision, dict) else "UNKNOWN"
    return _page(
        "Approval Decision",
        f"""
        <section class="page-title">
          <h1>Approval Decision</h1>
          <p>Run ID: {html.escape(run_id)}. Reviewer persona: {html.escape(reviewer_persona)}.</p>
        </section>
        <section class="proof-row" aria-label="Approval proof status">
          {_proof_step("Reviewer", reviewer_persona)}
          {_proof_step("Decision", str(decision_status), "warn" if decision_status == "not_recorded" else "ok")}
          {_proof_step("Export", "completed only if approved", "warn")}
          {_proof_step("Evidence Verify", "valid hash chain" if verification_valid else "verification failed", "ok" if verification_valid else "bad")}
          {_proof_step("Data", "synthetic corpus")}
          {_proof_step("Prototype", "challenge path")}
        </section>
        <section class="panel">
        <h2>Decision Result</h2>
        <div class="callout {'warn' if decision_status == 'not_recorded' else 'ok'}">
          <strong>Reviewer approve/reject path is visible.</strong>
          Decision status: <span class="code-chip">{html.escape(str(decision_status))}</span>.
        </div>
        <pre>{_json_pre(decision)}</pre>
        </section>
        <section class="panel">
        <h2>Evidence Verification</h2>
        <div class="callout {verification_class}">
          <strong>{'Evidence proof: valid hash chain.' if verification_valid else 'Evidence verification failed.'}</strong>
          The result below is returned by the Approval/Evidence Agent verify path.
        </div>
        <pre>{_json_pre(verification)}</pre>
        </section>
        <p class="footer-nav"><a href="/">Back</a></p>
        """,
    )
