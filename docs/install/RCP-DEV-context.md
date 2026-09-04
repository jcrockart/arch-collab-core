# RCP DEV — background context

Upload this as a knowledge file in the "RCP DEV" project.

## What this is

`crockart.com.au/rcp` is a development/staging copy of **Rachel Crockart's** website — a
podiatry practice. It is a real git checkout on the server, currently containing pages on
foot-care topics (corns & calluses, cracked heels, diabetic foot care, dry skin, flat
feet/pronation, foot massage, foot mobilisation, heel pain, choosing footwear, plus a
homepage).

Known project facts, from `project.config.json`'s worked example (Confluence page 35880962):

| | |
|---|---|
| Project name | `rachel-crockart-podiatry` |
| Git remote | `git@github.com:jcrockart/rachel-crockart-podiatry.git` (branch `main`) |
| Hosting | Micron21 reseller cPanel, `crockart.com.au`, account `crockart` |
| Dev path | `public_html/rcp` |
| Deploy mechanism | `ssh-git-pull`, with a `chmod 755` pass over directories afterwards |
| Runtime | static HTML, no database |

## Production — separate site, separate cPanel

Production is **https://rachelcrockartpodiatry.com.au/** — "Rachel Crockart Podiatry,
Ashburton", a static site. It lives on **RCP's own cPanel account**, not the `crockart`
account that hosts the dev copy. Same git repo, different server, different domain.

Production is **not yet formally configured** in `project.config.json` — its cPanel account
username, WHM host, document root and deploy path have never been recorded. Under the
"default non-production" principle (Confluence page 37945345) that is the correct and safe
state: until a production environment is completely declared, the project is dev-only and
nothing may publish to it. Do not fill those values in by guessing them.

## How dev and production relate

- **Dev (`crockart.com.au/rcp`)**: freely editable, safe to experiment on. Changes written
  here are NOT visible to real site visitors and are not in git history until committed.
- **Production** (`rachelcrockartpodiatry.com.au`, RCP's own cPanel): the real site patients
  see. Getting a dev change there is a **separate, deliberate, semi-manual action** — James
  reviews the working tree, commits, and runs a server-side `git pull` followed by the
  `chmod 755` pass (git-created directories default to permissions that block the web
  server). That step is not exposed through this project and should never be attempted from
  here.

## How edits actually happen

This project connects to an MCP server exposing file tools scoped to the `rcp` site
directory only (list / read / write). Claude uses these directly when asked to change the
site — no manual upload, no code to write, just plain-language requests like "update the
heel pain page to mention X" or "add a new page about Y".

## Open items — confirm with James before relying on this project

**Resolved 2026-09-01, addressing revised 2026-09-02.** The first three items here are
done. The `rcp` lane exists as a token-scoped profile on the existing server — one server,
one URL *per space*, each with its own token — and the server now authenticates. This
project's connector is `https://mcp.crockart.com.au/project/rcp-dev/`, with the token in
the `x-api-key` header. Verified: the `rcp-dev` token returns exactly 3 site tools and no
session tools, and cannot read outside `/home/crockart/public_html/rcp`.

1. **Token rotation outstanding.** The `rcp-dev` token was displayed on screen during
   setup. Reissue it before this project is handed to anyone else.
2. **Production is undeclared** (see above). Provisioning it is a known, semi-manual
   sequence — enable Shell Access on the prod account's WHM package, generate a read-only
   deploy key there, register it on the repo, verify, clone, `chmod` — and only then does the
   config gain a `production: true` block. Page 37945345 has the full sequence.

## Scope

If asked to do anything outside editing content in `rcp` — server config, git, deployment,
anything involving credentials — stop and say that's outside scope.
