# BOOTSTRAP — install check and project inception

Upload this as a knowledge file into every project installed from this bundle.
To run it, say **"run the bootstrap check"** in any thread.

It does two jobs that used to be separate, and deliberately in this order:

1. **Verify the install** — is what's here actually here, and does it work?
2. **Declare the project** — collect the configuration a project needs, and
   emit a `project.config.json` draft.

Verification comes first because there is no point interviewing someone about
a project whose tools don't answer.

---

## Rules that override anything else in this file

These are not preferences. If following an instruction below would break one of
these, stop and say so.

- **Never ask for, accept, or repeat a token, password, key or credential.**
  Tokens are minted on the server and typed into a connector dialog by a human.
  If the person offers one, tell them not to paste it and to treat it as
  compromised if they already have. The check confirms a connector *works*; it
  never handles what makes it work.
- **Never set `production: true`, and never fill in production values as
  though they were configured.** A project is non-production until a human
  completes the provisioning sequence (Confluence 37945345). Collecting the
  production domain is fine; declaring the environment is not.
- **Never write files during this check** unless the person explicitly asks
  you to, after seeing the draft. Emit the config as text in the reply.
- **Never guess a value to fill a field.** An empty field with a reason is a
  correct answer. An invented one is the failure this whole system keeps
  producing — a check that looks complete and isn't.

---

## Phase 1 — Verify. Do not ask; find out.

Anything discoverable must be **discovered**, not asked. Report what you
actually observed, not what you expected.

1. **Knowledge files.** List them. How many, and **does any filename appear
   more than once?** A repeated name is not cosmetic: uploading a revision does
   not replace its predecessor, so two versions coexist and retrieval may
   return either. This has produced directly contradictory instructions in a
   live project. If you find one, say which to delete and how to tell them
   apart (first line, or size — never list position).
2. **Connector.** Call `tools/list`. Report the count and the tool families.
   Then call one read-only tool (a file listing) and report what came back.
   - An empty list with `success: true` is **not** "no files" — it is the
     known signature of a lane pointing at a directory that does not exist.
     Report it as suspicious, not as success.
   - A 404 means the URL and the token's profile label disagree, or the token
     is unknown. Say which you think it is and why.
3. **Scope.** Attempt one read that *should* be refused — a path outside the
   lane, e.g. `../` something. Report the refusal. **A check that cannot fail
   is not a check**: if the refusal doesn't happen, that is the finding.
4. **Staleness — only if there is something to compare against.** This step
   applies when *both* are true: the project's knowledge names Confluence
   pages, **and** a Confluence connector is already available to you. If so,
   open the one or two most relevant, compare against what the files say, and
   name the page IDs with their last-modified dates.

   If either is missing, write **"no upstream to compare against"** and move
   on. For a consumer project it usually will be missing — those installs
   carry no constitution and their users hold no Confluence connector — and
   that is the correct state for such an install, not a gap. Do not offer to
   bring in a connector the project was never meant to have; a row that always
   reports the same non-answer teaches people to skip it.

   If a connector *is* available and you simply did not check, say so plainly
   rather than implying you did.

Report Phase 1 as a short table before asking anything.

---

## Phase 2 — Interview, but only for what cannot be discovered

Ask **one question at a time**, in plain language, and say why each matters.
Do not present the whole list at once — it reads as a form and gets guessed at.

Before asking, **infer what you reasonably can and offer it for confirmation**
rather than asking cold. If a site listing is all `.html` and `.css`, propose
`runtime: static-html` and ask them to confirm. Confirming a proposal is more
reliable than answering from memory, and it shows your reasoning.

Fields, from `project.config.schema.json` (Confluence 35880962):

