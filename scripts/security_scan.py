"""Local public-surface security checks for the challenge package.

The scanner intentionally stays narrow: it verifies that public/submission
artifacts do not include denied executive memo text or unsupported public
claims, and it scans project text for high-signal secret patterns.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".audit",
    ".auditops",
    ".akretic",
    ".hypothesis",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
}
GENERATED_SCAN_DIRS = {".akretic", "dist"}

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mmd",
    ".ps1",
    ".py",
    ".txt",
    ".toml",
    ".ts",
    ".yaml",
    ".yml",
}

PUBLIC_PACKAGE_FILES = [
    "README.md",
    "docs/p5_acceptance.md",
    "docs/devpost_answers.md",
    "docs/demo_video_script.md",
    "docs/video_shot_list.md",
    "docs/public_brief.md",
    "docs/submission_checklist.md",
    "docs/submission_package.md",
    "docs/challenge_readiness_remediation.md",
    "docs/judge_readiness.md",
    "docs/adk_alignment.md",
    "docs/a2a_intent_map.md",
    "docs/third_party_rights.md",
    "docs/eligibility_statement.md",
    "docs/public_release_gate.md",
    "docs/architecture.md",
    "docs/architecture.mmd",
    "docs/deployment.md",
    "docs/deployment_notes.md",
    "dist/video_url.txt",
]

DENIED_TEXT_PATTERNS = [
    re.compile(r"confidential acquisition timing", re.IGNORECASE),
]

OVERCLAIM_PATTERNS = [
    re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
    re.compile(r"\bcertified\b", re.IGNORECASE),
    re.compile(r"\bmarketplace[- ]approved\b", re.IGNORECASE),
    re.compile(r"\bguaranteed compliance\b", re.IGNORECASE),
    re.compile(r"\bunhackable\b", re.IGNORECASE),
    re.compile(r"\buniversal data[- ]leak prevention\b", re.IGNORECASE),
    re.compile(r"\blegal non[- ]repudiation\b", re.IGNORECASE),
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bCLIENT_INPUT_REQUIRED\b", re.IGNORECASE),
    re.compile(r"\bTODO\b", re.IGNORECASE),
]

NEGATION_HINTS = (
    "do not",
    "does not",
    "not ",
    "no ",
    "avoid",
    "without",
    "doesn't",
    "is not",
    "are not",
)

SECRET_RULES = [
    (
        "akretic-secret-private-key",
        "Private key marker",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----"),
    ),
    (
        "akretic-secret-google-api-key",
        "Google API key",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ),
    (
        "akretic-secret-aws-access-key",
        "AWS access key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
    (
        "akretic-secret-github-token",
        "GitHub token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b"),
    ),
    (
        "akretic-secret-slack-token",
        "Slack token",
        re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{20,}\b"),
    ),
]


@dataclass
class Finding:
    rule_id: str
    message: str
    path: str
    line: int
    snippet: str
    level: str = "error"
    severity: str = "S1"
    accepted: bool = False


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def iter_project_text_files(*, include_generated: bool = False) -> Iterable[Path]:
    excluded_dirs = set(DEFAULT_EXCLUDED_DIRS)
    if include_generated:
        excluded_dirs -= GENERATED_SCAN_DIRS
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel_parts = path.relative_to(ROOT).parts
        if any(part in excluded_dirs for part in rel_parts):
            continue
        yield path


def iter_public_text_surfaces() -> Iterable[tuple[str, str]]:
    for rel in PUBLIC_PACKAGE_FILES:
        path = ROOT / rel
        if path.exists():
            yield rel, read_text(path)

    for report in sorted((ROOT / "artifacts").glob("sample-evidence-report-*.json")):
        yield report.relative_to(ROOT).as_posix(), read_text(report)

    zip_path = ROOT / "dist" / "akretic-a2a-trust-gateway-submission.zip"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            for entry in archive.infolist():
                suffix = Path(entry.filename).suffix.lower()
                if entry.is_dir() or suffix not in TEXT_SUFFIXES or entry.file_size > 750_000:
                    continue
                data = archive.read(entry)
                yield f"{zip_path.relative_to(ROOT).as_posix()}::{entry.filename}", data.decode(
                    "utf-8", errors="ignore"
                )


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def line_at(text: str, index: int) -> str:
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    if end == -1:
        end = len(text)
    return text[start:end].strip()


def redacted_line(text: str, index: int, pattern: re.Pattern[str]) -> str:
    return pattern.sub("<redacted>", line_at(text, index))


def negated_public_claim(line: str) -> bool:
    lowered = line.lower()
    return any(hint in lowered for hint in NEGATION_HINTS)


def scan_secrets(findings: list[Finding], *, include_generated: bool = False) -> None:
    for path in iter_project_text_files(include_generated=include_generated):
        rel = path.relative_to(ROOT).as_posix()
        text = read_text(path)
        for rule_id, title, pattern in SECRET_RULES:
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        rule_id=rule_id,
                        message=f"{title} pattern appears in project text.",
                        path=rel,
                        line=line_number(text, match.start()),
                        snippet=redacted_line(text, match.start(), pattern),
                    )
                )


def scan_public_surfaces(findings: list[Finding]) -> None:
    for path, text in iter_public_text_surfaces():
        for pattern in DENIED_TEXT_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        rule_id="akretic-denied-text-public-surface",
                        message="Denied executive memo text appears in a public/submission surface.",
                        path=path,
                        line=line_number(text, match.start()),
                        snippet=line_at(text, match.start()),
                    )
                )

        for pattern in OVERCLAIM_PATTERNS:
            for match in pattern.finditer(text):
                line = line_at(text, match.start())
                if negated_public_claim(line):
                    continue
                findings.append(
                    Finding(
                        rule_id="akretic-public-overclaim",
                        message="Unsupported production/compliance/security claim appears public-facing.",
                        path=path,
                        line=line_number(text, match.start()),
                        snippet=line,
                    )
                )
        for pattern in PLACEHOLDER_PATTERNS:
            for match in pattern.finditer(text):
                line = line_at(text, match.start())
                if "CLIENT_INPUT_REQUIRED" in line and "public_release_gate" in path:
                    continue
                findings.append(
                    Finding(
                        rule_id="akretic-public-placeholder",
                        message="Submission/public package surface contains a stale placeholder.",
                        path=path,
                        line=line_number(text, match.start()),
                        snippet=line,
                    )
                )


def scan_git_history_for_secrets(findings: list[Finding]) -> None:
    proc = subprocess.run(
        ["git", "log", "--all", "--patch", "--no-ext-diff", "--format=commit %H"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="ignore",
    )
    if proc.returncode != 0:
        findings.append(
            Finding(
                rule_id="akretic-git-history-scan-failed",
                message="Git history scan failed.",
                path="git-history",
                line=1,
                snippet=proc.stderr[-300:] or "git log failed",
                severity="S1",
            )
        )
        return
    text = proc.stdout
    for rule_id, title, pattern in SECRET_RULES:
        for match in pattern.finditer(text):
            findings.append(
                Finding(
                    rule_id=f"{rule_id}-history",
                    message=f"{title} pattern appears in git history.",
                    path="git-history",
                    line=line_number(text, match.start()),
                    snippet=redacted_line(text, match.start(), pattern),
                )
            )


def sarif_rules() -> list[dict[str, object]]:
    rules = [
        {
            "id": "akretic-denied-text-public-surface",
            "name": "Denied text public surface",
            "shortDescription": {
                "text": "Denied executive memo text must not appear in public/submission artifacts."
            },
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "akretic-public-overclaim",
            "name": "Bounded public claims",
            "shortDescription": {
                "text": "Public copy must not claim production readiness, certification, or guarantees."
            },
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "akretic-public-placeholder",
            "name": "No stale public placeholders",
            "shortDescription": {
                "text": "Submission/public package artifacts must not contain stale placeholders."
            },
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "akretic-git-history-scan-failed",
            "name": "Git history scan failed",
            "shortDescription": {
                "text": "Git history must be scanned before public repository release."
            },
            "defaultConfiguration": {"level": "error"},
        },
    ]
    for rule_id, title, _pattern in SECRET_RULES:
        rules.append(
            {
                "id": rule_id,
                "name": title,
                "shortDescription": {"text": f"{title} must not be committed to source."},
                "defaultConfiguration": {"level": "error"},
            }
        )
    return rules


def build_sarif(findings: list[Finding]) -> dict[str, object]:
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "akretic-local-security-scan",
                        "version": "1.0.0",
                        "informationUri": "https://akretic.com/a2a-trust-gateway-demo",
                        "rules": sarif_rules(),
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": not findings,
                        "endTimeUtc": datetime.now(timezone.utc).isoformat(),
                    }
                ],
                "results": [
                    {
                        "ruleId": finding.rule_id,
                        "level": finding.level,
                        "message": {"text": finding.message},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": finding.path},
                                    "region": {
                                        "startLine": max(1, finding.line),
                                        "snippet": {"text": finding.snippet[:300]},
                                    },
                                }
                            }
                        ],
                    }
                    for finding in findings
                ],
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sarif", default=".audit/akretic-security.sarif")
    parser.add_argument("--json", default="")
    parser.add_argument("--no-fail", action="store_true")
    parser.add_argument("--include-generated", action="store_true")
    parser.add_argument("--scan-git-history", action="store_true")
    args = parser.parse_args()

    findings: list[Finding] = []
    scan_secrets(findings, include_generated=args.include_generated)
    scan_public_surfaces(findings)
    if args.scan_git_history:
        scan_git_history_for_secrets(findings)

    s0_s1_count = len([finding for finding in findings if finding.severity in {"S0", "S1"}])
    s2_unaccepted_count = len(
        [finding for finding in findings if finding.severity == "S2" and not finding.accepted]
    )
    release_gate_passed = s0_s1_count == 0 and s2_unaccepted_count == 0

    sarif_path = ROOT / args.sarif
    sarif_path.parent.mkdir(parents=True, exist_ok=True)
    sarif_path.write_text(json.dumps(build_sarif(findings), indent=2), encoding="utf-8")

    if args.json:
        json_path = ROOT / args.json
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {
                    "status": "pass" if release_gate_passed else "fail",
                    "finding_count": len(findings),
                    "s0_s1_count": s0_s1_count,
                    "s2_unaccepted_count": s2_unaccepted_count,
                    "release_gate": "pass" if release_gate_passed else "fail",
                    "sarif": sarif_path.relative_to(ROOT).as_posix(),
                    "findings": [finding.__dict__ for finding in findings],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    if findings:
        for finding in findings:
            print(
                f"{finding.severity} {finding.rule_id}: "
                f"{finding.path}:{finding.line}: {finding.message}"
            )
        if release_gate_passed:
            print("Security scan release gate passed with accepted non-S0/S1 findings.")
            return 0
        return 0 if args.no_fail else 1

    print(f"Security scan passed; SARIF written to {sarif_path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
