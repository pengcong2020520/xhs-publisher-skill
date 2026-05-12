#!/usr/bin/env python3
"""Render Xiaohongshu image placeholders into high-resolution HTML cards."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path


CARD_WIDTH = 1242
CARD_HEIGHT = 1656


def build_cards_from_placeholders(placeholders: list[dict[str, object]], title: str) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for placeholder in sorted(placeholders, key=lambda item: int(item["index"])):
        index = int(placeholder["index"])
        kind = str(placeholder["kind"])
        content = str(placeholder.get("content") or "").strip()
        headline = title if index == 1 else kind
        cards.append(
            {
                "filename": f"card-{index:02d}.html",
                "kind": kind,
                "headline": headline,
                "body": content,
            }
        )
    return cards


def render_card_html(card: dict[str, str]) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width={CARD_WIDTH}, initial-scale=1">
  <title>{html.escape(card["headline"])}</title>
  <style>
    {default_css()}
  </style>
</head>
<body>
  <main class="card-shell" style="width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px;">
    <p class="eyebrow">{html.escape(card["kind"])}</p>
    <h1>{html.escape(card["headline"])}</h1>
    <section class="insight">{format_body(card["body"])}</section>
    <footer>AI insight / Xiaohongshu</footer>
  </main>
</body>
</html>
"""


def default_css() -> str:
    return """
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: #f3f0ea;
      color: #161616;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
    }
    .card-shell {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 108px 96px 88px;
      background:
        linear-gradient(135deg, rgba(255,255,255,.9), rgba(255,255,255,.58)),
        #f7f1e8;
      border: 1px solid rgba(22, 22, 22, .14);
    }
    .eyebrow {
      margin: 0 0 42px;
      font-size: 38px;
      font-weight: 650;
      color: #b64032;
    }
    h1 {
      margin: 0;
      font-size: 96px;
      line-height: 1.08;
      font-weight: 760;
      letter-spacing: 0;
    }
    .insight {
      margin-top: 72px;
      padding-top: 52px;
      border-top: 3px solid rgba(22, 22, 22, .16);
      font-size: 48px;
      line-height: 1.42;
      font-weight: 520;
      white-space: pre-wrap;
    }
    footer {
      font-size: 30px;
      color: rgba(22, 22, 22, .48);
    }
    """


def format_body(body: str) -> str:
    return "<br>".join(html.escape(part.strip()) for part in body.splitlines() if part.strip())


def write_card_html(cards: list[dict[str, str]], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for card in cards:
        path = output_dir / card["filename"]
        path.write_text(render_card_html(card), encoding="utf-8")
        paths.append(path)
    return paths


def prepare_screenshot_html(source_html: str, scale: int) -> str:
    if scale <= 1:
        return source_html
    scaled_width = CARD_WIDTH * scale
    scaled_height = CARD_HEIGHT * scale
    injected = f"""
    html, body {{
      width: {scaled_width}px;
      height: {scaled_height}px;
      overflow: hidden;
    }}
    .card-shell {{
      transform: scale({scale});
      transform-origin: top left;
    }}
    """
    return source_html.replace("</style>", f"{injected}\n  </style>", 1)


def screenshot_cards(html_paths: list[Path], output_dir: Path, scale: int = 2) -> list[Path]:
    if not shutil.which("npx"):
        raise RuntimeError("npx is required for Playwright screenshots. Install Node.js and Playwright first.")

    image_paths: list[Path] = []
    for html_path in html_paths:
        image_path = output_dir / f"{html_path.stem}.png"
        screenshot_source = html_path
        viewport_width = CARD_WIDTH
        viewport_height = CARD_HEIGHT
        if scale > 1:
            screenshot_source = output_dir / f"{html_path.stem}-screenshot.html"
            screenshot_source.write_text(prepare_screenshot_html(html_path.read_text(encoding="utf-8"), scale), encoding="utf-8")
            viewport_width = CARD_WIDTH * scale
            viewport_height = CARD_HEIGHT * scale
        subprocess.run(
            [
                "npx",
                "playwright",
                "screenshot",
                "--viewport-size",
                f"{viewport_width},{viewport_height}",
                screenshot_source.resolve().as_uri(),
                str(image_path),
            ],
            check=True,
        )
        image_paths.append(image_path)
    return image_paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render Xiaohongshu cards from normalized JSON.")
    parser.add_argument("--input", required=True, help="Path to normalize_note.py JSON output.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--screenshot", action="store_true", help="Also create PNG screenshots with Playwright.")
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cards = build_cards_from_placeholders(payload.get("cards", []), args.title)
    html_paths = write_card_html(cards, Path(args.output_dir))
    result = {"html": [str(path) for path in html_paths], "images": []}
    if args.screenshot:
        result["images"] = [str(path) for path in screenshot_cards(html_paths, Path(args.output_dir), args.scale)]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
