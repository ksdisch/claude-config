# claude-config as a registry: versioned commands + a lockfile, so drift becomes a number

**Status:** Idea — not committed. Added by `/brainstorm` (`moonshot` mode) on 2026-06-18.
**Lens:** domain-transplant · **Fit:** identity-shift · **Boldness:** audacious · **(WILDCARD — kept deliberately as the boldest borderline survivor)**

## Premise

claude-config's compounding-leverage thesis has a leak: leverage only compounds where the
codified workflow is actually **present and current**. The symlink keeps Kyle's local machine
perfectly current (A1), but every vendored repo is a frozen photograph that silently decays — so
the cloud/collaborator audience runs an ever-older claude-config and nobody knows how old. A
registry doesn't add features; it adds a **truth channel**: every consuming repo can answer "which
version am I running, and how far behind is it?" The lockfile is the smallest object that gives
drift a name.

## The bet

The one thing that must be true: **drift is invisible because it's unnamed**, and a lockfile makes
it a readable number ("kickoff is 4 versions behind") that turns a stale copy from a thing you
discover by accident into a thing `cc outdated` reports. (Targets **A2** — vendoring silently
drifts/goes stale/never merges — the 7 stale vendor branches.)

Veteran reaction: *"You're standing up npm to manage 29 markdown files for an audience of one —
where's the registry server, the resolver, the conflict semantics? This is a lockfile cosplaying as
infrastructure."* The answer: it's **not** npm; it's the **one** primitive from npm that actually
pays — a pinned record that makes drift legible — and **git already IS the registry**, so there is
no server to stand up.

**Why now:** A2 just drew blood in the open — 7 repos sit on stale, unmerged vendor branches right
now, found only by manually looking. Today's drift is at the exact size where it's still
embarrassing-but-recoverable rather than silent rot. And the substrate is ready: frontmatter is
uniform across all 18 commands + 11 skills, `/claudify-repo` is stable ("copy faithfully" is its
whole PORT contract), and there are **zero git tags** — so the publish boundary is greenfield.

## Credible first step

In `commands/claudify-repo.md` PORT step 2: keep the faithful copy, but additionally write/append one
line per vendored item to `.claude/claude.lock` — `name version source-sha date` (version read from a
new `version:` frontmatter key; source-sha from `git rev-parse HEAD` in this repo at vendor time). Seed
it by adding `version: 2.0.0` to `skills/kickoff/SKILL.md` frontmatter (the field is non-breaking —
Claude ignores unknown keys). That single line turns the next vendor from a silent overwrite into a
diffable, drift-detectable record, and `cc outdated` is then just: compare lock line vs. current
`version:` here. No resolver, no server, no install verb yet — but the record that makes them possible
now exists.

## Decisions / open questions

- **Version source of truth:** per-item `version:` frontmatter (independent semver per command/skill) vs.
  one repo-wide version (git tag of the whole repo)? Per-item is the real package model but is 29 versions
  to hand-bump; repo-wide loses "kickoff is 4 behind" granularity. Lean per-item, lazily — bump only when
  you'd want a consumer to notice.
- **Who writes `version:`** — manual on edit (carries human intent: breaking vs. tweak) or derived
  (content hash / last-touch commit, can't go stale but can't signal "breaking")?
- **`cc upgrade` semantics:** overwrite, or three-way merge against local edits? The whole point over
  today's copy is **not** clobbering local tweaks — but that pulls in real merge semantics. v1 could just
  refuse to upgrade a locally-modified file and report it.
- **Single vs multi-source:** is the registry only claude-config, or could a repo declare deps on multiple
  sources? Single-upstream keeps it a lockfile; multi-source is when it becomes a real package manager.
  Stay single-upstream until proven otherwise.
- **Surface for `cc outdated`/`cc upgrade`:** a markdown command interpreted at runtime (in-character with
  prose-spec nature) or a real shell script (more honest infra)? Probably both: prose command that shells out.

## Dependencies

- Uniform frontmatter across commands (`description:`/`argument-hint:`) and skills (`name:`/`description:`) —
  confirmed present; `version:` slots in as one more non-breaking key.
- `/claudify-repo` PORT mode as the single chokepoint where vendoring happens — the only place a lockfile
  write must be added.
- Git as the registry substrate: tags-as-published-versions and `git rev-parse HEAD` as source-SHA. Zero
  tags exist today, so this is a new convention to start.
- A consumer-side reader (Claude at runtime, or a small script) that can diff `.claude/claude.lock` against
  the current `version:` here — needs claude-config reachable at check time.

## Explicitly out of scope (revisit later)

- A registry **server** or hosted index — git IS the registry; never stand up a service for an audience of
  one-plus-collaborators.
- Semver **range** resolution (`^2`, `~2.1`) and a real resolver — v1 pins exact versions only; ranges are
  the over-build that earns the veteran's scorn.
- Publishing outside this repo (npm/marketplace/strangers) — the audience is Kyle + his cloud sessions +
  named collaborators.
- Auto-upgrade / auto-merge of vendored files — upgrade must stay deliberate and reviewable; the failure mode
  being fixed is silent change, so silent change is forbidden as the cure.
- Touching the symlink/local path (A1) — local is already perfectly current; the registry is strictly about
  the vendored audience.
- CI/validation that a command "works" (A3) — versioning is about which bytes are deployed, not whether the
  prose is correct.

## Identity/positioning note

Today claude-config is "dotfiles I symlink and copy from" — a passive folder. The registry move gives it a
**publish boundary** it has never had: a notion of a released version distinct from the working file,
consuming repos that are declared **dependents** rather than anonymous recipients of a copy, and a protocol
(lock + version) the repo now owns. The README already calls this repo the "upstream" — the shift is making
"upstream" load-bearing: upstream/downstream with a version contract between them, instead of upstream-as-folklore.
The sharpening that keeps it bold: do **not** retreat to "it's just a version field." The version field is the
wedge; the identity is that claude-config gains the right to say *"you are running an old me, and here is exactly
how old."* If that sentence stops being true, the boldness was sanded off.
