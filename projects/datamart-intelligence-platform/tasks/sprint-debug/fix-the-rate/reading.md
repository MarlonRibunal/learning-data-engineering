## Sanity checks and dimensional reasoning

The "0.1 instead of 12.5%" bug — off by a factor of 100 — is caught not by a
debugger but by a **sanity check**: a rate of 0.1% conversion is *obviously* wrong
for a business that converts 1 in 8 visitors. Cultivating that "these numbers can't
be right" reflex is one of the most valuable instincts a data engineer has.

Ways to catch order-of-magnitude errors *before* they ship:

- **Dimensional / unit reasoning.** Track what a number *is*: a ratio (0.125) is
  unitless; a percentage is ×100. Mixing the two is a units error, the same class as
  the famous Mars Climate Orbiter loss (pounds vs. newtons). Ask "what are the units
  of my answer?"
- **Order-of-magnitude estimation.** Before trusting a computed value, guess its
  rough size. If conversion should be "roughly 10%," a result of 0.1 fails the smell
  test instantly.
- **Boundary and identity checks.** A percentage should sit in 0–100; a probability
  in 0–1. Values outside the plausible range are a red flag your code can *assert*.

These habits — units, magnitudes, plausible ranges — are cheap to apply and catch a
huge share of "valid but wildly wrong" bugs that no type-checker ever will. The best
data engineers are perpetually, productively suspicious of their own numbers.

*Go deeper: dimensional analysis; order-of-magnitude ("Fermi") estimation; sanity
checks / assertions.*
