"""Local public-surface security checks for the challenge package.

The scanner intentionally stays narrow: it verifies that public/submission
artifacts do not include denied executive memo text or unsupported public
claims, and it scans project text for high-signal secret patterns.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def iter_project_text_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel_parts = path.relative_to(ROOT).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts):
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


def negated_public_claim(line: str) -> bool:
    lowered = line.lower()
    return any(hint in lowered for hint in NEGATION_HINTS)


def scan_secrets(findings: list[Finding]) -> None:
    for path in iter_project_text_files():
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
                        snippet=line_at(text, match.start()),
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
    args = parser.parse_args()

    findings: list[Finding] = []
    scan_secrets(findings)
    scan_public_surfaces(findings)

    sarif_path = ROOT / args.sarif
    sarif_path.parent.mkdir(parents=True, exist_ok=True)
    sarif_path.write_text(json.dumps(build_sarif(findings), indent=2), encoding="utf-8")

    if args.json:
        json_path = ROOT / args.json
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                {
                    "status": "fail" if findings else "pass",
                    "finding_count": len(findings),
                    "sarif": sarif_path.relative_to(ROOT).as_posix(),
                    "findings": [finding.__dict__ for finding in findings],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    if findings:
        for finding in findings:
            print(f"{finding.rule_id}: {finding.path}:{finding.line}: {finding.message}")
        return 0 if args.no_fail else 1

    print(f"Security scan passed; SARIF written to {sarif_path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
