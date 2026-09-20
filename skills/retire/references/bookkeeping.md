# Bookkeeping checklist — per retired item

Run in order. Verify each step before starting the next. A step that cannot complete cleanly
**stops that item and is reported** — never a partial removal, never a surface left half-edited.

`$DATE` = `date +%F`. `$BK` = the dated backup folder under the claude home,
`~/.claude/backups/retired-$DATE`.

## Rules that hold on every surface

- **Never `rm -rf`.** The rm-rf hook rejects it outside `/tmp/` anyway. Tracked → `git rm`.
  Untracked → back up, then `mv`.
- **Referrer excision is surgical.** Read the line; identify every *other* item named on it;
  remove only the target fragment; re-read and assert every other name survived. If the line is a
  whole sentence about the item, delete the sentence. **If unsure, leave it and report it** — a
  shared line must never lose a neighbour by accident. Where a `merge-into` target was ruled,
  rewrite the route to the target instead of deleting it.
- **Mentions are not referrers.** A tracked doc that merely names the item gets edited with
  judgment in the same PR and listed under its own PR heading. The index doc, the playbook and the
  ledger are excluded from both — each has its own step below.
- **Downstream copies are report-only.** Append the item's `vendored_copies` repo **names** to its
  ledger line and the PR body. Never edit another repo. This repo is public: names, never paths.
- **Ledger ids are surface-qualified** (`skill:<name>`, `claude-md:<heading>`) so a skill
  and a section sharing a name never collide, and a ledger row pastes straight into targeted mode.
- **Re-inventory last.** Assert the item is absent from every surface it was on.

## Skill — tracked (`skills/<name>/`)

1. `git rm -r skills/<name>`
2. Delete its row in `docs/command-skill-reference.md` **and** its card in
   `docs/usage-playbook.md`. `python3 scripts/check-doc-sync.py` must pass before continuing.
3. Referrers, per the excision rule above.
4. Ledger line. Restore = `git show <sha>^:skills/<name>/SKILL.md`.
5. Re-inventory; assert `skill:<name>` absent.

## Skill — untracked (gitignored loose copies)

1. `mkdir -p "$BK" && tar czf "$BK/<name>.tar.gz" -C skills <name>`
2. `mv skills/<name> "$BK/<name>"`
3. Remove its block from `.gitignore`. If the comment above that block now describes nothing,
   remove the comment too. **A trailing ` # comment` on a gitignore line is part of the pattern** —
   keep comments on their own line. Remove any matching mention in `THIRD-PARTY.md`.
4. Referrers, per the excision rule.
5. Ledger line. Restore = the tarball path.
6. Re-inventory; assert absent. **For a plugin duplicate**, also verify the bare name still
   resolves in a fresh session. If it now resolves only as `plugin:<name>`, record that spelling
   in the playbook card that mentioned it and in the ledger's Why column.

## Command (`commands/<name>.md`, or `.md.disabled` when paused)

1. `git rm commands/<name>.md` (or the `.disabled` spelling).
2. Row and card, then doc-sync — as for tracked skills.
3. Referrers. For a paused command the inventory's `dangling` items **are** the routes to patch.
4. Ledger line. Restore = `git show <sha>^:commands/<name>.md`.
5. Re-inventory.

## Agent (`agents/<name>.md`)

1. `git rm agents/<name>.md`
2. Row under "Custom Subagents"; card under the playbook's agents section. Doc-sync must pass.
3. Referrers include **skills that dispatch it** by `subagent_type`. Edit them or retire the
   dispatching skill — never leave a dispatch pointing at an agent that is gone.
4. Ledger line; re-inventory.

## CLAUDE.md section

1. Show Kyle the exact span first — the heading through the line before the next same-level
   heading — so he sees what goes.
2. Delete it. (A `relocate` ruling means hand to `/trim-context` and delete nothing.)
3. Referrers: a prompt-type hook naming the section is a **settings edit** — per-file
   confirmation, backup first. Other sections cross-referencing it get the sentence excised.
4. Ledger line. Restore = `git show <sha>^:CLAUDE.md`, with the old line span in Why.
5. Re-inventory; assert the id is absent **and** the claude-md Totals row shrank.

## Operating-constraints paragraph

Same as a CLAUDE.md section — the unit is the bold-led paragraph, since that file has no headings.

## Output style (`output-styles/<name>.md`)

`git rm`; ledger line; re-inventory. No row or card exists for output styles.

## Plugin

1. Per-file confirmation, backup first.
2. **Retire → `claude plugin uninstall <key>`. Pause → `claude plugin disable <key>`.** Use the
   CLI verbs; do not hand-edit the install record or the enable map.
3. Ledger line (retire only). Restore = `claude plugin install <key>`.
4. Re-inventory; a retired plugin is absent, a paused one carries `disabled` with bytes 0.

## MCP server

1. Per-file confirmation, backup first.
2. `claude mcp remove <name>` for a configured server. For a claude.ai connector, add it to the
   deny list in `settings.json` instead — there is no local config to remove.
3. Ledger line. **Restore is the backup file path, never the config block** — it may hold secrets,
   and this repo is public.
4. Re-inventory.

## Hook entry

1. Per-file confirmation, backup first.
2. Delete the entry from its `hooks` array, and the group or event if nothing remains.
3. Ledger line. Restore = the backup file path; **never the command text** (public repo).
4. Re-inventory.

## Auto-memory directory

- **Empty** → remove it. No per-item stop; there is nothing to lose and these are mechanical.
- **Non-empty** → per-file confirmation; `tar czf "$BK/memory-<slug>.tar.gz"` then move the files
  out. Ledger line with the tarball as Restore.
- The report renders memory as a **count with a generic label**, never by slug.

## Pause mechanics (any surface that supports it)

Commands and skills rename to `.disabled`; plugins use the CLI disable verb. **No ledger line** —
a pause is not a retirement. The index row and playbook card **stay**, prefixed `(paused <date>)`
with a bold **Paused** note and the restore instruction, so the docs say what the ruling meant.
The pause date is the last commit touching the file, or its mtime when untracked. There is no
pause for CLAUDE.md sections, MCP servers, or hooks.
