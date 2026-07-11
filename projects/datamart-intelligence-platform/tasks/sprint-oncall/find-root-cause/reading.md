## Root cause and cascading failures

Finding the *first* failed job — not its victims — is **root cause analysis**, and
it rests on understanding how failures **cascade** through a dependency chain.

In a pipeline `extract → transform → load`, a `transform` failure makes `load`
fail too. But `load` isn't broken; it's *starved* — denied its input. Treating each
red task as its own problem sends you fixing symptoms while the real cause sits
upstream, untouched. In a DAG, failures propagate *downstream*, so the root cause is
always the *most upstream* failure.

Techniques that formalize this:

- **The 5 Whys** — keep asking "why did that fail?" until you reach a cause you can
  actually fix, not a symptom.
- **Follow the dependency graph.** Lineage tells you what feeds what; walk *up* from
  a failure to its source. (The Advanced sprint's blast-radius is this in reverse —
  walking *down* to find impact.)
- **Distinguish trigger from cause.** The 3am deploy *triggered* it; the missing
  null-check was the *cause*. Fix the cause, or it recurs.

Blameless **post-mortems** institutionalize this: find the systemic root cause so
the *class* of failure can't happen again, rather than patching this instance and
moving on.

*Go deeper: root cause analysis; the 5 Whys; cascading failures; blameless
post-mortems.*
