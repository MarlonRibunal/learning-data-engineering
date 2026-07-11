## Choosing the right chart

Revenue over time is a **line chart** — and *why* is a principle worth owning:
match the visual encoding to the data's structure.

- **Line** — a continuous quantity over ordered time. The connecting line implies
  "these points are a sequence," which is exactly right for a trend and exactly
  *wrong* for unordered categories.
- **Bar** — comparing a measure across discrete categories (revenue *by category*).
  Length is easy to compare; don't connect bars with a line.
- **The cardinal sin** is using a line for categories or a pie for anything with
  more than a few slices — the encoding lies about the data's shape.

Two engineering-side gotchas that decide whether the chart tells the truth:

- **Continuity / gaps.** A missing day should show a gap or a zero, not a straight
  line pretending nothing happened — the date-spine issue from the serving sprint,
  surfacing visually.
- **Aggregation grain.** Daily vs. weekly vs. monthly changes the story; the
  engineer chooses the grain that reveals signal without drowning it in noise.

Good dashboards start from the question and pick the encoding that answers it most
honestly — the visualization equivalent of picking the right SQL.

*Go deeper: chart-choice heuristics; line vs. bar vs. area; gaps in time series.*
