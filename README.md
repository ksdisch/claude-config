# claude-config

My personal, version-controlled **Claude Code** setup — the slash commands,
skills, subagents, global instructions, and statusline I've authored. Think
"dotfiles for Claude Code."

The canonical source lives here; `~/.claude/` symlinks to it, so editing in
either place is the same file and any new command/skill/agent I create lands in
git automatically. This is also the **upstream** that my `/claudify-repo` flow
vendors copies of into individual project repos.

## Layout

| Path | What |
|---|---|
| `commands/` | Global slash commands (`/envsetup`, `/boot_server`, `/tdd`, `/explore-plan`, …) |
| `skills/` | Global skills (`kickoff`, `mini`, `notebook-init`, …) |
| `agents/` | Global subagents (empty for now; future ones land here) |
| `CLAUDE.md` | Global instructions loaded into every session |
| `statusline-command.sh` | Custom statusline script |

## Install on a new machine

```bash
git clone git@github.com:ksdisch/claude-config.git ~/Projects/claude-config
~/Projects/claude-config/install.sh
```

`install.sh` symlinks each item into `~/.claude/`. It's idempotent and backs up
any pre-existing real files to `*.pre-claude-config.<timestamp>` before linking.

## What's intentionally NOT here

Everything machine-specific or sensitive stays out of git (see `.gitignore`):
`settings.local.json`, `.mcp.json`, `history.jsonl`, `projects/` (which holds the
auto-managed **memory** files + project history + image cache), `sessions/`,
`shell-snapshots/`, caches, the daemon, and telemetry. Secrets never belong here.

## Editing

Just edit the files in this repo (or via the `~/.claude/` symlinks — same inode),
then commit. Changes take effect immediately in Claude Code.
