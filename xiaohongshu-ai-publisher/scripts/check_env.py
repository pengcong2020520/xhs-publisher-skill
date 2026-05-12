#!/usr/bin/env python3
"""Check local prerequisites for the Xiaohongshu publisher skill."""

from __future__ import annotations

import json
import shutil
import subprocess


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def classify_status_failure(stderr: str) -> str:
    text = stderr.lower()
    if "permissionerror" in text or "operation not permitted" in text or "permission denied" in text:
        return "config_permission"
    if "login" in text or "cookie" in text or "cookies" in text or "登录" in stderr:
        return "auth_required"
    return "status_failed"


def check_xhs_status() -> dict[str, object]:
    if not command_available("xhs"):
        return {
            "ok": False,
            "status": "cli_missing",
            "hint": "Install with `uv tool install xiaohongshu-cli` or `pipx install xiaohongshu-cli`.",
        }

    completed = subprocess.run(["xhs", "status", "--json"], capture_output=True, text=True)
    status = "logged_in" if completed.returncode == 0 else classify_status_failure(completed.stderr)
    hints = {
        "logged_in": "",
        "auth_required": "Run `xhs login` or `xhs login --qrcode` before publishing.",
        "config_permission": "Allow xhs to create `~/.xiaohongshu-cli`, or run the check outside the sandbox.",
        "status_failed": "Run `xhs status` manually and inspect the error.",
    }
    return {
        "ok": completed.returncode == 0,
        "status": status,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "hint": hints[status],
    }


def check_environment() -> dict[str, object]:
    return {
        "xhs": check_xhs_status(),
        "npx": {
            "ok": command_available("npx"),
            "hint": "" if command_available("npx") else "Install Node.js or provide another screenshot path.",
        },
    }


def main() -> int:
    result = check_environment()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["xhs"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
