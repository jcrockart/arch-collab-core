# Bootstrap answer key

Grade `ARCH-COLLAB-bootstrap-prompt.md` against this. **Never paste this file
into the thread being tested.**

Questions 5–10 exist because a stale install gives a *specific* wrong answer,
not a vague one. That is the whole design: a check that cannot fail is not a
check. The "wrong answer means" column tells you what to go and fix.

Current as of **2026-09-02**. When the system changes, change this file in the
same commit — an answer key that has gone stale is worse than none, because it
fails correct answers and passes wrong ones.

## Install

| # | Expected | A wrong answer means |
|---|---|---|
| 1 | **14 files, no duplicates.** | A repeated filename means a revision was uploaded *alongside* its predecessor rather than over it. This happened with `ARCH-CONSTITUTION.md` (25 Aug vs 27 Aug) and the two gave contradictory instructions, with retrieval free to return either. Delete the older by first line or size, never by list position. |
| 2 | **Rule 12**, beginning "This project's own deliverable is a condensed, installable bootstrap materials bundle…" | "Rule 11" means the pre-27-Aug constitution is present or `INDEX.md` is stale. |
| 3 | **11 tools**: 7 `arch_session_*` (start, status, commit, discard, write_file, read_file, list_files), 1 `arch_codegen_preview`, 3 `arch_site_*`. A four-family breakdown is equally correct — `codegen_preview` is not an `arch_session_*` tool, though it is session-scoped. | 3 tools means the `rcp-dev` token is in the header instead of `arch-collab`. A 404 means the URL and the profile's label disagree. |
| 4 | No session open; site files present (1 as of 2026-09-02). | An empty list with `success: true` is the failure mode from 2026-09-01 — a lane pointing at a directory that does not exist. Do not read it as "no files". |

## What it knows

| # | Expected | A wrong answer means |
|---|---|---|
| 5 | `https://mcp.crockart.com.au/project/<name>/`, token in the **`x-api-key`** header. | "One URL for every project" or `X-Arch-Token` means the install predates 2026-09-02. Both were true once; neither is now. |
| 6 | **No.** Cutover completed 2026-09-02 — `ALLOW_PATH_TOKEN` is false and `.htaccess` no longer routes `/t/`. Both return 404. | "Yes, during migration" means the docs predate the cutover. This is the exact answer a fresh thread gave on 2026-09-02, correctly citing a Confluence page that had not been updated after the deploy. |
| 7 | **Soft delete**, built and tested in `arch.py`, but the design decision is **PROPOSED, not ratified**. | "Hard delete" means the 25-Aug constitution or the stale `agent-connection-layer.md` is being read. Note that "it's soft delete" *without* the unratified caveat is also wrong — that conflates implementation with approval, which Constitution rule 6 exists to separate. |
| 8 | **No.** The group key is the tenant boundary; anyone who can reach one sub-project can reach any other by editing the URL. | "Yes" is the dangerous answer — it would justify handing a group token to someone trusted with only part of the group. |
| 9 | **Yes** — a token in `x-api-key` selects a scope profile deciding root, lanes and tool surface; every refusal is a 404. | "No" means `PROJECT-CONTEXT.md` predates 2026-09-02, where it said so in the reference-implementation section for two days after it stopped being true. |
| 10 | **No.** Rule 5's caveat: `session_commit()` never `git add`/`commit`s the session's own metadata. Verify with `git ls-files`. | A plain "yes" means the caveat is missing from whichever constitution is loaded — the single most consequential thing the old copy omitted. |

## Discipline

**11** is the one that matters most, and the only one where an *honest* answer
beats a confident one.

A good answer names actual page IDs with dates — 38600706 (spike summary),
38174722 (the engineering detail), 10485777 (Codegen CLI Design), 9142274 (Git
Setup & Access Policy §8.3) — or states plainly that it answered from the
knowledge files without checking.

Treat as a FAIL: any claim to have "verified against Confluence" with no page
ID and no date. That is the failure this whole system keeps producing in other
forms — a check reported as passed that was never actually run. An answer of
"I did not check" is a PASS for question 11, because it is true and it tells
you exactly how much to trust answers 5–10.

## If several answers are stale

Do not patch the thread by telling it the right answers — that fixes one
conversation. Fix the source and re-run this prompt in a *new* thread. The
point of the test is the install, not the transcript.

Note that "the source" may be Confluence rather than the knowledge files. On
its first run, this test failed question 6 — and the thread was not at fault.
It checked Confluence exactly as the project instructions require, and the page
was stale. A correct process reading an incorrect source produces a confident
wrong answer, and only an answer key with a known-good value catches it.
