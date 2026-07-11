## Reading code you didn't write

Most engineering isn't writing new code — it's **reading and fixing existing code**,
usually someone else's, usually under pressure. This bug (dedup keeps the *first*
version instead of the *latest*) is a chance to practice a repeatable debugging
method rather than guessing.

A disciplined approach:

- **Reproduce, then read.** You have a failing case and the code. Trace the code by
  hand on that input — *predict* what each line does — before changing anything.
  Here: "the guard is `if key not in best`, so the first occurrence wins and later
  ones are skipped." Now you *understand* the bug, not just its symptom.
- **Form one hypothesis, test one change.** Change the smallest thing that your
  reading says is wrong (the guard), and re-run. Shotgun edits hide which fix
  actually worked.
- **Bugs cluster at edges.** First/last, empty input, ties, off-by-one — the
  boundaries are where logic breaks. "Keeps the first instead of the last" is a
  classic edge-of-iteration bug.

This is also why **tests and small, reviewable functions** matter: a bug in a tiny
pure function is trivial to isolate; the same bug buried in a 300-line job is a
nightmare. Debugging skill is mostly reading skill plus discipline.

*Go deeper: the scientific debugging method; reading code; boundary bugs.*
