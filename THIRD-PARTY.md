# Third-party notices

Some skills in this repo are vendored from other people's open-source work and adapted to
house conventions. [`LICENSE`](LICENSE) covers the original content here; it does **not**
cover the imported material below, which stays under its own licence and copyright.

Each imported skill also carries a one-line attribution at the bottom of its own `SKILL.md`,
because `install.sh` symlinks `skills/` into `~/.claude` and those files get read in
isolation from this one. **One footer covers its whole skill directory**, supporting files
included — `SKILL.md` is the entry point every reader arrives through, and a notice repeated
on each `*-FORMAT.md` would add noise without adding reach.

## cursor/plugins (pstack) — MIT

Source: <https://github.com/cursor/plugins>, imported at commit `101b274`.

| Skill | Upstream path | House edits |
|---|---|---|
| [`blast-radius`](skills/blast-radius/SKILL.md) | `harness/pstack/claude-code/skills/blast-radius` | the `how`/`why` companion line and `why` step-2 reference replaced with inline `git`/`gh` commands; the multi-model `arena` step replaced with `/code-review xhigh`; the `unslop` pass dropped; a line tying the safety fact to the review-gate proposal |
| [`correct`](skills/correct/SKILL.md) | `harness/pstack/claude-code/skills/correct` | "agent instruction files" mapped to `CLAUDE.md`/`AGENTS.md`; fixes land on a branch + PR; the rule table goes in the repo's `CLAUDE.md` and that PR gets the behavioral-file review |

```
MIT License

Copyright (c) 2026 Lauren Tan

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

The Matt Pocock skill set (<https://github.com/mattpocock/skills>, MIT) reaches sessions
through the `mattpocock-skills@mattpocock` plugin. The raw `npx skills` copies that used to sit
untracked in `skills/` were retired on 2026-09-21, and the last one, `implement-spec`, on
2026-10-14 once the plugin began registering it — see [`docs/retired.md`](docs/retired.md).
None is published by this repo, so no notice is needed here. Customized forks of 15 of those skills were previously
tracked (and listed above); they were retired to git history on 2026-08-21 — recover from the
parent of that retirement commit. If any skill is ever promoted back to tracked, it gets a
section above in the same commit.
