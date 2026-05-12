# Xiaohongshu AI Publisher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Codex skill that converts AI content into confirmed Xiaohongshu viewpoint notes, renders three HTML screenshot cards, and wraps confirmed direct publishing through `xiaohongshu-cli`.

**Architecture:** The skill body provides the agent workflow and confirmation gates. Python scripts provide repeatable normalization, risk scanning, card rendering, environment checking, and dry-run or live publish command handling.

**Tech Stack:** Codex skill structure, Python 3 standard library, `unittest` tests, HTML/CSS templates, optional Playwright CLI or Python package for screenshots, `xiaohongshu-cli` for live publishing.

---

### Task 1: Scaffold Skill And Docs

**Files:**
- Create: `xiaohongshu-ai-publisher/SKILL.md`
- Create: `xiaohongshu-ai-publisher/agents/openai.yaml`
- Create: `xiaohongshu-ai-publisher/references/workflow.md`
- Create: `xiaohongshu-ai-publisher/references/style-guide.md`
- Create: `xiaohongshu-ai-publisher/references/xiaohongshu-cli.md`
- Create: `xiaohongshu-ai-publisher/assets/card_template.html`
- Create: `xiaohongshu-ai-publisher/assets/card_style.css`

- [ ] Create the skill directory with `init_skill.py`.
- [ ] Replace generated placeholders with final workflow instructions.
- [ ] Add references for workflow, style, and CLI usage.
- [ ] Add HTML/CSS card assets.

### Task 2: Normalize Note Script

**Files:**
- Create: `tests/test_normalize_note.py`
- Create: `xiaohongshu-ai-publisher/scripts/normalize_note.py`

- [ ] Write failing tests for ordered-list repair, risk scanning, and image placeholder extraction.
- [ ] Run `python3 -m unittest tests.test_normalize_note -v` and confirm tests fail for missing implementation.
- [ ] Implement the script with pure Python.
- [ ] Run the tests and confirm they pass.

### Task 3: Render Cards Script

**Files:**
- Create: `tests/test_render_cards.py`
- Create: `xiaohongshu-ai-publisher/scripts/render_cards.py`

- [ ] Write failing tests for three-card extraction and HTML output generation.
- [ ] Run `python3 -m unittest tests.test_render_cards -v` and confirm tests fail for missing implementation.
- [ ] Implement HTML rendering and optional screenshot invocation.
- [ ] Run the tests and confirm they pass.

### Task 4: Environment And Publish Scripts

**Files:**
- Create: `tests/test_publish_note.py`
- Create: `xiaohongshu-ai-publisher/scripts/check_env.py`
- Create: `xiaohongshu-ai-publisher/scripts/publish_note.py`

- [ ] Write failing tests for command generation, image validation, and error diagnosis.
- [ ] Run `python3 -m unittest tests.test_publish_note -v` and confirm tests fail for missing implementation.
- [ ] Implement environment checks and dry-run publish wrapping.
- [ ] Run the tests and confirm they pass.

### Task 5: Validate, Package, Commit, Push

**Files:**
- Modify: all created files as needed.

- [ ] Run `python3 -m unittest discover -s tests -v`.
- [ ] Run `quick_validate.py xiaohongshu-ai-publisher`.
- [ ] Install a copy into the global Codex skills directory only after local validation.
- [ ] Run validation on the global copy.
- [ ] Commit all source files.
- [ ] Push to `origin main`.
