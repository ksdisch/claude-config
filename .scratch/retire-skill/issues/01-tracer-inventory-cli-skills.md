# 01: Tracer: the inventory CLI over a fixture, tracked skills only

**What to build:** Running the inventory script against a fixture claude home and config repo produces one record per tracked skill and proves the whole path: description bytes (folded block scalars joined), typed counts for the window and all-time plus last-used from the prompt history, an added date and the `new` temperature, a minimal `proposed` (cold → retire; hot, warm, new → omitted), full JSON and redacted markdown, the `--surface` filter, and the three exit codes. A stdlib `unittest` suite drives it over a generated fixture. Run against the live setup it answers "which skills have I typed in the last 90 days". The code-level plan's first, second, fourth and seventh tasks are the starting point; the spec wins where they differ.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `python3 -m unittest discover` from the script's tests directory is green; each test builds a resolved temporary fixture and asserts on JSON, markdown, or exit code only
- [ ] A fixture with three skills, one using a `>-` description, yields three records whose `bytes_always_loaded` equals the joined description length
- [ ] Typed 6 times in the window → `hot`; 2 → `warm`; 0 in window but typed once ever → `cool`; never typed, no referrers → `cold`; first commit inside the window → `new` regardless of counts
- [ ] Typed counts match only history rows whose display begins with the slash form followed by a non-name character (`/handoff` never counts for `/hand`)
- [ ] `--json` writes full records, `--md` writes the markdown table, neither writes markdown to stdout; `--since`, `--claude-home`, `--config-repo`, `--projects-root`, `--claude-json`, `--triggers`, `--no-cache`, `--surface` all exist
- [ ] `--surface skill` restricts output; an unknown surface exits non-zero and lists the valid names
- [ ] Missing or empty history exits 2 naming the source; a skills directory with no skill files exits 3; the happy path exits 0; a zero is only ever reported after the source was read
- [ ] Window default, temperature thresholds, and the `auto_only` threshold are named constants in one place
- [ ] Config repo defaults to the resolved target of the skills symlink under the claude home
- [ ] Run on the live setup, the markdown lists every tracked skill and the `/handoff` typed count agrees with the design's evidence snapshot (79 all-time)

## Comments

