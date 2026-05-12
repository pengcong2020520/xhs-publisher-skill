#!/usr/bin/env python3
"""Normalize Xiaohongshu note copy before card rendering or publishing."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ORDERED_RE = re.compile(r"^(\s*)(\d+)([.、)])(\s*)(.+)$")
PLACEHOLDER_RE = re.compile(r"\[图\s*(\d+)\s*:\s*([^|\]]+)(?:\|\s*([^\]]+))?\]")

RISK_PATTERNS = {
    "absolute_claim": [
        "一定",
        "必然",
        "所有人",
        "百分百",
        "100%",
        "绝对",
    ],
    "income_promise": [
        "月入",
        "年入",
        "躺赚",
        "稳赚",
        "暴富",
        "保底收益",
    ],
    "sensitive_wording": [
        "割韭菜",
        "封号",
        "灰产",
        "黑产",
    ],
    "unsupported_claim": [
        "已经证实",
        "官方确认",
        "所有人都会",
        "行业公认",
    ],
}


def renumber_ordered_lists(text: str) -> str:
    lines = text.splitlines()
    counters: dict[int, int] = {}
    markers: dict[int, str] = {}
    previous_key: int | None = None
    normalized: list[str] = []

    for line in lines:
        match = ORDERED_RE.match(line)
        if not match:
            if line.strip():
                previous_key = None
            else:
                counters.clear()
                previous_key = None
            normalized.append(line)
            continue

        indent, _number, marker, spacing, content = match.groups()
        key = len(indent)
        if previous_key != key:
            counters[key] = 1
            markers[key] = marker
        else:
            counters[key] = counters.get(key, 0) + 1
        previous_key = key
        normalized.append(f"{indent}{counters[key]}{markers[key]}{spacing or ' '}{content}")

    return "\n".join(normalized)


def extract_image_placeholders(text: str) -> list[dict[str, object]]:
    cards: list[dict[str, object]] = []
    for match in PLACEHOLDER_RE.finditer(text):
        index = int(match.group(1))
        kind = match.group(2).strip()
        content = (match.group(3) or "").strip()
        cards.append({"index": index, "kind": kind, "content": content})
    return cards


def scan_light_risks(text: str) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []
    for category, patterns in RISK_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                risks.append(
                    {
                        "category": category,
                        "match": pattern,
                        "message": risk_message(category, pattern),
                    }
                )
                break
    return risks


def risk_message(category: str, pattern: str) -> str:
    messages = {
        "absolute_claim": "Use a less absolute expression before publishing.",
        "income_promise": "Avoid promising income or guaranteed results.",
        "sensitive_wording": "Rewrite platform-sensitive wording in a calmer style.",
        "unsupported_claim": "Add evidence, attribution, or soften the claim.",
    }
    return f"{messages.get(category, 'Review this expression.')} Matched: {pattern}"


def normalize_payload(text: str) -> dict[str, object]:
    normalized = renumber_ordered_lists(text)
    return {
        "text": normalized,
        "cards": extract_image_placeholders(normalized),
        "risks": scan_light_risks(normalized),
    }


def read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize Xiaohongshu note copy.")
    parser.add_argument("--input", help="Path to a .md or .txt note. Reads stdin when omitted.")
    parser.add_argument("--output", help="Write JSON payload to this path.")
    args = parser.parse_args(argv)

    payload = normalize_payload(read_input(args.input))
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
