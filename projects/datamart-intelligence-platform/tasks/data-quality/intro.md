**Bad data is worse than no data** — it ships silently and misleads everyone downstream.
Data quality is the *Data Management* undercurrent of the lifecycle: catching problems
before they reach a dashboard. Here you write **data tests** — queries that return the
rows that break a rule. The grader proves each test both stays quiet on good data and
actually catches the bad.
