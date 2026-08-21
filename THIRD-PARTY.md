# Third-party notices

Some skills in this repo are vendored from other people's open-source work and adapted to
house conventions. [`LICENSE`](LICENSE) covers the original content here; it does **not**
cover the imported material below, which stays under its own licence and copyright.

Each imported skill also carries a one-line attribution at the bottom of its own `SKILL.md`,
because `install.sh` symlinks `skills/` into `~/.claude` and those files get read in
isolation from this one. **One footer covers its whole skill directory**, supporting files
included — `SKILL.md` is the entry point every reader arrives through, and a notice repeated
on each `*-FORMAT.md` would add noise without adding reach.

## Not listed here

`skills/adhd/` is vendored from [UditAkhourii/adhd](https://github.com/UditAkhourii/adhd)
(MIT) but is deliberately untracked — see the block in [`.gitignore`](.gitignore). It is not
published by this repo, so it needs no notice here. If it is ever promoted to tracked, it
gets a section above in the same commit.

The full Matt Pocock skill set (<https://github.com/mattpocock/skills>, MIT) is installed
in raw upstream form via `npx skills` and is deliberately untracked — see the block in
[`.gitignore`](.gitignore). It is not published by this repo, so it needs no notice here.
Customized forks of 15 of those skills were previously tracked (and listed above); they
were retired to git history on 2026-08-21 — recover from the parent of that retirement
commit. If any skill is ever promoted back to tracked, it gets a section above in the
same commit.
