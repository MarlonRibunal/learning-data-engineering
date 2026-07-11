# Cohort retention curve

**The scenario.** Every growth team's core question: of the users who signed up
together (a **cohort**), how many are still active on day 1, day 2, day 3…? That
declining curve — retention — is the single most-watched metric in product
analytics, and computing it is a **set intersection per day**.

## Intersect the cohort with each day's actives

```python
def retention_curve(cohort, activity):
    cohort = set(cohort)
    return {
        day: len(cohort & set(users))
        for day, users in sorted(activity.items())
    }
```

- **`cohort`** is your group of users; make it a `set` for fast intersection.
- **`activity`** maps each `day → [users active that day]`.
- For each day, **`cohort & set(users)`** keeps only the cohort members who were
  active, and `len(...)` counts them.
- `sorted(activity.items())` keeps the curve in day order.

## Your task

Write `retention_curve(cohort, activity)` returning `{day: count}` — how many of
the cohort were active each day. Cohort `[1,2,3]` with the given activity yields
`{1: 3, 2: 2, 3: 1}` — a classic decay.
