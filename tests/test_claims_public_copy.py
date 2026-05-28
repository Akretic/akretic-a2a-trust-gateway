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
]


def test_public_submission_copy_excludes_overclaims():
    text = (Path(__file__).resolve().parents[1] / "docs" / "submission_answers_public.md").read_text(encoding="utf-8").lower()
    for phrase in BANNED_PHRASES:
        assert phrase not in text
