## Normalization: comparing unlike things

Min-max scaling to 0–1 looks like a display trick, but it's an instance of a deep,
recurring need: **making unlike quantities comparable.** Revenue in millions and
latency in milliseconds can't share an axis — until you normalize both to a common
scale.

Where this shows up:

- **Small multiples & shared axes.** To compare many series' *shapes* (not
  magnitudes) on one grid, normalize each so a big-revenue category and a tiny one
  reveal their trends side by side. **Indexing** (everything = 100 at a start date)
  is the same idea, common in finance.
- **Feature scaling in ML.** Models that use distances (k-means, kNN) or gradient
  descent are dominated by whichever feature has the largest raw range unless you
  scale features to comparable ranges. Min-max and **z-score standardization** are
  the two workhorses — a preprocessing step data engineers build into feature
  pipelines constantly.
- **The trade-off.** Min-max is sensitive to outliers (one huge value squashes
  everything else toward 0); z-score handles outliers better but assumes a roughly
  normal spread. Choosing the right scaler is part of the craft.

So a sparkline normalizer and an ML feature scaler are the same mathematics —
rescaling so comparisons are about shape, not units.

*Go deeper: min-max vs. z-score standardization; indexing to 100; feature scaling.*
