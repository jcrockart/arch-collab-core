# RCP DEV — background context

Upload this as a knowledge file in the "RCP DEV" project.

## What this is

`crockart.com.au/rcp` is a development/staging copy of **Rachel Crockart's** website — a
podiatry practice. It is a real git checkout on the server, currently containing pages on
foot-care topics (corns & calluses, cracked heels, diabetic foot care, dry skin, flat
feet/pronation, foot massage, foot mobilisation, heel pain, choosing footwear, plus a
homepage).

Project facts, from the committed `project.config.json` in the repo root (commit
`c6eaa79`, 2026-09-04) — no longer from the worked example on Confluence 35880962:

| | |
|---|---|
| Project name | `rachel-crockart-podiatry` |
| Git remote | `git@github.com:jcrockart/rachel-crockart-podiatry.git` (branch `main`) |
| Hosting provider | Micron21 reseller cPanel/WHM |
| Server host | `cp-kil-m-021.micron21.com` |
| cPanel account | `crockart` |
| Domain | `crockart.com.au` |
| Document root | `/home/crockart/public_html` |
| Dev deploy path | `public_html/rcp` |
| Deploy mechanism | `ssh-git-pull`, with a `chmod 755` pass over directories afterwards |
| Runtime | `static-html`, no database |
| Scheduled jobs | none (verified: `crontab -l` is empty) |
| TLS | AutoSSL (verified: `uapi SSL installed_hosts` reports `is_autossl: 1`) |

Those values are **verified, not assumed** — `scheduled_jobs` and `tls` were each read off
the server rather than inferred. If a bootstrap check runs in this project, its job here is
to *confirm* this table, not to interview anyone for it.

Two caveats the table cannot carry:

- These values describe **dev only**. The current schema has no way to express dev and
  production in one file; see below.
- `runtime: static-html` is ahead of 61-ARCH-PLATFORM's confirmed capability menu, which
  lists PHP (confirmed) and Node (conditional). It is flagged deliberately rather than
  quietly used.

## The deploy path sits inside the document root

`deploy_path` is `public_html/rcp`, so **the repo root and the web document root are the
same directory**. Everything in the checkout is served over HTTP unless something denies
it — including `project.config.json` and the whole of `.git/`.

A `.htaccess` in the repo (commit `4512386`) denies `project.config.json`, `.git*`, `.env`
and `*.bak*`, and disables directory listings. It is committed deliberately so the
protection travels with the code instead of depending on a server rule that exists only on
this account.

Two things follow, and they matter more than they look:

1. **Do not write anything secret into this site directory.** Not a token, not a key, not
   a note containing one. It is a public web directory that happens to be a git checkout.
2. **A 404 is not proof the deny rule works.** Apache resolves not-found before it checks
   authorisation, so requesting a file that does not exist returns 404 whether or not the
   rule would have denied it. The only valid test is to place a real file and confirm
   **403**. That mistake was made here on 2026-09-03 and the site was briefly believed
   protected by a rule that was not in the repo at all.

## Production — separate site, separate cPanel

Production is **https://rachelcrockartpodiatry.com.au/** — "Rachel Crockart Podiatry,
Ashburton", a static site. It lives on **RCP's own cPanel account**, not the `crockart`
account that hosts the dev copy. Same git repo, different server, different domain.

Production is **not declared** in `project.config.json` — its cPanel account username, WHM
host, document root and deploy path have never been recorded. Under the "default
non-production" principle (Confluence 37945345) that is the correct and safe state: until a
production environment is completely declared, the project is dev-only and nothing may
publish to it. Do not fill those values in by guessing them.

The `environments` map that would let one file describe both dev and production is
**proposed and not built**. Emitting it today would produce a file that fails `validate.py`,
so the committed config uses the flat shape and describes dev.

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

## Connector and access

**Resolved 2026-09-01, addressing revised 2026-09-02.** The `rcp` lane exists as a
token-scoped profile on the existing server — one server, one URL *per space*, each with
its own token — and the server authenticates every request. This project's connector is
`https://mcp.crockart.com.au/project/rcp-dev/`, with the token in the `x-api-key` header.
Verified: the `rcp-dev` token returns exactly 3 site tools and no session tools, and cannot
read outside `/home/crockart/public_html/rcp`.

Note that a token in the URL path (`/t/<token>/`) is **no longer accepted**. Cutover
completed 2026-09-02; both the server flag and the rewrite rules were removed, and that
route now returns 404.

## Open items — confirm with James before relying on this project

1. **Token rotation.** The `rcp-dev` token was displayed on screen during setup. James
   reported it rotated on 2026-09-04; that is his statement, not something verified from
   this side. If in doubt, rotate again — it costs a minute.
2. **Production is undeclared** (see above). Provisioning it is a known, semi-manual
   sequence — enable Shell Access on the prod account's WHM package, generate a read-only
   deploy key there, register it on the repo, verify, clone, `chmod` — and only then does the
   config gain a `production: true` block. Page 37945345 has the full sequence.
3. **The production site has no `.htaccess` protection yet** beyond what ships in the repo.
   It will inherit `4512386` on its first pull, but nobody has confirmed the production
   document root is laid out the same way. Check before assuming it is covered.

## Scope

If asked to do anything outside editing content in `rcp` — server config, git, deployment,
anything involving credentials — stop and say that's outside scope.
