---
name: xiaohongshu-ai-publisher
description: Create confirmed Xiaohongshu (小红书) AI-content image posts from pasted articles, Markdown, or local .md/.txt files. Use when the user wants to turn AI-related content into Xiaohongshu viewpoint copy, repair numbering, generate three high-resolution HTML screenshot cards, check xiaohongshu-cli login status, and publish with explicit confirmation through `xhs post`.
---

# Xiaohongshu AI Publisher

Use this skill to transform AI-related long-form content into a Xiaohongshu viewpoint note with three generated cards and a guarded direct-publish flow.

## Non-Negotiable Gates

Never call `xhs post` until all three confirmations are complete:

1. Confirm the topic angle.
2. Confirm final copy with image placeholders.
3. Confirm rendered image screenshots.

If the user asks to skip confirmation, explain that this skill requires confirmation because it publishes directly.

## Inputs

Accept either:

- Pasted article text or Markdown.
- A local `.md` or `.txt` path.

Create a run directory before generating artifacts, such as `runs/YYYYMMDD-HHMM-topic/`. Preserve the original input as `source.md` or `source.txt`.

## Workflow

1. Read the source content.
2. Propose 2-3 viewpoint angles in a restrained professional Xiaohongshu style.
3. Ask the user to choose one angle.
4. Draft the note with:
   - A strong but non-exaggerated title.
   - Short paragraphs.
   - Clean ordered lists.
   - Three image placeholders:
     - `[图1: 封面 | 核心钩子: ...]`
     - `[图2: 核心观点 | 三个判断: ...]`
     - `[图3: 总结行动 | 建议清单: ...]`
   - 3-6 Xiaohongshu tags.
   - A calm interaction question.
5. Run `scripts/normalize_note.py` to repair numbering and scan light risks.
6. Show the normalized copy and risk notes. Ask for copy confirmation.
7. Run `scripts/render_cards.py` to create three HTML cards. Use `--screenshot` when Playwright is available and the user is ready for image preview.
8. Show the card paths or screenshots. Ask for image confirmation.
9. Run `scripts/check_env.py`.
10. Run `scripts/publish_note.py` without `--execute` first to show the exact dry-run command.
11. After final publish confirmation, run `scripts/publish_note.py --execute`.

## Scripts

- `scripts/normalize_note.py`
  - Repairs ordered-list numbering.
  - Extracts image placeholders.
  - Flags light risk expressions.
  - Reads stdin or `--input`; writes JSON to stdout or `--output`.

- `scripts/render_cards.py`
  - Reads normalized JSON.
  - Builds three HTML card files.
  - Optionally creates PNG screenshots through Playwright with `--screenshot`.
  - Default card size is 1242x1656 with optional 2x device scale.

- `scripts/check_env.py`
  - Checks `xhs` availability.
  - Runs `xhs status --json`.
  - Checks `npx` availability for screenshot generation.

- `scripts/publish_note.py`
  - Validates image paths.
  - Builds `xhs post --title ... --body ... --images ...`.
  - Defaults to dry-run.
  - Executes only with `--execute`.
  - Classifies common failures.

## References

- Read `references/workflow.md` when orchestrating a full publish run.
- Read `references/style-guide.md` before drafting copy or card text.
- Read `references/xiaohongshu-cli.md` before installing, checking auth, or publishing.

## Failure Handling

If publishing fails:

1. Read the diagnosis from `publish_note.py`.
2. Explain the likely cause and the recovery command.
3. Ask the user whether to retry.
4. Retry at most two consecutive times.
5. If retries fail, stop and preserve the run directory with source copy, normalized copy, HTML, images, command, and logs.

Do not delete artifacts after a failed publish.

