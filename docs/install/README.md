# Claude project install bundles

Templates for standing up a new Claude project (claude.ai or Desktop) that can
do ARCH work. Nothing here is executed by any tool — these are files a human
copies into the claude.ai UI. They live in git so that every project installed
from them starts from the same known text, and so drift is visible in history.

Two bundles, on opposite sides of Constitution rule 12:

| | **A — ARCH-COLLAB** | **B — RCP DEV** |
|---|---|---|
| Role | where ARCH is authored | a project that consumes ARCH |
| Audience | James | non-technical |
| Connectors | Rovo + arch-mcp (11 tools) | site tools only |
| Session lifecycle | full start/commit/discard | none — direct dev writes |

Bundle B is deliberately thin. Giving a non-technical user the constitution and
the session lifecycle is handing them the machinery that produced the tool
rather than the tool.

## Files

| File | What it is | What you do with it |
|---|---|---|
| `ARCH-COLLAB-project-instructions.md` | Instruction text for an authoring project | Paste into **Set project instructions** |
| `ARCH-COLLAB-bootstrap-prompt.md` | Self-test for a fresh install | Paste as the **first message** in a new thread |
| `RCP-DEV-project-instructions.md` | Instruction text for a consumer project | Paste into **Set project instructions** |
| `RCP-DEV-context.md` | Background on the `rcp` dev site | Upload as a **knowledge file** |
| `NOTES-automation.md` | Why there is no installer, and the `arch_bootstrap` proposal | Read once; it is a design note, not a step |

Bundle A's knowledge files are not duplicated here — they are the existing
ARCH-COLLAB project docs. Manifest below.

---

## Install bundle A — ARCH-COLLAB

### Before you start: two fixes

Both of these propagate into every future install if not fixed first.

1. The current ARCH-COLLAB project lists **`ARCH-CONSTITUTION.md` twice**.
   Delete the duplicate.
2. **`agent-connection-layer.md` is stale** — it documents 5 tools; 11 are live,
   and its `arch_session_discard` note still says hard delete. Either update it
   or leave it out of the copy. Shipping it as-is teaches a fresh thread the
   wrong tool surface.

### Steps

1. **Create the project** on claude.ai.

2. **Set project instructions** → paste the whole of
   `ARCH-COLLAB-project-instructions.md` (skip the title and the `---` rule).

3. **Upload knowledge files.** Download these 14 from the existing ARCH-COLLAB
   project and drag them in together — multi-select works, it is one drag:

   - `ARCH-CONSTITUTION.md`
   - `PROJECT-CONTEXT.md`
   - `INDEX.md`
   - `arch.py`, `validate.py`, `agent-connection-layer.md`
   - `entity.schema.json`, `domain-model.schema.json`,
     `workflow.schema.json`, `integration.schema.json`
   - `todo.json`, `todo.domain.json`, `todo.workflow.json`, `todo.api.json`

4. **Add connectors** — Customize → Connectors:
   - Atlassian Rovo (Confluence, space AW)
   - `https://mcp.crockart.com.au/` — custom connector

5. **Verify.** New thread → paste `ARCH-COLLAB-bootstrap-prompt.md` → read the
   PASS/FAIL table before doing any real work. It checks that the knowledge
   files landed, both tool families are reachable, and whether
   `PROJECT-CONTEXT.md`'s snapshot has already gone stale against Confluence.

About three minutes.

---

## Install bundle B — RCP DEV

1. **Create the project.**
2. **Set project instructions** → paste `RCP-DEV-project-instructions.md`.
3. **Upload knowledge** → `RCP-DEV-context.md` only.
4. **Add connector** → the site-scoped MCP URL for `rcp`.

About one minute.

### Open items before this bundle is usable

- Both RCP files contain `[wife's name]` placeholders. Fill them in.
- The write-capable MCP endpoint for `rcp` **did not exist** when these were
  written — only the arch-collab equivalent. Confirm it is live first.
- The connector URL should carry a shared-secret token (agreed 2026-08-31)
  rather than being open to the public internet. Confirm before handing it over.

---

## Maintaining this folder

These are templates, not live config. Editing a file here changes nothing in
any already-installed project — those have to be re-pasted by hand. That is the
core weakness of the whole approach and the reason `NOTES-automation.md`
proposes serving the bundle over MCP instead.

When you change one, say in the commit message which projects still need
re-pasting.
