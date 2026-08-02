---
name: research-paper
description: End-of-project write-up for Kyle's reproduce-and-measure research projects (the forge-gap / decay-pin / ghost-patch lineage). From a COMPLETED repo's recorded results ONLY — no new measurements, no fabricated numbers, no fabricated citations — produce two Markdown deliverables and PR them for review (never merged): a professional research paper (abstract + full academic sections) and a presenter pack that makes Kyle fluent enough to defend the paper claim-by-claim. Use whenever Kyle types /research-paper, says "write the paper", "write up this project", "generate the research paper", "paper + presenter pack", "turn this repo into a paper", or closes a research project and wants the formal write-up — even if he doesn't name the skill. NOT for reading someone else's paper (paper-companion) and NOT for choosing the next project (seed-hunt). Built to run unattended (async, max effort); works interactively too.
---

# Research Paper — write up a finished project from its recorded results

You are running the write-up step in Kyle's research-reproduction pipeline: project
declared COMPLETE → **/research-paper** (this skill) → `/seed-hunt` (pick the next
paper). A project in this lineage re-implements a narrow primitive from a published
paper at hobby scale and *measures* the paper's claim honestly under pre-committed
statistical gates. The write-up must preserve exactly that honesty: it reports what
was measured — including the nulls — and nothing else.

**Deliverables:** (1) a research paper — with figures where the recorded data earns
them, (2) a presenter pack, (3) a review-only PR, (4) a final report with provenance
and flagged gaps. You take **no new measurements** and you **merge nothing**.

Designed for an unattended max-effort run (cloud / autonomous session) — the
unattended rules in the global operating constraints apply. The only hard stop is in
Preflight; everything after it runs end-to-end without asking.

## Parse `$ARGUMENTS`

- **A path** → treat it as the project repo root. Default: the current repo.
- **Anything else** → operator notes: fold them into the mission (an explicit
  length budget, emphasis, a section to add or skip, a specific audience for the
  pack). Notes tune the mission; they never override the Hard constraints below.

## Preflight

Run from the finished project's repo root. If the cwd is clearly not a project repo
(e.g. `claude-config` itself, or a repo with no recorded results anywhere) and no
path was given, stop and say so — in an unattended run, report the ambiguity as the
outcome rather than papering the wrong repo.

This skill assumes the project is **closed**. If the tree is dirty or the roadmap
shows a milestone mid-flight, surface that and stop — a paper over a moving target
misstates the record. (`/seed-hunt` Phase 0 owns the full closure audit; here one
mechanical look is enough.)

## Hard constraints (non-negotiable, in force through every phase)

1. **NO NEW MEASUREMENTS.** Do not run experiments, call any model or API, or execute
   any script the target repo already ships — measurement, ablation, reanalysis and
   figure-rendering scripts alike — and never overwrite an artifact the repo *recorded*
   (a result file, a figure image, a data JSON). The only files you write are this
   skill's own deliverables in the paper directory, which a re-run may replace. Use only
   numbers already recorded in the repo. Drawing a *new* plot of those recorded
   numbers, in a new file this skill writes, is not a measurement — see **Figures**
   below for what such a plot may compute and which executions are permitted.
2. **NO FABRICATED NUMBERS.** Every statistic — each delta, confidence interval, N,
   percentage, dollar figure — is lifted verbatim from a real file. Numbers you
   *derive* (even trivial arithmetic over recorded values) don't qualify: cite the
   recorded form or drop the claim. If a number you want isn't recorded anywhere,
   say so plainly in the text and flag it in the final report. Never estimate.
   **The one carve-out** is the narrow, scripted, disclosed derivation defined under
   **Figures** below — it exists because plotting inherently computes something, and
   it is bounded so that a reviewer can check every plotted value against a file.
   Nothing outside that carve-out is exempt.
3. **NO FABRICATED CITATIONS.** Cite exactly what the repo records. If only an arXiv
   ID + title is on record (no author list), cite that and note it. If the repo
   names no source for a primitive, describe it as established/common practice and
   frame the work as reproducing a known pattern. Never invent titles, authors, or
   venues.
