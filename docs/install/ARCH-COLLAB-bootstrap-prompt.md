# Bootstrap prompt

First message to paste into a fresh thread — in a newly installed project, or
in an existing one after the knowledge files change. Verifies the install
actually works, and that what it knows is current, before any real work starts.

Grade the answers against `ARCH-COLLAB-bootstrap-answers.md`. Do **not** paste
that file into the thread: several questions below are chosen precisely because
a stale install gives a specific wrong answer, and a thread that can see the
expected answers proves nothing.

---

Bootstrap check before we start. Answer from project knowledge and the
connectors only — no web search. Work through these in order and reply with a
single table (question number, PASS/FAIL/UNSURE, and a short answer), then
stop. No preamble, no summary.

**Install**

1. List the knowledge files you can see. How many are there, and does any
   filename appear more than once?
2. What is the highest-numbered rule in the constitution? Quote its first
   sentence.
3. Call the arch-mcp connector's `tools/list`. How many tools, and which tool
   families are present?
4. Call `arch_session_status` and `arch_site_list_files`. Is a session open,
   and how many site files are there?

**What it knows**

5. What URL shape does a connector for this project use, and which HTTP header
   carries the token?
6. Is a token in the URL path still accepted by the server?
7. Is `arch session discard` a hard delete or a soft delete — and is that
   behaviour ratified, or proposed?
8. In a group space, are sub-projects isolated from one another?
9. Does the MCP server authenticate its callers? One sentence on how.
10. Does `arch session commit` reporting success prove the session's metadata
    reached git?

**Discipline**

11. The project instructions say certain things must be checked against
    Confluence before being stated as current fact. For each answer above where
    that applies, name the page ID you actually opened and its last-modified
    date. If you answered any of them from the knowledge files alone, say so
    plainly rather than implying you checked.

Do not start any work, do not open a session, and do not write any files.
