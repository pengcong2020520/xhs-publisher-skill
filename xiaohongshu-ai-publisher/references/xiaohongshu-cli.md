# xiaohongshu-cli Reference

This skill uses `jackwener/xiaohongshu-cli` as the publishing backend.

## Install

Recommended:

```bash
uv tool install xiaohongshu-cli
```

Alternative:

```bash
pipx install xiaohongshu-cli
```

## Auth

```bash
xhs login
xhs login --qrcode
xhs status
xhs whoami
```

Run `scripts/check_env.py` before publishing. If auth is missing or expired, ask the user to run `xhs login` or `xhs login --qrcode`.

## Direct Publish

The documented creator command is:

```bash
xhs post --title "标题" --body "正文" --images img.jpg
```

This skill does not assume draft-box support. It publishes directly only after explicit confirmation.

## Failure Classes

- `cli_missing`: install `xiaohongshu-cli`.
- `auth_required`: run login.
- `missing_image`: regenerate images or fix paths.
- `rate_limited`: wait before retrying.
- `captcha_or_risk_control`: stop and let the user resolve the platform challenge.
- `unknown`: preserve logs and do not retry blindly.
