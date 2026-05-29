"""Local release evidence harness for AuditOps and final package checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = ROOT / ".auditops" / "validation" / "latest-ci-local.json"


def powershell_exe() -> str:
    return "powershell"


def tail(value: str, limit: int = 4000) -> str:
    value = value or ""
    return value[-limit:]


def run_check(name: str, command: list[str]) -> dict[str, object]:
    started = time.time()
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    duration = round(time.time() - started, 3)
    return {
        "name": name,
        "command": command,
        "status": "pass" if proc.returncode == 0 else "fail",
        "returncode": proc.returncode,
        "durationSeconds": duration,
        "stdoutTail": tail(proc.stdout),
        "stderrTail": tail(proc.stderr),
    }


def write_validation(checks: list[dict[str, object]]) -> None:
    VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    payload = {
        "schema": "akretic-ci-local-v1",
        "status": status,
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "artifacts": {
            "junit": ".audit/junit.xml",
            "securitySarif": ".audit/akretic-security.sarif",
            "submissionZip": "dist/akretic-a2a-trust-gateway-submission.zip",
        },
    }
    VALIDATION_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--skip-package", action="store_true")
    parser.add_argument("--skip-security", action="store_true")
    args = parser.parse_args()

    (ROOT / ".audit").mkdir(exist_ok=True)

    checks: list[dict[str, object]] = []
    if not args.skip_tests:
        checks.append(
            run_check(
                "pytest-junit",
                [sys.executable, "-m", "pytest", "-q", "--junitxml=.audit/junit.xml"],
            )
        )

    if not args.skip_package:
        checks.append(
            run_check(
                "submission-package",
                [
                    powershell_exe(),
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "scripts/build_submission_package.ps1",
                ],
            )
        )

    if not args.skip_security:
        checks.append(
            run_check(
                "public-surface-security-sarif",
                [sys.executable, "scripts/security_scan.py", "--sarif", ".audit/akretic-security.sarif"],
            )
        )

    write_validation(checks)
    failed = [check for check in checks if check["status"] != "pass"]
    if failed:
        for check in failed:
            print(f"{check['name']} failed with return code {check['returncode']}")
            stderr = str(check.get("stderrTail") or "").strip()
            stdout = str(check.get("stdoutTail") or "").strip()
            if stderr:
                print(stderr)
            elif stdout:
                print(stdout)
        return 1

    print(f"ci_local passed; validation written to {VALIDATION_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
