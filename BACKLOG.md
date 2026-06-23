# Backlog

Ideas and work for `claude-config`. New items land under **## Open**. Full write-ups
live in [`docs/ideas/`](docs/ideas/).

## Open

### [Exploration] Fleet manifest + `/reconcile`: make single-source true on demand
- **Why:** Drift between canonical and vendored copies is dangerous only because it's invisible — a declared `fleet.yml` + an on-demand `/reconcile` verb makes single-source (A1) and propagation (A2) checkable by running one command. See [`docs/ideas/fleet-manifest-reconcile.md`](docs/ideas/fleet-manifest-reconcile.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (`fleet.yml` + `commands/reconcile.md` + the `claudify-repo` append-line) and judge whether the bet holds.
- **Size:** L
- **Added:** 2026-06-18

### [Exploration] The Coliseum: commands earn their keep on lived-invocation evidence
- **Why:** Lived-invocation data (which of the ~29 specs actually fire, overlap, or get hand-corrected) is a sharper curation signal than memory — a usage trace + `/retro` gives the repo its first subtraction pressure (A3 + A4). See [`docs/ideas/coliseum-commands-earn-their-keep.md`](docs/ideas/coliseum-commands-earn-their-keep.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (`/retro` reader over a hand-seeded `usage.jsonl`, then the Stop-hook) and judge whether the bet holds.
- **Size:** L
- **Added:** 2026-06-18

### [Exploration] Telemetry-Forged Commands: the config writes itself from how you actually work
- **Why:** Your transcripts already hold the richest record of what's worth codifying — `/forge` mines repeated hand-driven sequences and drafts new commands as PRs you ratify, flipping authorship from write→propose-and-approve (A3). See [`docs/ideas/telemetry-forged-commands.md`](docs/ideas/telemetry-forged-commands.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (read-only `commands/forge-scan.md` that prints your top 3 "you keep doing this by hand" clusters) and judge whether the signal exists.
- **Size:** L
- **Added:** 2026-06-18

### [Exploration] claude-config as a registry: versioned commands + a lockfile
- **Why:** Vendored copies silently decay and nobody knows how old they are — a `version:` field + a `.claude/claude.lock` turns drift into a readable number (`cc outdated`: "kickoff is 4 versions behind"), using the one primitive from npm that pays, with git as the registry (A2). See [`docs/ideas/claude-config-as-registry.md`](docs/ideas/claude-config-as-registry.md) for the full write-up.
- **Acceptance:** Prototype the credible first step (lockfile-write in `claudify-repo` PORT + seed `version: 2.0.0` on `kickoff`) and judge whether the bet holds.
- **Size:** L
- **Added:** 2026-06-18

### [Improvement] CONVENTIONS.md: the command frontmatter contract + a copy-paste stub
- **Why:** A short root `CONVENTIONS.md` states the command frontmatter contract (`description` / `argument-hint` / `allowed-tools`, their order, when each is optional) + a copy-paste stub — documentation as the validator for a prose-only, test-less repo (A3). See [`docs/ideas/conventions-md.md`](docs/ideas/conventions-md.md) for the full write-up.
- **Acceptance:** Create `CONVENTIONS.md` (contract + stub + omit-rules), link it from README, and add it to `install.sh` DENY; confirm a stub copy reproduces `smoke-test.md`'s field order and `begin`/`wrap`/`handoff` are documented as the intentional argument-less case.
- **Size:** M
- **Added:** 2026-06-23
