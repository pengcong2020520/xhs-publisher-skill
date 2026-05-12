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
    hook = build_hook(card, points)
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
      <span class="badge">观点洞察</span>
      <span class="badge badge-light">{html.escape(card["kind"])}</span>
    </div>
    <section class="hero">
      <p class="kicker">AI 趋势观察</p>
      <h1>{html.escape(card["headline"])}</h1>
      <p class="hook">{html.escape(hook)}</p>
    </section>
    <section class="point-list">{points_html}</section>
    <footer>
      <span>先收藏再复盘</span>
      <span>AI SKILL NOTE</span>
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
      background: #f5f2e9;
      color: #161616;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
    }
    .card-shell {
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 76px 74px 64px;
      background:
        linear-gradient(90deg, rgba(22,22,22,.08) 1px, transparent 1px),
        linear-gradient(0deg, rgba(22,22,22,.08) 1px, transparent 1px),
        #f9f6eb;
      background-size: 44px 44px;
      border: 0;
    }
    .card-shell::before {
      content: "";
      position: absolute;
      inset: 48px;
      border: 5px solid rgba(22, 22, 22, .92);
      border-radius: 0;
      pointer-events: none;
    }
    .card-shell::after {
      content: "";
      position: absolute;
      right: -170px;
      top: -74px;
      width: 430px;
      height: 128px;
      background: #e65f2f;
      transform: rotate(45deg);
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
      min-height: 54px;
      padding: 0 24px;
      border: 4px solid #161616;
      border-radius: 0;
      background: #161616;
      color: #fbf7eb;
      font-size: 30px;
      font-weight: 850;
    }
    .badge-light {
      background: #b9ff59;
      color: #161616;
    }
    .hero {
      position: relative;
      z-index: 1;
      padding-top: 58px;
    }
    .kicker {
      display: inline-block;
      margin: 0 0 32px;
      padding: 12px 20px;
      border: 4px solid #161616;
      border-radius: 0;
      background: #ffffff;
      color: #161616;
      font-size: 36px;
      line-height: 1.15;
      font-weight: 900;
      box-shadow: 8px 8px 0 #59baff;
    }
    h1 {
      max-width: 1020px;
      margin: 0;
      font-size: 100px;
      line-height: 1.03;
      font-weight: 950;
      letter-spacing: 0;
      color: #161616;
      text-shadow: 5px 5px 0 #ffffff;
    }
    .hook {
      display: inline-block;
      max-width: 940px;
      margin: 40px 0 0;
      padding: 18px 26px;
      border: 5px solid #161616;
      border-radius: 0;
      background: #b9ff59;
      box-shadow: 10px 10px 0 #161616;
      font-size: 42px;
      line-height: 1.2;
      font-weight: 900;
    }
    .point-list {
      position: relative;
      z-index: 1;
      display: grid;
      gap: 26px;
      margin-top: 42px;
    }
    .point {
      display: grid;
      grid-template-columns: 82px 1fr;
      gap: 22px;
      align-items: start;
      padding: 30px 32px;
      border: 5px solid #161616;
      border-radius: 0;
      background: #ffffff;
      box-shadow: 9px 9px 0 rgba(22, 22, 22, .92);
    }
    .point-number {
      display: grid;
      place-items: center;
      width: 82px;
      height: 82px;
      border-radius: 999px;
      background: #161616;
      color: #ffffff;
      font-size: 38px;
      line-height: 1;
      font-weight: 900;
    }
    .point-text {
      font-size: 42px;
      line-height: 1.25;
      font-weight: 850;
    }
    .card-cover .point {
      background: #fffef9;
    }
    .card-cover .point-text {
      font-size: 48px;
      line-height: 1.18;
    }
    footer {
      position: relative;
      z-index: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 36px;
      color: #77736c;
      font-size: 30px;
      font-weight: 800;
    }
    .card-核心观点 {
      background:
        radial-gradient(circle at 13% 13%, rgba(112,56,255,.55) 0 12%, transparent 25%),
        radial-gradient(circle at 90% 90%, rgba(255,70,130,.42) 0 12%, transparent 27%),
        linear-gradient(145deg, #070b16 0%, #11152a 100%);
      color: #ffffff;
    }
    .card-核心观点::before {
      border-color: rgba(255, 255, 255, .22);
      box-shadow: inset 0 0 90px rgba(255,255,255,.08);
    }
    .card-核心观点::after {
      background: rgba(105, 78, 255, .62);
    }
    .card-核心观点 .badge {
      border-color: rgba(255,255,255,.92);
      background: rgba(255,255,255,.92);
      color: #090c17;
    }
    .card-核心观点 .badge-light {
      background: transparent;
      color: #ffffff;
    }
    .card-核心观点 .kicker {
      border-color: rgba(255,255,255,.35);
      background: rgba(255,255,255,.08);
      color: #ffffff;
      box-shadow: 8px 8px 0 rgba(105, 78, 255, .7);
    }
    .card-核心观点 h1 {
      color: #ffffff;
      text-shadow: 0 0 26px rgba(255,255,255,.22);
    }
    .card-核心观点 .hook {
      border-color: rgba(255,255,255,.34);
      background: rgba(255,255,255,.09);
      color: #ffffff;
      box-shadow: 10px 10px 0 rgba(105, 78, 255, .65);
    }
    .card-核心观点 .point {
      border-color: rgba(255,255,255,.26);
      background: rgba(255,255,255,.1);
      box-shadow: 12px 12px 0 rgba(0,0,0,.35);
    }
    .card-核心观点 .point-number {
      background: #ffffff;
      color: #090c17;
    }
    .card-核心观点 footer {
      color: rgba(255,255,255,.62);
    }
    .card-总结行动 {
      background:
        linear-gradient(90deg, rgba(22,22,22,.07) 1px, transparent 1px),
        linear-gradient(0deg, rgba(22,22,22,.07) 1px, transparent 1px),
        #ffffff;
      background-size: 34px 34px;
    }
    .card-总结行动 .kicker {
      box-shadow: 8px 8px 0 #ffb02e;
    }
    .card-总结行动 .hook {
      background: #59baff;
      color: #161616;
    }
    .card-总结行动 .point:nth-child(2) {
      transform: rotate(-1deg);
    }
    .card-总结行动 .point:nth-child(3) {
      transform: rotate(1deg);
    }
    .card-问题背景 .hook {
      background: #ffb02e;
      color: #161616;
    }
    .card-问题背景 .point:nth-child(1) {
      transform: rotate(-1deg);
    }
    .card-问题背景 .point:nth-child(2) {
      transform: rotate(1deg);
    }
    .card-方法拆解 {
      background:
        linear-gradient(90deg, rgba(22,22,22,.07) 1px, transparent 1px),
        linear-gradient(0deg, rgba(22,22,22,.07) 1px, transparent 1px),
        #f6fbff;
      background-size: 34px 34px;
    }
    .card-方法拆解 .kicker {
      box-shadow: 8px 8px 0 #b9ff59;
    }
    .card-方法拆解 .hook {
      background: #59baff;
      color: #161616;
    }
    .card-方法拆解 .point-number {
      background: #59baff;
      color: #161616;
      border: 5px solid #161616;
    }
    .card-案例启发,
    .card-金句总结 {
      background:
        radial-gradient(circle at 18% 12%, rgba(185,255,89,.42) 0 10%, transparent 22%),
        linear-gradient(90deg, rgba(22,22,22,.07) 1px, transparent 1px),
        linear-gradient(0deg, rgba(22,22,22,.07) 1px, transparent 1px),
        #fffdf6;
      background-size: auto, 38px 38px, 38px 38px, auto;
    }
    .card-案例启发 .hook,
    .card-金句总结 .hook {
      background: #161616;
      color: #ffffff;
    }
    .card-案例启发 .point,
    .card-金句总结 .point {
      background: #fffef9;
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

    return re.split(r"[;；,，、]\s*|\n+", text)


def build_hook(card: dict[str, str], points: list[str]) -> str:
    if len(points) <= 1:
        return points[0] if points else clean_card_body(card["body"])
    if card["kind"] == "封面":
        return "这不是替代焦虑，是能力平权"
    if card["kind"] == "问题背景":
        return "先把矛盾讲清楚"
    if card["kind"] == "核心观点":
        return f"{len(points)} 个判断，一图看懂"
    if card["kind"] == "方法拆解":
        return "照这个路径执行"
    if card["kind"] == "总结行动":
        return f"{len(points)} 个动作，马上能练"
    if card["kind"] == "案例启发":
        return "把经验变成模板"
    if card["kind"] == "金句总结":
        return "最后留一句判断"
    return f"{len(points)} 个重点，拆开看"


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
