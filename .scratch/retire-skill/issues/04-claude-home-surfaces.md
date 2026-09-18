# 04: The Claude home: plugins, MCP servers, hooks, memory dirs

**What to build:** The surfaces that live outside the repo appear as rows: plugins with install dating and the `duplicate` flag against loose skill copies, MCP servers from the union of user-scope config and names observed in transcripts (so claude.ai connectors get rows), hook entries with the comment-only flag, and auto-memory directories with the empty flag. Agent dispatches are counted for agent rows. The plan's third task is the starting point.

**Blocked by:** 02, 03

**Status:** ready-for-agent

- [x] Plugins come from the install record and the settings enable map; a disabled plugin has bytes 0 and flag `disabled`; an enabled plugin's bytes are the sum of its shipped skill descriptions; `installedAt` is the added date and drives `new`
- [x] An untracked skill whose name matches a skill an enabled plugin ships carries `duplicate` with `duplicate_of` naming the canonical `short:name`
- [x] MCP rows are the union of user-scope config servers and `mcp__<server>__` names seen in transcripts, with session-chosen counts and last-used; connector-only servers are labelled as such and denied connectors are flagged
- [x] Hook rows use id `hook:<event>[group][index]`; a command that is comment-only carries `disabled_comment`; prompt-type hooks are exposed for the referrer corpus
- [x] Memory directories under the projects tree carry `empty` when they hold nothing; the markdown renders them as a count, never by slug
- [x] Agent tool dispatches count as session-chosen for the named agent
- [x] Tests cover every criterion above

## Comments

