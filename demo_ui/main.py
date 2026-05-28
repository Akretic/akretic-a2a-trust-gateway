from __future__ import annotations

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from agents.root_orchestrator.main import run_vendor_review_workflow

app = FastAPI(title="Akretic Demo UI")


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
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; margin: 40px; max-width: 980px;">
        <h1>VendorNova Review</h1>
        <p><strong>Run ID:</strong> {result['run_id']}</p>
        <p><strong>Persona:</strong> {persona}</p>
        <p><strong>Summary:</strong> {result['summary']}</p>
        <h2>Permitted sources</h2>
        <pre>{[chunk['source_id'] for chunk in result['retrieval']['chunks']]}</pre>
        <h2>Denied sources</h2>
        <pre>{result['retrieval']['denied_sources']}</pre>
        <h2>External action decision</h2>
        <pre>{result['export_decision']['outcome']}: {result['export_decision']['reason']}</pre>
        <h2>Evidence verification</h2>
        <pre>{result['verification']}</pre>
        <p><a href="/">Back</a></p>
      </body>
    </html>
    """
