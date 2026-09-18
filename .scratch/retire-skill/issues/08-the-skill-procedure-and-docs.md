# 08: The skill: procedure, bookkeeping reference, index row, playbook card

**What to build:** `/retire`, `/retire --report`, `/retire --surface <name>`, and `/retire <item>…` exist as a skill whose procedure follows the spec: preflight, inventory, proposals rendered from the script, the titled ratification table with the reply grammar, the apply pass with per-surface checklists, measurement, and shipping with a review-scope proposal. The index row and playbook card land in the same commit. Owner: the orchestrating session itself, written inline from the spec and the plan's tenth-task text amended per design §14. Do not dispatch this ticket to a fresh implementer subagent; it is judgment work and the plan's full draft makes it well-specified for the session that holds the whole context. The plan's tenth task is the starting point.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] The skill file has a short, honest description carrying the trigger phrases from the spec, prime directives, the four invocation forms, steps from preflight through ship, a failure table, and the handoffs (relocate → /trim-context, merge-into → backlog stub, hook-convertible → backlog stub, vendored copies → ledger and PR body)
- [ ] The bookkeeping reference has one checklist per surface covering backup, removal without `rm -rf`, row and card, ignore block, referrer excision with the refuse-if-unsure guard, doc-mention editing, ledger line, downstream report, re-inventory; plus pause mechanics, the CLI verbs, per-file confirmation, and the public-repo rule
- [ ] The reference-doc row (Session & Context Management) and the playbook card are in the same commit; the doc-sync check passes
- [ ] `/retire --report` invoked as the skill runs end to end on the live setup and produces the same report the script does
- [ ] The skills directory is live through the symlink, so the description is accurate from the first commit

## Comments

