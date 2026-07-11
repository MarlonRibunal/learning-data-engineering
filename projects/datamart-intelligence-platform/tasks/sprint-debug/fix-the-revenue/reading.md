## The silent data bug

The revenue-includes-refunds bug is the most dangerous kind in data engineering: a
**silent, semantic bug.** The code runs fine. No error, no crash, no failed task —
it just produces a *wrong number*, and wrong numbers propagate confidently into
decisions.

Why data bugs are worse than software bugs:

- **They don't announce themselves.** A null-pointer crashes and pages you; an
  overstated revenue figure sails into a board deck. The absence of an error is not
  evidence of correctness.
- **They're bugs in *meaning*, not syntax.** `SUM(amount)` is valid, runs, returns
  a number — it just encodes the wrong *definition* of "revenue." Catching it needs
  someone who knows the business rule (refunds aren't revenue), not a linter.
- **They compound.** A wrong intermediate feeds every downstream mart and dashboard,
  so one definition error corrupts dozens of numbers, all internally consistent and
  all wrong.

The defenses are exactly what this course drills: **data tests** that assert
business rules ("revenue excludes refunded"), **reconciliation** against a known
figure, and **sanity checks** ("does this total *feel* right?"). The scariest
pipeline isn't the one that's failing loudly — it's the green one quietly shipping
a number that's subtly off.

*Go deeper: semantic vs. runtime bugs; testing business logic; reconciliation as a
safety net.*
