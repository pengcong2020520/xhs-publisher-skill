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
    points = split_card_points(card["body"])
    points_html = render_points(points)
    hook = clean_card_body(card["body"])
    card_class = f"card-shell xiaohongshu-card card-{slug_kind(card['kind'])}"
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
  <main class="{card_class}" style="width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px;">
    <div class="topbar">
      <span class="badge">爆款观点</span>
      <span class="badge badge-light">{html.escape(card["kind"])}</span>
    </div>
    <section class="hero">
      <p class="kicker">AI 趋势观察</p>
      <h1>{html.escape(card["headline"])}</h1>
      <p class="hook">{html.escape(hook)}</p>
    </section>
    <section class="point-list">{points_html}</section>
    <footer>
      <span>建议收藏后慢慢看</span>
      <span>AI insight</span>
    </footer>
  </main>
</body>
</html>
"""


def default_css() -> str:
    return """
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: #ffe8e0;
      color: #191512;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
    }
    .card-shell {
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 72px 72px 64px;
      background:
        radial-gradient(circle at 12% 9%, rgba(255,255,255,.92) 0 11%, transparent 12%),
        linear-gradient(145deg, #ff4f3e 0%, #ff7a35 42%, #ffd96a 100%);
      border: 0;
    }
    .card-shell::before {
      content: "";
      position: absolute;
      inset: 34px;
      border: 6px solid rgba(25, 21, 18, .92);
      border-radius: 42px;
      pointer-events: none;
    }
    .card-shell::after {
      content: "AI";
      position: absolute;
      right: -42px;
      top: 202px;
      font-size: 250px;
      line-height: 1;
      font-weight: 900;
      color: rgba(255, 255, 255, .24);
      transform: rotate(9deg);
    }
    .topbar {
      position: relative;
      z-index: 1;
      display: flex;
      gap: 18px;
      align-items: center;
      justify-content: space-between;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 58px;
      padding: 0 28px;
      border: 4px solid #191512;
      border-radius: 999px;
      background: #191512;
      color: #fff8ea;
      font-size: 32px;
      font-weight: 800;
    }
    .badge-light {
      background: #fff8ea;
      color: #191512;
    }
    .hero {
      position: relative;
      z-index: 1;
      padding-top: 56px;
    }
    .kicker {
      display: inline-block;
      margin: 0 0 34px;
      padding: 14px 22px;
      border-radius: 16px;
      background: rgba(255, 248, 234, .92);
      color: #b62018;
      font-size: 36px;
      line-height: 1.15;
      font-weight: 900;
    }
    h1 {
      max-width: 1010px;
      margin: 0;
      font-size: 104px;
      line-height: 1.04;
      font-weight: 950;
      letter-spacing: 0;
      color: #fff8ea;
      text-shadow: 7px 7px 0 #191512;
    }
    .hook {
      max-width: 930px;
      margin: 42px 0 0;
      padding: 28px 32px;
      border: 5px solid #191512;
      border-radius: 28px;
      background: #fff8ea;
      box-shadow: 12px 12px 0 rgba(25, 21, 18, .9);
      font-size: 44px;
      line-height: 1.28;
      font-weight: 850;
    }
    .point-list {
      position: relative;
      z-index: 1;
      display: grid;
      gap: 22px;
      margin-top: 42px;
    }
    .point {
      display: grid;
      grid-template-columns: 76px 1fr;
      gap: 22px;
      align-items: start;
      padding: 28px 30px;
      border: 5px solid #191512;
      border-radius: 28px;
      background: rgba(255, 248, 234, .94);
      box-shadow: 9px 9px 0 rgba(25, 21, 18, .88);
    }
    .point-number {
      display: grid;
      place-items: center;
      width: 76px;
      height: 76px;
      border-radius: 22px;
      background: #191512;
      color: #fff8ea;
      font-size: 38px;
      line-height: 1;
      font-weight: 900;
    }
    .point-text {
      font-size: 42px;
      line-height: 1.25;
      font-weight: 850;
    }
    .card-cover .point-list {
      grid-template-columns: 1fr 1fr;
    }
    .card-cover .point {
      min-height: 150px;
    }
    footer {
      position: relative;
      z-index: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 36px;
      color: #191512;
      font-size: 32px;
      font-weight: 800;
    }
    .card-核心观点 {
      background:
        radial-gradient(circle at 90% 10%, rgba(255,255,255,.9) 0 10%, transparent 11%),
        linear-gradient(145deg, #1d1bff 0%, #7257ff 42%, #ffcf32 100%);
    }
    .card-总结行动 {
      background:
        radial-gradient(circle at 16% 14%, rgba(255,255,255,.9) 0 10%, transparent 11%),
        linear-gradient(145deg, #00a86b 0%, #25c6a2 42%, #fff06a 100%);
    }
    """


def format_body(body: str) -> str:
    return "<br>".join(html.escape(part.strip()) for part in body.splitlines() if part.strip())


def clean_card_body(body: str) -> str:
    text = body.strip()
    if ":" in text:
        return text.split(":", 1)[1].strip()
    if "：" in text:
        return text.split("：", 1)[1].strip()
    return text


def split_card_points(body: str) -> list[str]:
    cleaned = clean_card_body(body)
    parts = [part.strip(" ;；,，") for part in re_split_points(cleaned)]
    return [part for part in parts if part][:4] or [cleaned]


def re_split_points(text: str) -> list[str]:
    import re

    return re.split(r"[;；]\s*|\n+", text)


def render_points(points: list[str]) -> str:
    return "\n".join(
        f'<article class="point"><span class="point-number">{index}</span><span class="point-text">{html.escape(point)}</span></article>'
        for index, point in enumerate(points, 1)
    )


def slug_kind(kind: str) -> str:
    return "".join(char for char in kind if char.isalnum() or "\u4e00" <= char <= "\u9fff") or "card"


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
