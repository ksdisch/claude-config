# Gates earn the veto; adversarial review keeps it until they do

Status: accepted (2026-08-25, grill-with-docs rounds 2–4)

Uncle Bob's pipeline (the Pocock/Martin discussion, 2026-08 — same source as the
2026-08-20 idea-mine) gives veto power only to deterministic mechanism; judgment
review rides along without blocking. We adopted the deterministic Gates but
rejected the gates-only veto: `adversarial-review` (probabilistic, propose-first)
**keeps the merge veto everywhere**, because behavioral markdown — this config's
most common diff type — is unreachable by any deterministic Gate, and because the
gauntlet pilot (2026-08-20) showed an unproven gate can cost more than it catches.

Instead, Gates start as **Preflight evidence** that argues review scope down, and
each Gate **earns the veto per-repo** (Promotion): after a report-only proving
period of ~a month, ≥1 true catch or clean passes across ≥5 merges, zero false
blocks — and the grant is always Kyle's explicit call, recorded in that repo's
CLAUDE.md, installed as a pre-push hook. The mirror kill rule (Demotion): zero
actionable signal plus ≥1 false block in the first month costs a Gate the veto —
it becomes an Instrument, never tuned into staying.

Consequences: the first two Gates (dependency-cruiser config-as-spec-file and
report-only `/crap-check`, piloting in Constellation) ship without blocking
power; the gauntlet re-pilot is parked in favor of merge-time gates; a dated
backlog entry triggers the month-one promote/demote verdict. Vocabulary — Gate,
Instrument, Preflight, Promotion, Demotion — is defined in `CONTEXT.md`.
