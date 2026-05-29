# Public Repository Release Gate

Before the GitHub repository is made public, run the release scan against the
working tree, final zip, `.akretic/` package/check folders, and git history.

## Required Result

- 0 active S0/S1 findings.
- All S2 findings fixed or explicitly accepted in a public-safe note.
- Scanner false positives are documented, especially if a guardrail test
  intentionally lists banned phrases.
- No secrets, credentials, private keys, auth headers, cookies, customer data, or
  private third-party data are present in public surfaces.
- Denied executive memo text is absent from the UI output, model output, logs,
  sample evidence report, final zip public docs, and generated package docs.

## Command

```powershell
.\.venv\Scripts\python.exe scripts\security_scan.py `
  --sarif .audit\akretic-security.sarif `
  --json .audit\akretic-security.json `
  --include-generated `
  --scan-git-history
```

## Current False Positives

None accepted. Guardrail tests may contain banned phrase examples by design, but
the scanner only evaluates public/submission surfaces for overclaim language.