4. **PRESERVE THE HONESTY FRAMING (load-bearing).** The lineage's stance:
   "reproduced and measured a published primitive — not invented it"; gaps
   manufactured by injecting faults are disclosed AS manufactured; a null result (a
   mechanism that did nothing) is reported as a result, not hidden. Do not overclaim
   novelty, do not bury nulls, do not round a CI-overlapping result up into a "win."
5. **REPORT STATS HONESTLY.** Carry through the repo's recorded method — lineage
   standard: Wilson intervals per arm, a Newcombe interval on the between-arm
   difference, the N≥20 discipline, the noise-floor constraint; defer to whatever
   this repo actually recorded. A delta whose CI includes zero is a null/small
   effect and is stated as such; anything the repo pre-declared underpowered is
   stated as no-claim.
6. **FIT LENGTH TO CONTENT — no padding, no omission.** No default target word
   count: the recorded material decides how long the paper is. Don't make it longer
   than the record requires — no padding, no restatement, no section the material
   doesn't earn. Don't make it shorter by leaving recorded content out — measured
   results, nulls, required disclosures, owned deviations, and the constraint-4
   honesty framing are never dropped to hit a size. An operator note may set an
   explicit length budget: it tightens the no-padding half — trim discretionary
   prose (motivating context, connective transitions, restatement) to meet it,
   never a section's mandated content: the recorded measurement discipline, the
   nulls' interpretation, and the un-validatable residual are not discretionary.
   A budget never licenses omission; one that can't be met without dropping
   recorded content is kept unmet, with the overrun flagged in the final report.
   Judge length on the prose (`wc -w` over-counts table tokens). The same rule
   governs the presenter pack.

## Figures — encouraged when they earn their place

Figures are **welcome, and expected wherever the recorded data plots well**: a dose
curve, a 2-D prime × probe grid, per-arm rates with their intervals, a cliff. Some
results are far more legible as a picture than as a row of numbers, and a repo whose
own brief calls something "the killer figure" should not ship tables-only.

This is encouragement, not a mandate. **Tables-only stays a legitimate outcome — it
just stops being the default** for a repo full of plottable recorded data. Judge each
candidate on one question: *does it show a shape a table hides* — a curve, a cliff, a
grid, an interval overlap? If no, use the table. State what you decided, and why, in
the final report.

**Chart conventions are the global `dataviz` skill's job — invoke it before writing
the first line of plotting code** (palette, axes, legends, light/dark). Do not
restate or re-derive those rules here.

### What a figure may compute — the constraint-2 carve-out

A figure plots the record. Exactly two things are permitted:

- values lifted verbatim from a committed result file — counts, rates, recorded
  confidence intervals, and the axis values the repo itself used (α, tier, layer,
  band, concept);
- one rate from a recorded numerator over a recorded denominator (`hits / n`) — the
  single arithmetic step allowed, because both operands are on record and the result
  is checkable against the paper's own tables.

Forbidden: smoothing, interpolation, fitted or trend lines, error bars you compute
yourself (plot the **recorded** interval or none at all), pooling across cells the
repo never pooled, re-binning, axis values read off an existing image, and any value
the repo does not hold.

If the paper wants a statistic that exists only in prose (a milestone brief,
`DECISIONS.md`), do **not** do that arithmetic inline or inside the plotting script.
Take the lineage route instead — a sibling `docs/paper/derived_contrasts.py` that
recomputes it **through the repo's own stats module** from counts parsed out of
committed result files, **asserts** it equals the prose-recorded value at the
recorded precision, writes one result JSON for the paper to cite, and writes nothing
at all if any assertion fails. A mismatch is a finding to report, never something to
paper over. A statistic recorded nowhere at all stays out of the paper and goes into
the final report as a flagged gap.

### How the derivation is disclosed

All four, non-negotiable:

1. **A committed script, never hand-placed pixels** — `docs/paper/figures.py`,
   deterministic and headless (matplotlib `Agg`), reading only committed result
   files: same data in, same figures out on any re-run.
