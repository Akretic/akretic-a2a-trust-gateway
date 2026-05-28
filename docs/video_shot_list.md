# Video Shot List

Use this to record the hosted 1-2 minute demo video. Do not commit or package
raw video files.

1. Home screen
   - Show product name, challenge prototype label, synthetic-data label, and
     judge walkthrough.
2. Start review
   - Keep persona as `procurement_user`.
   - Keep the VendorNova query.
   - Click `Start VendorNova Review`.
3. Proof row
   - Show Identity, Policy, RAG Filter, A2A, Approval, and Evidence Verify.
4. Gemini panel
   - Show `Mode: vertex`, `Model: gemini-2.5-flash`, project
     `akretic-a2a-trust-gateway`, and location `us-central1`.
5. Retrieval boundary
   - Show permitted source IDs.
   - Show denied source ID proof.
   - State that denied text is blocked before model context.
6. Approval gate
   - Show `approval_required`.
   - Show export/action remains paused until reviewer action.
7. A2A proof
   - Show Agent Card resolved.
   - Show skill call.
   - Show `correlation_id`.
8. Reviewer decision
   - Submit approve or reject as `security_reviewer`.
9. Evidence proof
   - Show valid hash chain and event count.
   - Optionally show the sample evidence report link.

## After Upload

Write the hosted video URL to:

```text
dist/video_url.txt
```
