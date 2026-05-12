# Xiaohongshu AI Publisher Skill

Codex skill for turning AI-related articles into confirmed Xiaohongshu image notes with 5-6 high-resolution cards, strict confirmation gates, and `xiaohongshu-cli` publishing.

## Install

Run this first:

```bash
npx github:pengcong2020520/xhs-publisher-skill install
```

Then install the runtime dependencies:

```bash
npx github:pengcong2020520/xhs-publisher-skill env
```

This installs:

- `xiaohongshu-cli`, which provides the `xhs` command.
- Playwright Chromium for high-resolution HTML card screenshots.

## Login

After the environment is installed, log in to Xiaohongshu:

```bash
npx github:pengcong2020520/xhs-publisher-skill login
```

If you prefer the browser login flow:

```bash
npx github:pengcong2020520/xhs-publisher-skill login --browser
```

Check the environment:

```bash
npx github:pengcong2020520/xhs-publisher-skill check
```

## Use In Codex

After installation and login, ask Codex:

```text
使用 xiaohongshu-ai-publisher skill，把这篇 AI 文章转成小红书图文笔记并发布。文章路径：/path/to/article.md
```

The skill requires three confirmations before publishing:

1. Confirm the topic angle.
2. Confirm the final copy and image placeholders.
3. Confirm the rendered card images.

Only after those confirmations will it run `xhs post`.

## Diagnostics

```bash
npx github:pengcong2020520/xhs-publisher-skill doctor
```

This prints the local Codex skill path and checks whether `xhs`, `npx`, and `python3` are available.