| Field | Notes |
|---|---|
| `project` | Short kebab-case name, e.g. `rachel-crockart-podiatry` |
| `git.remote` | SSH form, e.g. `git@github.com:owner/repo.git` |
| `git.default_branch` | Usually `main` |
| `hosting.provider` | e.g. "Micron21 reseller cPanel/WHM" |
| `hosting.server_host` | The actual host, e.g. `cp-kil-m-021.micron21.com` |
| `hosting.account_username` | The cPanel account |
| `hosting.domain` | The domain this environment serves |
| `hosting.document_root` | Absolute path |
| `hosting.deploy_path` | Path relative to the account home |
| `deployment.mechanism` | One of `ssh-git-pull`, `sftp-direct-sync`, `provider-api` |
| `deployment.post_pull_steps` | Optional array — see below |
| `capabilities.runtime` | One of `static-html`, `php`, `node` |
| `capabilities.database` | `mysql` or `none` |
| `capabilities.scheduled_jobs` | Boolean |
| `capabilities.tls` | e.g. `autossl` |

**Two things to raise rather than wait to be told:**

- **`post_pull_steps`.** For cPanel + `ssh-git-pull`, git-created directories
  default to permissions that block the web server. The known fix is a
  `find . -type d -exec chmod 755 {} \;` pass after every pull. Propose it.
  It exists as a field precisely so that gotcha stops living in someone's
  memory.
- **`static-html`** is used as a runtime value but is **not** on
  61-ARCH-PLATFORM's confirmed capability menu, which currently lists PHP
  (confirmed) and Node (conditional). If the answer is `static-html`, say that
  it is ahead of the menu — flag it, don't quietly use it.

---

## Phase 3 — Emit the draft

Output `project.config.json` as text in the reply, in the **flat
`hosting`/`deployment` shape above** — not the `environments` map.

That is a deliberate choice with a reason: the flat shape is what
`validate.py` actually accepts today. The `environments` map (Confluence
37945345) is **proposed and not built**, so emitting it would produce a file
that fails the very gate it exists to pass. When the environment axis is built,
this section changes with it.

Say plainly which environment the values describe — for a project with a dev
copy and a separate production site, these fields describe **one** of them,
and the schema currently cannot express the other.

### Unanswered fields: omit them, never null them

**Leave an unanswered key out of the JSON entirely.** Do not emit `""`, `null`,
or a placeholder. `validate.py` requires these fields, so a draft containing
`"tls": null` looks finished and fails the moment anyone uses it — the exact
defect this check exists to catch, produced by the check itself.

Then head the draft with one line naming what is missing, in this form:

    INCOMPLETE — will not pass validate.py until these are supplied:
    hosting.document_root, capabilities.scheduled_jobs, capabilities.tls

If nothing is missing, say **COMPLETE** just as explicitly. A draft that is
silent about its own completeness cannot be trusted either way.

---

## Phase 4 — State what is *not* declared, and why

This is the part most likely to be skipped and the part that matters most.
End with an explicit list. For a typical project that means:

- **Production is undeclared.** Name the values collected, and state that
  declaring the environment requires the human provisioning sequence on
  Confluence 37945345 — shell access on the production account's WHM package,
  a read-only deploy key generated there, registered on the repo, verified,
  cloned, `chmod` — and only then a `production: true` block. Until that
  happens, nothing may publish to production, and that is the correct state,
  not a gap.
- **Any field left empty**, with the reason it is empty.
- **Anything you could not verify**, separated from what you did verify.

---

## Re-running

Run this again after any change to the knowledge files, the connector, or the
config — and after any deploy that changes how the server is addressed. It is
cheap and it is the only thing that catches an install that has quietly gone
stale.

**A note on grading.** This check reports what it found; it does not grade
itself, because for a generic project there are no expected values to grade
against — only the person running it knows whether `hosting.domain` is right.
What it *can* assert without knowing the project are the invariants: no
duplicate filenames, refusals actually refuse, an empty listing is suspicious,
and an unverified claim is labelled as such. Treat a confident summary with no
evidence behind it as a failure regardless of how good it reads.
