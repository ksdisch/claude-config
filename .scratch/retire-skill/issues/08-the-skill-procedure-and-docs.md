# 08: The skill: procedure, bookkeeping reference, index row, playbook card

**What to build:** `/retire`, `/retire --report`, `/retire --surface <name>`, and `/retire <item>…` exist as a skill whose procedure follows the spec: preflight, inventory, proposals rendered from the script, the titled ratification table with the reply grammar, the apply pass with per-surface checklists, measurement, and shipping with a review-scope proposal. The index row and playbook card land in the same commit. Owner: the orchestrating session itself, written inline from the spec and the plan's tenth-task text amended per design §14. Do not dispatch this ticket to a fresh implementer subagent; it is judgment work and the plan's full draft makes it well-specified for the session that holds the whole context. The plan's tenth task is the starting point.

**Blocked by:** 06

**Status:** done

- [x] The skill file has a short, honest description carrying the trigger phrases from the spec, prime directives, the four invocation forms, steps from preflight through ship, a failure table, and the handoffs (relocate → /trim-context, merge-into → backlog stub, hook-convertible → backlog stub, vendored copies → ledger and PR body)
- [x] The bookkeeping reference has one checklist per surface covering backup, removal without `rm -rf`, row and card, ignore block, referrer excision with the refuse-if-unsure guard, doc-mention editing, ledger line, downstream report, re-inventory; plus pause mechanics, the CLI verbs, per-file confirmation, and the public-repo rule
- [x] The reference-doc row (Session & Context Management) and the playbook card are in the same commit; the doc-sync check passes
- [x] `/retire --report` invoked as the skill runs end to end on the live setup and produces the same report the script does
- [x] The skills directory is live through the symlink, so the description is accurate from the first commit

## Comments

- 2026-09-18 — written inline by the orchestrating session, committed as `4c7d3a8`. Amends the plan's Task 10 draft per design §14: script-computed `proposed`, `pause` as a verdict, `merge-into` removing nothing, `--surface` as a fourth form, mentions edited separately from referrers, per-file settings confirmation, CLI verbs, and every `ask` row carrying its own question. Doc-sync 102/102/64 → 103/103/65 in the same commit.
- **Observer effect caught before push.** Naming real items as illustrations made the skill a referrer to them: `plugin:swift-lsp@claude-plugins-official` — the only `cold` item in the whole 222-item surface and the only individual `retire` row — flipped to `cool`/`ask` purely because `SKILL.md` used it as an example of surface-qualified naming. All illustrative names replaced with placeholders; swift-lsp verified back at `cold`/`retire` with 0 referrers. Genuine routes (`/trim-context`, `adversarial-review`) correctly remain referrers.

