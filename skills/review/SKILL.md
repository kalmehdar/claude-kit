---
name: review
description: Check a change against the project's own standards and report honestly what was tested. Use before handing work back, before a PR or release, or when the user asks "is this done", "review this" or "did you test it".
---

# Review

1. **Standards come from the project, not from memory.** Read the repo's `CLAUDE.md`, README and any rule file they name.
2. **Run the checks the project defines** (its test, lint and type-check commands), and quote the result line.
   - A test you wrote is not trusted until you have made it fail by breaking the thing it guards.
3. **Look at the thing, not only the tests.** For a screen, open it and look at it at phone and desktop width; for a claim, find its source.
4. **Report in three lists:**
   - **Verified:** each check, the command and the result.
   - **Not tested:** each gap, and why.
   - **Found:** defects, each with file:line and the smallest fix.

Never write "done" for something only partly checked. A failed check is reported as failed, with its output.
