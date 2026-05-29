# Video Shot List

Use this to record the hosted 1-2 minute demo video. Do not commit or package
raw video files.

1. Home screen
   - Show product name, challenge prototype label, synthetic-data label, and
     judge walkthrough.
   - Land the thesis: agents can collaborate, but the model cannot decide what
     it may read, share, approve, or export.
2. Start review
   - Keep persona as `procurement_user`.
   - Keep the VendorNova query.
   - Click `Start VendorNova Review`.
3. Proof row
   - Show Identity, Policy, RAG Filter, A2A, Approval, and Evidence Verify.
4. Gemini panel
   - Show `Mode: vertex`, `Model: gemini-2.5-flash`, project
     `akretic-a2a-trust-gateway`, and location `us-central1`.
5. ADK wrapper proof
   - Show the Google ADK Workflow wrapper delegates to the verified root
     orchestrator path.
6. Retrieval boundary
   - Show permitted source IDs.
   - Show denied source ID proof.
   - State that denied text is blocked before model context.
7. Approval gate
   - Show `approval_required`.
   - Show export/action remains paused until reviewer action.
8. A2A proof
   - Show Agent Card URL.
   - Show agent and skill/intent.
   - Show caller/callee.
   - Show `correlation_id`.
   - Show evidence event/hash.
9. Reviewer decision
   - Submit approve or reject as `security_reviewer`.
10. Evidence proof
   - Show valid hash chain and event count.
   - Optionally show the sample evidence report link.

## After Upload

Write the hosted video URL to:

```text
dist/video_url.txt
```
