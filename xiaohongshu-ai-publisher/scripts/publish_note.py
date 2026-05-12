#!/usr/bin/env python3
"""Build and optionally execute xiaohongshu-cli publishing commands."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def build_post_command(title: str, body: str, images: list[str]) -> list[str]:
    command = ["xhs", "post", "--title", title, "--body", body]
    for image in images:
        command.extend(["--images", image])
    return command


def validate_images(images: list[str]) -> list[str]:
    errors: list[str] = []
    for image in images:
        path = Path(image)
        if not path.exists():
            errors.append(f"{image} does not exist")
        elif path.suffix.lower() not in IMAGE_EXTENSIONS:
            errors.append(f"{image} is not a supported image; use png, jpg, jpeg, or webp")
        elif not path.is_file():
            errors.append(f"{image} is not a file")
    return errors


def diagnose_failure(stderr: str) -> str:
    text = stderr.lower()
    if "command not found" in text or "no such file or directory: 'xhs'" in text:
        return "cli_missing"
    if "login" in text or "登录" in stderr or "cookie" in text or "cookies" in text:
        return "auth_required"
    if "no such file" in text or "does not exist" in text or "missing" in text:
        return "missing_image"
    if "429" in text or "rate" in text or "too many requests" in text:
        return "rate_limited"
    if "captcha" in text or "461" in text or "471" in text:
        return "captcha_or_risk_control"
    return "unknown"


def run_publish(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, text=True)
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "diagnosis": "" if completed.returncode == 0 else diagnose_failure(completed.stderr),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run or execute xhs post commands.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--images", nargs="+", required=True)
    parser.add_argument("--execute", action="store_true", help="Actually run xhs post. Omit for dry-run.")
    args = parser.parse_args(argv)

    errors = validate_images(args.images)
    command = build_post_command(args.title, args.body, args.images)
    payload: dict[str, object] = {"command": command, "image_errors": errors, "executed": False}

    if errors:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2
    if not shutil.which("xhs"):
        payload["diagnosis"] = "cli_missing"
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 3
    if args.execute:
        payload.update(run_publish(command))
        payload["executed"] = True

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not payload.get("diagnosis") else 1


if __name__ == "__main__":
    raise SystemExit(main())
