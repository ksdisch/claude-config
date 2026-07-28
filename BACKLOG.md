# Backlog

Ideas and work for `claude-config`. New items land under **## Open**. Full write-ups
live in [`docs/ideas/`](docs/ideas/).

## Open

### [Improvement] Two deferred nice-to-haves from PR #46's review
- **Why:** F4 — the silent-failure dimension shipped in `hunt-engine.template.js` passes the whole `ROOT` while `bug-hunt`'s own slicing rule mandates one slice per finder, so on a 6+-finder repo hunt it overlaps every other slice and must self-bound its coverage (the thing the skill says never to do silently); and because `agentType` resolves the agent definition, that dimension silently inherits `model: sonnet` regardless of session model, putting the one mandated lens on the fan-out's weakest model. F7 — `CLAUDE.md`'s newly-declared owner rung is missing two criteria both dependents attribute to it: `prompt-optimize`'s "long autonomous run where self-verification pays" on `xhigh`/`max`, and the ultracode `/config` prerequisite + silent-degradation caveat that currently live only in `handoff.md` and `ship-and-route`. An incomplete owner sends a reader who obeys "cite here, never each other" to the thinner text. Full record in PR #46's review comment.
- **Acceptance:** F4 — the example dimension shows the sliced form, SKILL.md step 1 says to fan the lens out per subsystem like the others, and the sonnet pin is disclosed so an adapter can override with `model:`. F7 — both clauses added to the owner rungs (a half-line each). Each shipped or explicitly declined with a reason.
- **Size:** S
- **Added:** 2026-07-27

### [Improvement] paper-figures scripts: close the four silent failures found in the first audit
- **Why:** The first real dispatch of `silent-failure-hunter` (over `skills/paper-figures/scripts/`, 2026-07-27) returned four genuine findings, none fixed yet: **(1)** `inject.py:60` prints `injected {len(images)}` — the *manifest* count, not the count actually replaced, so skipped placeholders (unmatched lead-in, missing file) report as success; both injectors already track the real number and discard it. **(2)** `contactsheet.py:65-78` silently falls back to inlining a full-resolution original when a per-image `sips` resample fails, with no log — the exact 26MB regression the script exists to prevent. **(3)** `checks.py:110-115` `except OSError: continue` drops which file couldn't be hashed. **(4)** `contactsheet.py:71-74` and `normalize.py:53-56, 85-89` run `sips` with no `timeout=`, so a hung child blocks forever indistinguishably from slow.
- **Acceptance:** (1) and (2) fixed — injection reports `n/total` and enumerates skips; the resample fallback logs per-file and summarizes. (3) and (4) fixed or declined with a reason. The scripts have a real test suite (`scripts/tests/`), so each fix lands with a test.
- **Size:** M
- **Added:** 2026-07-27

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
