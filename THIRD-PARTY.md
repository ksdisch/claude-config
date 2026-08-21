# Third-party notices

Some skills in this repo are vendored from other people's open-source work and adapted to
house conventions. [`LICENSE`](LICENSE) covers the original content here; it does **not**
cover the imported material below, which stays under its own licence and copyright.

Each imported skill also carries a one-line attribution at the bottom of its own `SKILL.md`,
because `install.sh` symlinks `skills/` into `~/.claude` and those files get read in
isolation from this one. **One footer covers its whole skill directory**, supporting files
included — `SKILL.md` is the entry point every reader arrives through, and a notice repeated
on each `*-FORMAT.md` would add noise without adding reach.

## mattpocock/skills — MIT

Source: <https://github.com/mattpocock/skills>

| Skill | Upstream path | House edits |
|---|---|---|
| [`grilling`](skills/grilling/SKILL.md) | `skills/productivity/grilling` | trigger conditions, unattended runs |
| [`grill-me`](skills/grill-me/SKILL.md) | `skills/productivity/grill-me` | — |
| [`teach`](skills/teach/SKILL.md) | `skills/productivity/teach` | house-edited description; a workspace-location guard before the first write; `GLOSSARY.md` wired into the workspace list. The four `*-FORMAT.md` files were taken verbatim at import and have never been edited here — upstream has moved since, so don't read that as "identical to upstream today". |
| [`wayfinder`](skills/wayfinder/SKILL.md) | `skills/engineering/wayfinder` | self-contained tracker doc with a local-markdown fallback; clear-map handoff follows the vendored `to-spec`'s process and template by path (`to-spec` is typed-only, so mid-session it is read, not invoked) and routes onward; named invariants hardening the upstream-documented failure modes; unattended runs |
| [`prototype`](skills/prototype/SKILL.md) | `skills/engineering/prototype` | the verdict is never the agent's; unattended runs |
| [`research`](skills/research/SKILL.md) | `skills/engineering/research` | citation and "not established" discipline; no git operations in the subagent |
| [`domain-modeling`](skills/domain-modeling/SKILL.md) | `skills/engineering/domain-modeling` | decisions route to the repo's existing ledger rather than a second one; unattended runs |
| [`codebase-design`](skills/codebase-design/SKILL.md) | `skills/engineering/codebase-design` | NOT-for routing clause in the description; `DEEPENING.md` and `DESIGN-IT-TWICE.md` kept verbatim |
| [`wait-what`](skills/wait-what/SKILL.md) | `skills/productivity/wait-what` | — |
| [`wizard`](skills/wizard/SKILL.md) | `skills/engineering/wizard` | upstream `template.sh` not shipped — re-expressed as a named-invariant UX contract in `SKILL.md` (house rule: no copy-paste shell in skill files); unattended runs |
| [`resolving-merge-conflicts`](skills/resolving-merge-conflicts/SKILL.md) | `skills/engineering/resolving-merge-conflicts` | heading added; rebase ours/theirs orientation named in step 1; otherwise verbatim |
| [`to-spec`](skills/to-spec/SKILL.md) | `skills/engineering/to-spec` | self-contained (no `/setup-matt-pocock-skills`); spec lands in-repo at `docs/specs/` with an optional guarded tracker publish; codebase-design seam vocabulary cited; routes onward to `to-tickets` |
| [`to-tickets`](skills/to-tickets/SKILL.md) | `skills/engineering/to-tickets` | self-contained backend choice with the public-repo guard; local tickets under `docs/tickets/` (upstream: `.scratch/`); GitHub blocking edges via wayfinder tracker.md's Backend A procedures |
| [`triage`](skills/triage/SKILL.md) | `skills/engineering/triage` | self-contained label mapping recorded in `docs/triage-labels.md`; external-PR surface opt-in; public-repo write guard; out-of-scope KB at `docs/out-of-scope/` (upstream: `.out-of-scope/`) |
| [`implement`](skills/implement/SKILL.md) | `skills/engineering/implement` | house git workflow (feature branch + PR) and the adversarial-review gate replace `/code-review`; `tdd` invoked via the Skill tool |

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Not listed here

`skills/adhd/` is vendored from [UditAkhourii/adhd](https://github.com/UditAkhourii/adhd)
(MIT) but is deliberately untracked — see the block in [`.gitignore`](.gitignore). It is not
published by this repo, so it needs no notice here. If it is ever promoted to tracked, it
gets a section above in the same commit.
