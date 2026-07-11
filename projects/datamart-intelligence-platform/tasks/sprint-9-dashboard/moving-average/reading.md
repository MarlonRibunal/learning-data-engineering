## Smoothing: signal vs. noise

A raw daily line is jagged — weekends dip, one big order spikes it — and that noise
hides the trend. A **moving average** smooths it, and it's your first taste of a
huge idea: separating **signal** from **noise**.

The trade-offs every smoother makes:

- **Window size = smoothness vs. lag.** A longer window is smoother but *lags* —
  it reacts slowly to real changes, because it's still averaging in old data. A
  short window tracks turns quickly but stays noisy. There's no free lunch; you
  pick where to sit.
- **Trailing vs. centered.** A *trailing* average (only past points) is causal — it
  can run in real time, but it lags. A *centered* average (past and future points)
  is smoother and lag-free, but needs future data, so it only works on history.
- **Beyond the simple mean.** Weighted and **exponential** moving averages weight
  recent points more, reacting faster while still smoothing — the basis of EWMA
  charts and much of time-series forecasting.

Removing a weekly cycle to see the underlying trend is **seasonal decomposition** in
miniature. Smoothing is where a dashboard stops showing *data* and starts showing
*insight*.

*Go deeper: moving averages (simple/weighted/exponential); trailing vs. centered;
seasonality & signal-vs-noise.*