2. **Its docstring states the contract** — the run command, which files it reads,
   one line per figure describing what that figure shows, and an explicit sentence
   on what the script does and does not compute.
3. **It prints every plotted number**, so a reviewer can check the figures against
   the paper's tables without opening a PNG.
4. **The paper points back** — the Reproducibility section names the script and its
   run command; every caption gives the n and says the intervals shown are the
   recorded ones.

Add no dependency to the project's manifest; inject the plotting library for that run
only (lineage form: `uv run --with matplotlib docs/paper/figures.py`).

**The complete set of execution this skill permits** — nothing outside it: the scripts
it writes itself (`figures.py`, plus `derived_contrasts.py` where a prose-only
statistic needs it), and read-only parsing of committed files (as Phase 5 requires for
JSON sources). None of that touches a model, a lens, a measurement or ablation script,
or **any script the target repo already ships** — constraint 1 governs those, and
re-running one to refresh a committed image is exactly what it forbids.

## Phase 1 — Comprehend (read before writing a word)

**First, map this repo's actual ledger of record.** Layouts differ across the
lineage — never assume this repo matches the last one (past mission templates have
named a sibling repo's artifacts):

- Candidates: kickoff/milestone briefs; `docs/` writeups (ROADMAP / DECISIONS /
  LEARNING / session logs); committed result files (`docs/figures/*-data.json`,
  `data/*_results.json`, or equivalents); committed outputs of stats/ablation
  scripts.
- Prefer **nearest-to-raw**: committed result files over prose; briefs over
  `CLAUDE.md` (a guide, not the ledger). Where two sources disagree, trust the one
  nearest the raw result and note the discrepancy.
- Distrust stale directories — anything holding overwritten or mixed-session
  trajectories (historically `runs/`) is not a number source.
- You will state the chosen sources of truth in the final report.

Then read the project modules (agent, scenario, oracle, faults, stats, ablation —
or this repo's equivalents), the tests, the result files, and any figure images.
Build an accurate model of: the thesis, the task, each mechanism/arm, each
experiment — including which came back null — and the exact measured numbers.

## Phase 2 — Claims ledger (internal)

Before drafting, list every load-bearing factual claim the paper will make, and
beside each the exact number and the source file it comes from. This ledger is what
Phase 5 verifies against and what distills into the pack's provenance table.

## Phase 3 — The paper → `docs/paper/<slug>-paper.md`

Create `docs/paper/` (no `docs/`? use `paper/` at repo root). `<slug>` = repo
directory name. Empirical-methods structure, adapted to the material:

- **Title + Abstract** (150–250 words: problem, method, headline measured results
  with numbers, contribution)
- **Introduction** — the reliability-gap problem and the honest contribution
  ("reproduce and measure a published primitive; report the narrow, measured delta")
- **Background & Method** — the target paper's claim; the reproduced primitive; the
  arms/mechanisms; the measurement discipline as recorded (interval method, N
  discipline, noise floor, pre-committed gates)
- **Experimental Setup** — models tested, the task, each testbed as the repo defines
  them (clean / injected-fault / natural-gap / …); manufactured gaps labeled
  manufactured here and again in Results
- **Results** — every measured delta with its CI, INCLUDING the nulls, plus a
  results table. **Build the figures the data earns** (see **Figures** above): decide
  the figure list from what the recorded results actually contain, render it with the
  committed script, and embed each one with a correct relative path and a caption
  stating what it shows, its n, and that the intervals are the recorded ones. Embed
  figures the repo already has the same way, with captions matching what those images
  actually show. Tables carry results whose shape a plot wouldn't clarify; a paper
  with nothing worth plotting is tables-only, says so in its preamble, and gives the
  reason in the final report.
- **Discussion** — the thesis as measured (e.g. matched-guardrail: each mechanism
  against the gap it targets), what the nulls mean, the un-validatable residual
- **Threats to validity / Limitations**
- **Reproducibility** — how a reader would re-run it; recorded costs if any
- **References** — honest ones only (constraint 3)

## Phase 4 — The presenter pack → `docs/paper/<slug>-presenter-pack.md`

Goal: Kyle can defend the paper claim-by-claim in front of a mentor.

- **60-second story** — the whole project in one spoken paragraph
- **Results at a glance** — the headline table (per-experiment verdicts)
- **Provenance table** — claim → number → source file, so any figure can be traced
  live
- **Anticipated Q&A** with crisp answers — at minimum: Why manufacture the gap? Why
  is a null a result? Why Wilson intervals? What is the un-validatable residual?
  Why these models? What would you do next / what are the roads not taken?
- **Vocabulary crib** — every jargon term in the paper, one plain-English line each

## Phase 5 — Verify (refute your own draft)

Walk the claims ledger against both finished files. Mechanically where possible:
every load-bearing number must grep or parse out of its named source — and since
pretty-printing defeats string-matching, **parse JSON sources rather than grepping
them** before calling a number missing. Hunt these specific failure modes (each has
been caught in a real run of this mission):

- **Derived-not-lifted numbers** — arithmetic you did that no file records → remove
  or replace with the recorded form
- **Imputed denominators** — a fraction whose denominator you inferred → cite the
  recorded form
- a CI-straddling delta stated as a win → restate as null
- a manufactured gap missing its "manufactured" label; a null missing from Results
- an invented or embellished citation
- **A plotted value that isn't in its source file** — check the script's printed
  numbers against the paper's tables and against the parsed result files
- **A figure computing past the carve-out** — a smoothed or fitted line, an error bar
  the script computed itself, a pooling the repo never performed
- **A caption that overstates** — wrong n, wrong arm, a missing "manufactured" label,
  or an interval described as anything other than what was recorded

Fix everything that fails and re-verify. Do not claim done until this passes.

## Phase 6 — Deliver

- Create a `docs/paper` feature branch (suffix it if one already exists), commit both
  Markdown files with a descriptive message, push, open a PR. **Commit the figure
  assets in the same PR** — `figures.py`, any `derived_contrasts.py` and the result
  JSON it wrote, and the rendered PNGs — so the paper and the images that back it are
  reviewed together. Confirm the PNGs aren't caught by a `.gitignore` rule before
  claiming they landed.
- **Do NOT merge and do NOT push to `main`.** This PR is for Kyle's review — an
  explicit gate that overrides the global merge-autonomously workflow. Leave the
  repo on its default branch with a clean tree.
- **Final report:** both file paths; the PR link; the headline results exactly as
  written in the paper; the sources of truth you used; every flagged gap (numbers
  that weren't recorded, adaptations you made because this repo's layout differed
  from the mission's examples).
- **Close the report by routing the paper onward**, in these terms and no stronger —
  the hop is Kyle's to trigger, and this skill does not perform it:

  > **Portfolio notebook:** this PR is review-only and is not merged, so nothing has
  > been added anywhere. Once you merge it, the paper becomes eligible for the
  > research-portfolio notebook — run `/portfolio-notebook-sync --add-paper <slug>`.
  > While it sits on a branch, that command will correctly refuse it.

  Do not claim the paper "will be added automatically" or that a sync has been
  scheduled. Neither is true: `--add-paper` reads the **default branch** and surfaces
  what it would add for confirmation before touching the notebook. Overstating this
  is the same failure mode the paper's own honesty framing exists to prevent.

## Definition of done

Two Markdown files exist under `docs/paper/` (or `paper/`); every statistic in them
traces to a real repo file and survived the Phase 5 mechanical check; the honesty
framing, all nulls, and honest citations are intact; the length fits the content —
nothing padded, no recorded content dropped for size, judged on the prose; a
review-only PR is open; and the final report gives paths + PR link + headline
results + sources of truth + flagged gaps.

On figures, every figure the paper carries falls into one of two cases, and the final
report states which: **rendered here** — produced by the committed script from recorded
values, computing nothing past the carve-out, disclosed all four ways, with a caption
matching what it shows; or **repo-supplied** — an image the repo already had, embedded
with its caption verified against what that image actually shows (no script is owed for
one of these). A paper carrying neither is **tables-only**, declared so in its preamble,
with the reason in the final report.
