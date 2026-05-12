# Xiaohongshu AI Publisher Skill

把 AI 相关文章或 Markdown 转成小红书图文笔记的 Agent Skill。

能力范围：

- 生成小红书观点洞察型文案。
- 自动修复序号错乱。
- 默认生成 5 张高清图文卡，内容足够时可扩展到 6 张。
- 使用 HTML 截图生成封面图和配图。
- 严格三步确认后才调用 `xiaohongshu-cli` 发布。

## 安装 Skill

### Codex

```bash
mkdir -p ~/.codex/skills
tmpdir="$(mktemp -d)"
git clone https://github.com/pengcong2020520/xhs-publisher-skill.git "$tmpdir/xhs-publisher-skill"
cp -R "$tmpdir/xhs-publisher-skill/xiaohongshu-ai-publisher" ~/.codex/skills/
```

### Claude Code

Claude Code 的个人 Skills 目录是 `~/.claude/skills/`。安装命令：

```bash
mkdir -p ~/.claude/skills
tmpdir="$(mktemp -d)"
git clone https://github.com/pengcong2020520/xhs-publisher-skill.git "$tmpdir/xhs-publisher-skill"
cp -R "$tmpdir/xhs-publisher-skill/xiaohongshu-ai-publisher" ~/.claude/skills/
```

项目级安装：

```bash
mkdir -p .claude/skills
tmpdir="$(mktemp -d)"
git clone https://github.com/pengcong2020520/xhs-publisher-skill.git "$tmpdir/xhs-publisher-skill"
cp -R "$tmpdir/xhs-publisher-skill/xiaohongshu-ai-publisher" .claude/skills/
```

安装后重启 Codex 或 Claude Code，让 Skill 重新加载。

## 安装运行环境

先安装 `xiaohongshu-cli`：

```bash
uv tool install xiaohongshu-cli
```

如果没有 `uv`，可以用 `pipx`：

```bash
pipx install xiaohongshu-cli
```

安装 Playwright Chromium，用于高清 HTML 截图：

```bash
npx playwright install chromium
```

## 登录小红书

```bash
xhs login --qrcode
xhs status
```

如果二维码登录不适合当前环境，可以使用浏览器登录：

```bash
xhs login
```

确认登录成功后，`xhs status` 应返回 authenticated/logged_in 状态。

## 使用

在 Codex 或 Claude Code 中提出任务：

```text
使用 xiaohongshu-ai-publisher skill，把这篇 AI 文章转成小红书图文笔记并发布。文章路径：/path/to/article.md
```

Skill 会严格等待三次确认：

1. 选题角度确认。
2. 最终文案和图片占位符确认。
3. 渲染后的图片确认。

只有收到最终发布确认后，才会调用 `xhs post`。

## 仓库结构

```text
.
├── readme.md
└── xiaohongshu-ai-publisher/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    ├── references/
    └── scripts/
```

## 参考

- Claude Code Skills 文档：<https://docs.claude.com/en/docs/claude-code/skills>
