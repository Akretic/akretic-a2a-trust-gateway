from pathlib import Path


BANNED_PHRASES = [
    "unhackable",
    "guaranteed compliance",
    "mathematically impossible",
    "universal data-leak prevention",
    "fully autonomous enterprise action",
    "blockchain-grade",
    "legal non-repudiation",
    "marketplace-approved",
    "certified",
    "production-ready",
    "a2a-style",
    "client_input_required",
]


def test_public_copy_excludes_overclaims():
    docs_dir = Path(__file__).resolve().parents[1] / "docs"
    public_copy_paths = [
        docs_dir / "submission_answers_public.md",
        docs_dir / "submission_form_packet.md",
        docs_dir / "devpost_answers.md",
        docs_dir / "public_brief.md",
        docs_dir / "a2a_intent_map.md",
        docs_dir / "adk_alignment.md",
        docs_dir / "third_party_rights.md",
        docs_dir / "eligibility_statement.md",
        docs_dir / "submission_package.md",
        docs_dir / "submission_checklist.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in public_copy_paths)
    for phrase in BANNED_PHRASES:
        assert phrase not in text
