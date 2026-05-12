# Xiaohongshu AI Publisher Skill Design

## Goal

Create a local Codex skill named `xiaohongshu-ai-publisher` that turns user-provided AI-related articles, Markdown, or `.txt/.md` files into Xiaohongshu-style viewpoint notes, generates three high-resolution HTML screenshot cards, and publishes only after explicit user confirmation.

## Confirmed Requirements

- Use `skill-creator` conventions for the skill structure.
- Develop and test the skill in this repository first.
- After local tests pass, package/install it globally under the user's Codex skills directory.
- Push development content to `https://github.com/pengcong2020520/xhs-publisher-skill`.
- Use `jackwener/xiaohongshu-cli` as the publishing backend.
- Publish directly with `xhs post` after user confirmation; draft-box support is a future extension because the referenced CLI documents direct post support, not draft-box support.
- Require strict three-step confirmation:
  1. Confirm topic angle.
  2. Confirm final copy and image placeholders.
  3. Confirm rendered image screenshots.
- Generate three images by default:
  1. Cover card.
  2. Core viewpoint card.
  3. Summary or action card.
- Generate images from HTML and screenshot them at high resolution.
- Use a viewpoint-insight account style by default.
- Support direct pasted text and local `.md/.txt` file paths.
- Use Xiaohongshu-friendly formatting with configurable tone; default to restrained and professional.
- Automatically fix ordered-list numbering issues.
- Run light risk checks for absolute claims, income promises, sensitive wording, and unsupported conclusions.
- Include initialization checks for CLI availability, login status, image paths, and publish arguments.
- On publish failure, diagnose the cause, ask before retrying, allow up to two consecutive retries, then preserve the copy and images.

## Architecture

The skill is a workflow guide plus a small script toolkit.

`SKILL.md` defines the agent-facing procedure, confirmation gates, and when to load references. Scripts handle deterministic steps that should not vary between runs: normalization, risk scanning, card rendering, environment checks, and publish command wrapping.

## Files

```text
xiaohongshu-ai-publisher/
  SKILL.md
  agents/openai.yaml
  scripts/
    check_env.py
    normalize_note.py
    render_cards.py
    publish_note.py
  assets/
    card_template.html
    card_style.css
  references/
    workflow.md
    style-guide.md
    xiaohongshu-cli.md
tests/
  test_normalize_note.py
  test_render_cards.py
  test_publish_note.py
```

## Workflow

1. Gather input from pasted text or a local `.md/.txt` file.
2. Create a run directory for artifacts.
3. Propose two or three viewpoint angles and ask the user to choose one.
4. Draft a Xiaohongshu note with title, body, tags, interaction close, and three image placeholders.
5. Normalize numbering and run light risk checks.
6. Ask the user to confirm the final copy and placeholders.
7. Render three HTML cards and high-resolution screenshots.
8. Ask the user to confirm the rendered images.
9. Check `xiaohongshu-cli` availability and login state.
10. Publish with `xhs post --title ... --body ... --images ...`.
11. If publishing fails, diagnose the error and ask whether to retry. Stop after two failed retries and preserve the artifact package.

## CLI Reference Basis

The referenced `jackwener/xiaohongshu-cli` README documents:

- Installation with `uv tool install xiaohongshu-cli` or `pipx install xiaohongshu-cli`.
- Authentication commands including `xhs login`, `xhs login --qrcode`, `xhs status`, and `xhs whoami`.
- Creator commands including `xhs post --title "标题" --body "正文" --images img.jpg`.
- Structured output with `--json` and `--yaml` for many commands.

## Validation

Local validation must include:

- Standard-library unit tests for numbering repair, risk scanning, placeholder extraction, card model creation, publish command generation, and error diagnosis.
- Skill validation with `quick_validate.py`.
- A dry-run publish command path that never posts.
- A card-rendering path that generates HTML without requiring live Xiaohongshu access.
