"""Render the public brief markdown to a public-safe PDF."""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate


SOURCE = Path("docs/public_brief.md")
DIST_OUTPUT = Path("dist/akretic-a2a-trust-gateway-public-brief.pdf")
LEGACY_OUTPUT = Path("output/pdf/akretic-a2a-trust-gateway-public-brief.pdf")

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


def clean_inline(text: str) -> str:
    text = text.strip()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def build_story(markdown: str):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="AkreticTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#111827"),
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="AkreticHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="AkreticBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="AkreticBullet",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=10,
        )
    )

    story = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            story.append(Paragraph(clean_inline(line[2:]), styles["AkreticTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(clean_inline(line[3:]), styles["AkreticHeading"]))
        elif line.startswith("- "):
            story.append(Paragraph("- " + clean_inline(line[2:]), styles["AkreticBullet"]))
        elif re.match(r"^\d+\. ", line):
            story.append(Paragraph("- " + clean_inline(re.sub(r"^\d+\. ", "", line)), styles["AkreticBullet"]))
        else:
            story.append(Paragraph(clean_inline(line), styles["AkreticBody"]))
    return story


def main() -> None:
    markdown = SOURCE.read_text(encoding="utf-8")
    lowered = markdown.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            raise SystemExit(f"Public brief contains banned phrase: {phrase}")

    DIST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    LEGACY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(DIST_OUTPUT),
        pagesize=LETTER,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Akretic A2A Trust Gateway Public Brief",
        author="Akretic",
    )
    doc.build(build_story(markdown))
    LEGACY_OUTPUT.write_bytes(DIST_OUTPUT.read_bytes())

    reader = PdfReader(str(DIST_OUTPUT))
    if not reader.pages:
        raise SystemExit("Generated PDF has no pages")
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    for expected in ["Akretic A2A Trust Gateway", "challenge prototype", "synthetic"]:
        if expected.lower() not in extracted.lower():
            raise SystemExit(f"Generated PDF text missing expected phrase: {expected}")

    print(
        {
            "pdf": str(DIST_OUTPUT),
            "legacy_copy": str(LEGACY_OUTPUT),
            "pages": len(reader.pages),
        }
    )


if __name__ == "__main__":
    main()
