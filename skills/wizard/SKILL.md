---
name: wizard
description: Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself.
---

# Wizard

A **wizard** is a bash script that walks a human, step by step, through a manual procedure that's tedious to do by hand and tedious to re-explain to an AI every time. It opens each URL, says exactly what to click and copy, captures the values, writes them where they belong (`.env`, GitHub secrets), confirms at every stage, and shows how many stages are left. It might configure third-party services, run a one-off migration, or move the project from one state to another.

Upstream ships the wizard UX as a copy-paste shell template; this repo deliberately doesn't. **The UX contract below is a set of named invariants, not a script: author the wizard fresh each time, and hold every invariant.** Your job is to scope the procedure, author its stages, and write a script that satisfies the contract.

A wizard is ephemeral by default: built for one run, saved to a scratch or `scripts/` path, deleted when the job's done. Commit it only when Kyle wants a repeatable setup path that should live in the repo.

## The UX contract

Each invariant is named so it can be cited during authoring and verification.

- **`fail-fast`** — the script runs under strict shell modes (`set -euo pipefail`), so a failed command halts the wizard instead of plowing on with unset values. Decorations (color, bold) are used only when the terminal supports them. Strict mode turns an *answer* into an error if you let it: every interactive `read` is guarded so EOF can't kill the run, and any helper that returns non-zero as its answer — a y/N gate, an env lookup that finds nothing — is only ever called in a conditional context, never bare.
- **`one-stage-on-screen`** — each stage begins by clearing the terminal so only the current step is visible; clearing is a no-op when stdout isn't a terminal, so piped logs stay readable. Keep a stage to one focused task, so nothing the human needs scrolls away.
- **`progress-visible`** — an opening banner says what the wizard does and how many stages it has; every stage header shows "Stage N of TOTAL". The total is declared once and must equal the number of stages authored.
- **`open-before-ask`** — open a page in the human's browser *before* asking for any value found on it. URL opening works cross-platform, WSL included: try the platform openers in order (`wslview`, `explorer.exe`, `xdg-open`, `open`), and when none works, print the URL and tell the human to visit it manually — never fail the run over a browser.
- **`secrets-stay-hidden`** — anything secret is read with hidden input and never echoed back. Non-secret values use visible input.
- **`reruns-resume`** — before prompting for a value, look up its current entry in the env file and offer it as the default (Enter keeps it). Ctrl-C and re-running therefore resumes from where the human left off instead of restarting, and the banner says so.
- **`env-writes-upsert`** — persisting `KEY=VALUE` creates the env file if missing and *replaces* any existing `KEY` line rather than appending a duplicate. Idempotent by construction.
- **`ci-writes-degrade`** — GitHub secret/variable writes first check that `gh` exists and is authenticated; on any failure they record the skip, print the exact manual command to run later, and the wizard continues. A missing `gh` never aborts the run.
- **`confirm-irreversible`** — any irreversible action sits behind an explicit yes/no gate that defaults to **no**. Declining skips that action and continues to the closing summary; it never exits the wizard.
- **`closing-summary`** — the wizard ends with a summary frame: every env key written, every CI secret/variable set, and everything skipped that the human still has to do by hand.

## Process

### 1. Scope the procedure

Work out every manual step the human must take and every value that gets captured along the way. Read the repo first, don't ask cold:

- For setup: `.env`, `.env.example`, `.env.*`, `README`, `docker-compose*`, framework config, and `.github/workflows/*` (every `secrets.*` / `vars.*` reference is a value the wizard must produce).
- For a migration or transition: the current state, the target state, and the irreversible actions between them.

Then show Kyle the ordered list of stages and the values each produces, and confirm: he may add, drop, or reorder.

**Done when:** every stage is named in order, and for each captured value you know (a) where the human gets it, (b) where it's written (`.env`, a GitHub secret, both, or nowhere; some stages are pure actions), and (c) whether it's secret (hidden entry) or public.

### 2. Map each stage's journey

For each stage, write the precise path a human follows: which URL to open, what to do there, where a value is shown, which variable it fills: e.g. "Dashboard → Developers → API keys → Reveal test key → copy". Where you don't actually know the current UI or the exact command, say so and ask Kyle or check the docs: never invent steps that may not exist.

**Done when:** every stage traces to concrete instructions a stranger could follow.

### 3. Author the wizard

Write the script fresh at the target path, in two clearly separated sections:

1. **A small helper layer first** — one function per recurring move: announce a stage, print an instruction line, open a URL, prompt for a visible value, prompt for a secret, upsert an env entry, set a CI secret, set a CI variable, pause for the human, confirm a gate, and print the closing summary. Each helper is where its invariants from the contract live; keep the layer small and boring.
2. **The stages below** — one stage per step from your map, in dependency order, with the stage total declared to match (`progress-visible`).

Hold the bar the contract sets, per stage: open the URL before asking for its value (`open-before-ask`), hidden entry for anything secret (`secrets-stay-hidden`), persist every captured value (`env-writes-upsert`), set as a CI secret only the values CI actually needs (`ci-writes-degrade`), and gate anything irreversible (`confirm-irreversible`).

### 4. Verify and hand off

- `bash -n <script>`; run `shellcheck` if available. `chmod +x <script>`.
- Don't run it end-to-end yourself: it opens browsers and blocks on human input. Trace it statically instead: every value from step 1 is captured and lands where step 1 said, every CI secret name exactly matches a `secrets.*` reference in CI, and every invariant in the contract holds — check them off **by name**.
- Tell Kyle how to run it. If it's a repeatable setup path, commit it and link it from the README so the next person runs the script instead of asking an AI.

## Unattended runs

A wizard is scoped *with* Kyle and run *by* a human, so both halves block on one. Unattended, do only the read-only half: survey the repo, draft the ordered stage map and each stage's journey with every unverified UI path marked as an unconfirmed assumption, and stop before step 3, reporting the draft for Kyle to confirm. Never author the script against an unconfirmed stage list (step 1's gate), never invent UI paths to fill a gap (step 2's rule), and never *execute* a wizard unattended — it blocks on human input and captures live credentials.

---

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), adapted to house conventions — the upstream `template.sh` is re-expressed as the named-invariant contract above. Full notice: `THIRD-PARTY.md` in the claude-config repo.
