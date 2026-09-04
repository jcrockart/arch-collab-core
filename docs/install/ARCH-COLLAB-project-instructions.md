# Project instructions — ARCH-COLLAB (portable copy)

Paste into "Set project instructions" on any fresh Claude project that will
do ARCH authoring work.

---

This project is where ARCH itself is authored — the constitution, the CLI
(`arch.py` / `validate.py`), the schemas, and the installable bootstrap
materials bundle. It is not an app built with ARCH.

**Confluence is the single source of truth. Chat is scratch space. Project
knowledge files are a snapshot, not live data.**

Before stating any ARCH decision, open question, or implementation status as
current fact — especially anything flagged "proposed", "pending", or
"conditional" — check the relevant Confluence page (space AW,
crockart.atlassian.net) using the page IDs in `PROJECT-CONTEXT.md`'s key page
index. Do not rely solely on the uploaded files for anything that could have
changed since they were last updated. James runs multiple concurrent threads
by design; pages change underneath you between sessions and that is normal.

Read `ARCH-CONSTITUTION.md` and `PROJECT-CONTEXT.md` at the start of every
session. `INDEX.md` maps the rest of the knowledge base.

Connectors this project expects:
- **Atlassian Rovo** — Confluence read/write (space AW, cloudId
  `a94eb8ab-1e74-43ac-ba51-6c47a89f02f5`). Use `search` with CQL-ish queries
  to discover, then `getConfluencePage` / `updateConfluencePage` with the
  numeric page ID. Always set `versionMessage` — it is the audit trail a
  governance-driven system depends on. Pass raw HTML in `body`, never
  HTML-escaped.
- **arch-mcp** (`https://mcp.crockart.com.au/project/arch-collab/`, token in
  the `x-api-key` header) — 11 tools. Eight
  `arch_session_*` (lifecycle + file access scoped to `metadata/`, writes
  session-gated) and three `arch_site_*` (file access scoped to `site/`, not
  session-gated, serves `crockart.com.au/arch-collab/`).

Boundaries that are design, not gaps:
- Git is driven through `arch.py`, never raw (Constitution rule 10).
- No MCP tool and no agent-reachable path can `git push` to any remote. Only
  James, at a terminal, does that. Do not propose working around it.
- MCP file tools write only inside `metadata/` or `site/`. They never touch
  `arch-mcp-php`'s own source.
- A change to the MCP server's own code alters the security boundary that
  governs every agent using it. Treat that as needing James's explicit
  sign-off on that specific change — a general go-ahead for a session does
  not cover it.

Land decisions on Confluence pages before a thread closes. A decision that
exists only in a transcript is invisible to every other thread and does not
exist.
