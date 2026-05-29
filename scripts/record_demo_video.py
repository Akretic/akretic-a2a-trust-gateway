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
    from playwright.sync_api import Error as PlaywrightError
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
    parser.add_argument(
        "--basename",
        default="akretic-p5-demo-footage",
        help="Output basename without extension",
    )
    return parser.parse_args()


def install_cursor(page) -> None:
    page.add_style_tag(
        content="""
        #akretic-demo-cursor {
          position: fixed;
          z-index: 2147483647;
          width: 22px;
          height: 22px;
          left: 0;
          top: 0;
          border-radius: 50%;
          border: 3px solid #0f766e;
          background: rgba(20, 184, 166, 0.18);
          box-shadow: 0 0 0 6px rgba(20, 184, 166, 0.18);
          pointer-events: none;
          transform: translate(-40px, -40px);
          transition: transform 650ms ease, box-shadow 180ms ease, background 180ms ease;
        }
        #akretic-demo-cursor.clicking {
          background: rgba(249, 115, 22, 0.28);
          box-shadow: 0 0 0 13px rgba(249, 115, 22, 0.18);
        }
        """
    )
    page.evaluate(
        """
        () => {
          const existing = document.querySelector("#akretic-demo-cursor");
          if (existing) existing.remove();
          const cursor = document.createElement("div");
          cursor.id = "akretic-demo-cursor";
          document.body.appendChild(cursor);
          window.akreticMoveCursor = (x, y, clicking = false) => {
            cursor.style.transform = `translate(${x}px, ${y}px)`;
            cursor.classList.toggle("clicking", clicking);
          };
        }
        """
    )


def move_cursor_to(page, selector: str, *, click: bool = False, delay_ms: int = 850) -> None:
    locator = page.locator(selector).first
    locator.scroll_into_view_if_needed(timeout=30_000)
    box = locator.bounding_box(timeout=30_000)
    if box is None:
        return
    x = box["x"] + min(box["width"] * 0.55, box["width"] - 8)
    y = box["y"] + min(box["height"] * 0.55, box["height"] - 8)
    page.evaluate("(args) => window.akreticMoveCursor(args.x, args.y, false)", {"x": x, "y": y})
    page.wait_for_timeout(delay_ms)
    if click:
        page.evaluate("(args) => window.akreticMoveCursor(args.x, args.y, true)", {"x": x, "y": y})
        page.wait_for_timeout(220)
        page.mouse.click(x, y)
        try:
            page.evaluate("(args) => window.akreticMoveCursor(args.x, args.y, false)", {"x": x, "y": y})
        except PlaywrightError:
            pass


def wait_and_scroll(page, text: str, delay_ms: int = 3500) -> None:
    locator = page.get_by_text(text).first
    locator.scroll_into_view_if_needed(timeout=30_000)
    box = locator.bounding_box(timeout=30_000)
    if box is not None:
        x = box["x"] + min(box["width"] * 0.5, box["width"] - 8)
        y = box["y"] + min(box["height"] * 0.5, box["height"] - 8)
        page.evaluate("(args) => window.akreticMoveCursor(args.x, args.y, false)", {"x": x, "y": y})
    page.wait_for_timeout(delay_ms)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    final_video = output_dir / f"{args.basename}.webm"
    metadata_path = output_dir / f"{args.basename}.metadata.json"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(temp_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()

        page.goto(args.url, wait_until="networkidle", timeout=120_000)
        install_cursor(page)
        page.wait_for_timeout(3_000)
        move_cursor_to(page, "textarea[name='query']", delay_ms=1_600)
        move_cursor_to(page, "button[type='submit']", click=True)
        page.wait_for_load_state("networkidle", timeout=180_000)
        page.wait_for_selector("text=Denied Sources", timeout=180_000)
        install_cursor(page)

        wait_and_scroll(page, "VendorNova Review", delay_ms=4_000)
        wait_and_scroll(page, "Vertex/Gemini summarization path", delay_ms=4_500)
        wait_and_scroll(page, "Denied before model context", delay_ms=5_500)
        wait_and_scroll(page, "Permitted Sources", delay_ms=4_000)
        wait_and_scroll(page, "Denied Sources", delay_ms=4_500)
        wait_and_scroll(page, "Policy Decision", delay_ms=3_500)
        wait_and_scroll(page, "A2A Proof", delay_ms=5_500)
        wait_and_scroll(page, "Approval Request", delay_ms=4_000)
        move_cursor_to(page, "select[name='reviewer_persona']", delay_ms=1_200)
        move_cursor_to(page, "select[name='status']", delay_ms=1_200)
        move_cursor_to(page, "input[name='reason']", delay_ms=1_400)

        move_cursor_to(page, "button[type='submit']", click=True)
        page.wait_for_load_state("networkidle", timeout=180_000)
        page.wait_for_selector("text=Approval Decision", timeout=180_000)
        install_cursor(page)
        wait_and_scroll(page, "Decision Result", delay_ms=5_000)
        wait_and_scroll(page, "Evidence Verification", delay_ms=8_000)

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
        "note": "Silent browser walkthrough with synthetic cursor overlay; add narration or upload wrapper as needed.",
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
