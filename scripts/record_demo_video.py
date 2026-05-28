"""Record a raw browser walkthrough of the public Cloud Run P0 demo.

This creates a silent WebM capture for submission editing. It is intentionally
separate from the app runtime and uses Playwright only as local tooling.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:  # pragma: no cover - local tooling guard
    raise SystemExit(
        "Missing optional local dependency: playwright. "
        "Install with `.\\.venv\\Scripts\\python.exe -m pip install playwright` "
        "and `.\\.venv\\Scripts\\python.exe -m playwright install chromium`."
    ) from exc


DEFAULT_URL = "https://akretic-demo-ui-oes3slkexq-uc.a.run.app"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Public demo URL")
    parser.add_argument(
        "--output-dir",
        default="output/playwright/video",
        help="Directory for raw video and metadata",
    )
    return parser.parse_args()


def wait_and_scroll(page, text: str, delay_ms: int = 1500) -> None:
    page.get_by_text(text).first.scroll_into_view_if_needed(timeout=30_000)
    page.wait_for_timeout(delay_ms)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    final_video = output_dir / "akretic-p0-demo-raw.webm"
    metadata_path = output_dir / "akretic-p0-demo-raw.metadata.json"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(temp_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()

        page.goto(args.url, wait_until="networkidle", timeout=120_000)
        page.wait_for_timeout(2_000)
        page.get_by_role("button", name="Start VendorNova Review").click()
        page.wait_for_load_state("networkidle", timeout=180_000)
        page.wait_for_selector("text=Denied Sources", timeout=180_000)

        for label in [
            "VendorNova Review",
            "Permitted Sources",
            "Denied Sources",
            "Policy Decision",
            "Approval Request",
            "Evidence Verification",
        ]:
            wait_and_scroll(page, label)

        page.get_by_role("button", name="Record reviewer decision").click()
        page.wait_for_load_state("networkidle", timeout=180_000)
        page.wait_for_selector("text=Approval Decision", timeout=180_000)
        wait_and_scroll(page, "Decision Result")
        wait_and_scroll(page, "Evidence Verification", delay_ms=2_000)

        video = page.video
        context.close()
        browser.close()

        if video is None:
            raise RuntimeError("Playwright did not produce a video artifact")

        source_video = Path(video.path())
        if final_video.exists():
            final_video.unlink()
        shutil.move(str(source_video), final_video)

    for path in temp_dir.glob("*"):
        path.unlink()
    temp_dir.rmdir()

    metadata = {
        "url": args.url,
        "video": str(final_video),
        "generated_at": datetime.now(UTC).isoformat(),
        "format": "webm",
        "audio": False,
        "note": "Raw silent browser walkthrough; add narration or upload wrapper as needed.",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
