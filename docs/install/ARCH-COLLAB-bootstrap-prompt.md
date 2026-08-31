# Bootstrap prompt

First message to paste into a fresh thread in a newly installed project.
Verifies the install actually works before any real work starts.

---

Bootstrap check before we start. Do these in order and report a short PASS/FAIL
table, nothing else:

1. Confirm you can see `ARCH-CONSTITUTION.md`, `PROJECT-CONTEXT.md` and
   `INDEX.md` in project knowledge. Quote rule 12's first sentence.
2. Call the arch-mcp connector's `tools/list`. Report how many tools and
   whether both the `arch_session_*` and `arch_site_*` families are present.
3. Call `arch_session_status`. Report whether a session is open.
4. Call `arch_site_list_files`. Report the file count.
5. Via Rovo, fetch Confluence page `10879042` (10-ARCH-MISSION) and report its
   title and last-modified date.
6. Compare that date against PROJECT-CONTEXT.md's "Current state (as of ...)"
   line and tell me whether the snapshot is stale.

Do not start any work, do not open a session, and do not write any files.
