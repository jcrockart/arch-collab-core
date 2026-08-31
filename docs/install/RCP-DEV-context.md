# RCP DEV — background context

Upload this as a knowledge file in the "RCP DEV" project.

## What this is

`crockart.com.au/rcp` is a development/staging copy of [wife's name]'s website — a real git
repository checked out directly on the server, currently containing pages about foot care
topics (corns & calluses, cracked heels, diabetic foot care, dry skin treatments, flat
feet/pronation, foot massage, foot mobilisation, heel pain, choosing footwear, plus a
homepage). This is presumed to be a podiatry/foot-care business site — update this note with
the actual business name and details once confirmed.

## How dev and production relate

- **Dev (`crockart.com.au/rcp`)**: freely editable, safe to experiment on. Changes written here
  are NOT visible to real site visitors and are not tracked in git history until committed.
- **Production**: the real, live site customers see. Getting a dev change into production is a
  **separate, deliberate action** — James reviews the working tree, commits to git, and deploys.
  That step is not exposed through this project and should never be attempted from here.

## How edits actually happen

This project is connected to an MCP server that exposes file tools scoped to the `rcp` site
directory only (list / read / write). Claude uses these tools directly when asked to change
the site — there's no manual upload step, no code to write, just plain-language requests like
"update the heel pain page to mention X" or "add a new page about Y."

## Known limitations / open items

- As of this note, the write-capable MCP endpoint for `rcp` had not yet been built — only the
  equivalent tooling for a different project (arch-collab) existed. Confirm with James that the
  connector URL in this project's settings is live before relying on it.
- The MCP server for this project should have a shared-secret token baked into its URL (agreed
  2026-08-31) rather than being open to the public internet — confirm this is in place.
- If asked to do anything outside editing content in `rcp` (server config, git, deployment,
  anything involving credentials), stop and say that's outside scope.
