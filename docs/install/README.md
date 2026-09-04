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

## How a connector is addressed

Read this once before installing anything. It is the part that has changed
most, and the part that is easiest to get subtly wrong.

Every connector needs **two** things: a **URL**, which identifies *which space*,
and a **token**, sent as a header, which is *the entire authorisation*. The URL
is not a secret. The token is the whole of the secret.

```
URL      https://mcp.crockart.com.au/project/rcp-dev/
Header   x-api-key: <the rcp-dev token>
Auth     None          <- the dialog's own auth setting; the header does the work
```

Two URL shapes:

| Shape | Meaning |
|---|---|
| `/project/<name>/` | A **dedicated** space — one profile, one root, one owner. |
| `/group/<name>/<sub>/` | A **shared** space. The token authorises the *group*; the last segment picks a sub-project inside it, e.g. `/group/family/calendar/`. |

The `<name>` must match the token's profile label exactly, including case. If it
does not, the server returns 404 — deliberately, so that a connector pointed at
the wrong space with a valid token fails loudly instead of quietly succeeding
against someone else's tree.

**Three things about claude.ai connectors that will otherwise cost you an hour
each:**

1. **They are account-level, not project-level.** Adding one makes it available
   in every project on the account; the per-project toggle is a convenience
   filter, not a boundary. What actually keeps a project inside its own tree is
   the token's scope profile, enforced server-side.
2. **They are deduplicated by URL across the whole organisation.** A second
   connector on a URL already registered is refused as a duplicate. This is the
   reason each space needs its own URL rather than one shared endpoint — that
   was the original design and it does not work here.
3. **Custom header names need Anthropic approval.** The dialog offers a fixed
   list. `x-api-key` is on it; a bespoke name is not, and shows an error. That
   is why the header is called what it is.

---

## Install bundle A — ARCH-COLLAB

### Before you start: two fixes

Both of these propagate into every future install if not fixed first.

1. The current ARCH-COLLAB project holds **two different documents both named
   `ARCH-CONSTITUTION.md`** — not a duplicate, a superseded draft that was
   uploaded alongside its replacement rather than over it. The older one
   (~6k, 2026-08-25, first line `# ARCH Constitution (Legacy Edition)`)
   contradicts the current one: it instructs readers to carry the "Legacy
   Edition" subtitle forward, describes discard as a hard delete with no
   recovery, omits rule 12, and omits rule 5's caveat that a `COMMITTED`
   message does not prove metadata persisted. Retrieval can return either.
   Delete the older one — and check by first line or size, not position in
   the list.
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

4. **Add connectors** — Customize → Connectors → Add ▾ → Add custom connector:

   - Atlassian Rovo (Confluence, space AW)
   - **ARCH (arch-collab)**
     - URL `https://mcp.crockart.com.au/project/arch-collab/`
     - Authentication **None**
     - Request header `x-api-key` = the `arch-collab` token

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
4. **Add connector** → **ARCH (rcp-dev)**
   - URL `https://mcp.crockart.com.au/project/rcp-dev/`
   - Authentication **None**
   - Request header `x-api-key` = the `rcp-dev` token

About one minute.

**Confirm it before handing it over:** a new thread should see exactly **3**
tools — `arch_site_list_files`, `arch_site_read_file`, `arch_site_write_file` —
and no `arch_session_*`. If more than three appear, stop and check which token
went into the header.

---

## Provisioning a new space

Three steps, all on the server, all by a human. Tokens are never pasted into a
chat, a repo, or Confluence.

1. **Mint a token and add the profile.**

   ```
   cd ~/arch-mcp-php
   python3 bin/mint-tokens.py --url <name>
   python3 bin/check-tokens.py          # catches duplicate JSON keys
   ```

   `check-tokens.py` is not optional politeness. Duplicate keys in
   `tokens.json` collapse silently — `json.loads` keeps the last and raises
   nothing — and this has already hidden a live profile once.

2. **Give the profile a root and lanes** in
   `~/arch-mcp-secrets/tokens.json`. The root must already exist; a profile
   pointing at a missing directory is refused rather than created, so a typo
   fails instead of minting an empty tree.

   ```json
   {
     "<token>": {
       "label": "rcp-dev",
       "kind": "project",
       "root": "/home/crockart/public_html/rcp",
       "lanes": { "site": "" },
       "session_tools": false,
       "write_extensions": ["html", "css", "js", "png", "svg", "txt"]
     }
   }
   ```

   `write_extensions` matters wherever the root is served by a webserver:
   without it, a write of `shell.php` is remote code execution. Omit it only
   for a root that PHP will never execute.

3. **Register the connector** at `/project/<label>/` with the token in
   `x-api-key`, then confirm the tool count.

### Group spaces

A group is one token shared by several people, with a sub-project per URL:

```json
{
  "<token>": {
    "label": "family",
    "kind": "group",
    "seed": true,
    "root": "/home/crockart/groups/family",
    "lanes": { "site": "" },
    "session_tools": false
  }
}
```

With `"seed": true`, naming a sub-project that does not exist **creates** it —
`/group/family/calendar/` works with no provisioning step. That is the point of
a group, and it is also the trap: `/group/family/calender` seeds an empty space
rather than failing, so a typo looks like a working connector with nothing in
it. Set `"seed": false` once a group's sub-projects are established.

> **Sub-projects are not isolated from each other.** The group key is the
> boundary. Anyone who can reach `/group/family/calendar/` can reach
> `/group/family/anything-else/` by editing the URL. Give a group token only to
> people trusted with the entire group — a group is one tenant, not several.

---

## When something returns 404

The server answers 404 for every refusal and tells the caller nothing more, on
purpose: an unauthenticated caller should not be able to tell "wrong token"
from "nothing here". The reason is on the server, in the log line's `via`
field.

| `via` | What went wrong |
|---|---|
| `header` | Token was sent but is malformed or unknown |
| `none` | No token reached the server at all — check the header name |
| `header/kind-mismatch` | A project token at a `/group/` URL, or the reverse |
| `header/label-mismatch` | Valid token, wrong `<name>` in the URL |
| `header/unseeded` | New sub-project on a group with `seed: false` |

A malformed header refuses outright rather than falling back to any other
method. That is deliberate: a mistyped header that silently kept working would
hide the misconfiguration indefinitely.

---

## Maintaining this folder

These are templates, not live config. Editing a file here changes nothing in
any already-installed project — those have to be re-pasted by hand. That is the
core weakness of the whole approach and the reason `NOTES-automation.md`
proposes serving the bundle over MCP instead.

When you change one, say in the commit message which projects still need
re-pasting.
