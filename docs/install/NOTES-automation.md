# Note: why there is no installer

**Status:** design note. The `arch_bootstrap` proposal below is **not
approved and not built** — it needs sign-off on that specific change.
Written 2026-08-31.

## The question

Can installing a Claude project be automated — an `.exe` that drops the right
context into a new project space?

## The claude.ai half: no

There is no public API for creating a project, setting project instructions,
uploading knowledge files, or registering a custom connector. All four are UI
actions. An installer would have to drive a browser, which is more fragile than
the three minutes it saves — and browser automation against claude.ai is the
least stable thing in this stack. An evening already went into fighting
cPanel's in-browser editor for exactly this class of reason.

The connector URL paste is irreducible in any case. A human does it once.

## The bundle half: yes, but shrink it instead

`PROJECT-CONTEXT.md` opens by warning that it is a snapshot and Confluence is
live. Uploading it into a fresh project re-freezes that warning at install time
and restarts the drift immediately. Fourteen files across five projects means
five vintages of the same truth, and `agent-connection-layer.md` is already
proof this happens — it has been stale since the file tools shipped.

Scripting the copy makes the drift faster, not smaller.

## Proposal: serve the bundle over MCP

The server already solves this shape for `metadata/` and `site/`. Extend it
with a read-only **`arch_bootstrap`** tool backed by a `bootstrap/` directory
in `arch-collab-core`, returning a manifest plus file contents.

A fresh project then needs:

- one connector URL (a human pastes it, once)
- ~10 lines of project instructions saying "call `arch_bootstrap` first"

No uploads, no manifest to keep in sync, no stale copies. Update the repo once
and every project installed afterwards — and every existing one, on its next
session — gets the current bundle.

That is rule 12 taken one layer out: a project reaches ARCH by installing a
copy of the bundle, and the MCP server becomes the distribution channel for it.
It extends *Proposal: ARCH-COLLAB as Installable Bootstrap Materials*
(Confluence page 35880962) rather than competing with it.

## The trade, honestly

Knowledge files are injected into context free and always. A tool call costs a
round trip and depends on the agent actually making it. Mandating it in the
project instructions plus the bootstrap prompt's PASS/FAIL table covers that,
but it is a real cost, not a free win.

There is also a resilience argument for files: if the connector is down, an
uploaded constitution is still there and a bootstrap-only project is empty.

**Suggested split:** constitution and schemas stay as uploaded files — they
change rarely and are what you most want present when a connector is down.
Current state, open questions, and the tool surface come live. That is already
the discipline the project instructions describe; `arch_bootstrap` just makes
it mechanical instead of a habit.

## Sequencing

`arch_bootstrap` is a change to the server that defines the MCP security
boundary, so it needs explicit sign-off on that specific change — a general
go-ahead for a session does not cover it. It is read-only and narrower than
anything already deployed, so it is a small ask, not a large one.

Install bundle A by hand first. If doing it a second time feels tedious, that
is the signal to build the tool.
