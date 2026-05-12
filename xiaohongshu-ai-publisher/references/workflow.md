# Workflow Reference

## Run Directory

Create a dedicated directory for every post:

```text
runs/YYYYMMDD-HHMM-topic/
  source.md
  normalized.json
  final-note.md
  cards/
    card-01.html
    card-02.html
    card-03.html
    card-01.png
    card-02.png
    card-03.png
  publish-command.json
  publish-error.log
```

## Confirmation Sequence

1. Angle confirmation: show 2-3 candidate angles and wait for the user to choose.
2. Copy confirmation: show the final title, body, tags, and `[图N: ...]` placeholders.
3. Image confirmation: show generated image paths and, when possible, preview screenshots.

Only after these gates may the agent execute a live publish command.

If the user confirms a new visual style after reviewing screenshots, update `scripts/render_cards.py`, `references/style-guide.md`, and focused tests before installing or packaging the skill. Do not turn a rejected one-off visual experiment into the reusable theme.

## Default Commands

Normalize:

```bash
python3 xiaohongshu-ai-publisher/scripts/normalize_note.py --input runs/<run>/final-note.md --output runs/<run>/normalized.json
```

Render HTML:

```bash
python3 xiaohongshu-ai-publisher/scripts/render_cards.py --input runs/<run>/normalized.json --title "<title>" --output-dir runs/<run>/cards
```

Render PNG screenshots:

```bash
python3 xiaohongshu-ai-publisher/scripts/render_cards.py --input runs/<run>/normalized.json --title "<title>" --output-dir runs/<run>/cards --screenshot --scale 2
```

Dry-run publish:

```bash
python3 xiaohongshu-ai-publisher/scripts/publish_note.py --title "<title>" --body "<body>" --images runs/<run>/cards/card-01.png runs/<run>/cards/card-02.png runs/<run>/cards/card-03.png
```

Live publish:

```bash
python3 xiaohongshu-ai-publisher/scripts/publish_note.py --title "<title>" --body "<body>" --images runs/<run>/cards/card-01.png runs/<run>/cards/card-02.png runs/<run>/cards/card-03.png --execute
```
