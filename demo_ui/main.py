from __future__ import annotations

import html
import json
import os

import httpx
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from agents.root_orchestrator.main import run_vendor_review_workflow

app = FastAPI(title="Akretic Demo UI")


def _approval_url() -> str:
    return os.getenv("APPROVAL_EVIDENCE_URL", "http://127.0.0.1:8104")


def _json_pre(value: object) -> str:
    return html.escape(json.dumps(value, indent=2, sort_keys=True))


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "demo-ui"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <html>
      <head><title>Akretic A2A Trust Gateway</title></head>
      <body style="font-family: Arial, sans-serif; margin: 40px; max-width: 980px;">
        <h1>Akretic A2A Trust Gateway</h1>
        <p>Challenge prototype: policy-mediated A2A vendor-risk review.</p>
        <form method="post" action="/run">
          <label>Persona:</label>
          <select name="persona">
            <option value="procurement_user">procurement_user</option>
            <option value="security_reviewer">security_reviewer</option>
            <option value="legal_reviewer">legal_reviewer</option>
            <option value="admin">admin</option>
          </select>
          <br><br>
          <label>Query:</label><br>
          <textarea name="query" rows="4" cols="90">VendorNova procurement security policy</textarea>
          <br><br>
          <button type="submit">Start VendorNova Review</button>
        </form>
      </body>
    </html>
    """


@app.post("/run", response_class=HTMLResponse)
async def run(persona: str = Form(...), query: str = Form(...)) -> str:
    result = await run_vendor_review_workflow({"persona": persona, "query": query}, x_akretic_persona=persona)
    approval = result.get("approval_request")
    approval_html = ""
    if approval:
        approval_html = f"""
        <h2>Approval request</h2>
        <pre>{_json_pre(approval)}</pre>
        <form method="post" action="/approval/decide">
          <input type="hidden" name="run_id" value="{html.escape(result['run_id'])}">
          <input type="hidden" name="approval_id" value="{html.escape(approval['approval_id'])}">
          <label>Reviewer persona:</label>
          <select name="reviewer_persona">
            <option value="security_reviewer">security_reviewer</option>
            <option value="procurement_user">procurement_user</option>
          </select>
          <label>Decision:</label>
          <select name="status">
            <option value="approved">approved</option>
            <option value="rejected">rejected</option>
          </select>
          <input name="reason" value="demo reviewer decision">
          <button type="submit">Record reviewer decision</button>
        </form>
        """
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; margin: 40px; max-width: 980px;">
        <h1>VendorNova Review</h1>
        <p><strong>Run ID:</strong> {html.escape(result['run_id'])}</p>
        <p><strong>Persona:</strong> {html.escape(persona)}</p>
        <p><strong>Summary:</strong> {html.escape(result['summary'])}</p>
        <h2>Permitted sources</h2>
        <pre>{_json_pre([chunk['source_id'] for chunk in result['retrieval']['chunks']])}</pre>
        <h2>Denied sources</h2>
        <pre>{_json_pre(result['retrieval']['denied_sources'])}</pre>
        <h2>External action decision</h2>
        <pre>{html.escape(result['export_decision']['outcome'])}: {html.escape(result['export_decision']['reason'])}</pre>
        <h2>Export result</h2>
        <pre>{_json_pre(result['export_result'])}</pre>
        {approval_html}
        <h2>Evidence verification</h2>
        <pre>{_json_pre(result['verification'])}</pre>
        <p><a href="/">Back</a></p>
      </body>
    </html>
    """


@app.post("/approval/decide", response_class=HTMLResponse)
async def decide_approval(
    run_id: str = Form(...),
    approval_id: str = Form(...),
    reviewer_persona: str = Form(...),
    status: str = Form(...),
    reason: str = Form(...),
) -> str:
    headers = {"x-akretic-persona": reviewer_persona}
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{_approval_url().rstrip('/')}/decide_approval",
            json={"approval_id": approval_id, "status": status, "reason": reason},
            headers=headers,
        )
        if response.status_code >= 400:
            decision: object = {"status_code": response.status_code, "error": response.text}
        else:
            decision = response.json()
        verification_response = await client.get(
            f"{_approval_url().rstrip('/')}/verify/{run_id}",
            headers={"x-akretic-persona": "security_reviewer"},
        )
        verification = verification_response.json()

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; margin: 40px; max-width: 980px;">
        <h1>Approval Decision</h1>
        <p><strong>Run ID:</strong> {html.escape(run_id)}</p>
        <p><strong>Reviewer persona:</strong> {html.escape(reviewer_persona)}</p>
        <h2>Decision result</h2>
        <pre>{_json_pre(decision)}</pre>
        <h2>Evidence verification</h2>
        <pre>{_json_pre(verification)}</pre>
        <p><a href="/">Back</a></p>
      </body>
    </html>
    """
