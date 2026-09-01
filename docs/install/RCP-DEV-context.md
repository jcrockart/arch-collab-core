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

**Not recorded anywhere yet:** the practice's trading name and its production domain. Ask
James rather than guessing — nothing in this project should assume `crockart.com.au` is the
public-facing address.

## How dev and production relate

- **Dev (`crockart.com.au/rcp`)**: freely editable, safe to experiment on. Changes written
  here are NOT visible to real site visitors and are not in git history until committed.
- **Production**: the real site patients see. Getting a dev change into production is a
  **separate, deliberate action** — James reviews the working tree, commits, and deploys
  (a server-side `git pull`, then the `chmod` step, because git-created directories default
  to permissions that block the web server). That step is not exposed through this project
  and should never be attempted from here.

## How edits actually happen

This project connects to an MCP server exposing file tools scoped to the `rcp` site
directory only (list / read / write). Claude uses these directly when asked to change the
site — no manual upload, no code to write, just plain-language requests like "update the
heel pain page to mention X" or "add a new page about Y".

## Open items — confirm with James before relying on this project

1. **No `rcp`-scoped MCP endpoint exists yet.** As of 2026-08-31 the live server
   (`mcp.crockart.com.au`) has a site lane scoped to `arch-collab-core/site` only — that is
   the ARCH Field Guide, not this site. Something has to serve `rcp` before any of the above
   works.
2. **Unresolved design question:** does `rcp` get its own MCP server instance, or does the
   existing server gain a project-scoped site lane selecting between projects? Not decided.
   The second is less infrastructure but widens what one URL can reach.
3. **The server currently has no authentication at all.** Anyone with the URL can call every
   tool on it. That is tolerable for a single-user spike and is not tolerable once a URL is
   handed to a second person. A shared secret in the URL has been discussed as the minimum
   fix — discussed, not implemented. **Do not hand out a connector URL until this is done.**
   Tracked as Codegen CLI Design §9 item 5.

## Scope

If asked to do anything outside editing content in `rcp` — server config, git, deployment,
anything involving credentials — stop and say that's outside scope.
