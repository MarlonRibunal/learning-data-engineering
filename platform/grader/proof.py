"""Portfolio proof-artifact generator — the growth loop.

When a learner passes a capstone, the grader writes a portfolio-ready folder they
commit to their OWN GitHub:

    portfolio/<sprint>-<task>/
      PORTFOLIO.md          what they built + pipeline diagram + verified checks
      verified-checks.json  machine-readable list of what passed
      chart.png             (best-effort) a chart rendered from their real result

Honest and zero-hosting: it shows the actual verified work, needs no central
authority, and is inherently shareable because it is just files in a repo.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .context import Context
from .result import Result
from .spec import TaskSpec


def generate_proof(
    sprint: str,
    task: str,
    spec: TaskSpec,
    result: Result,
    ctx: Context,
    out_root: Path,
    *,
    now: datetime | None = None,
) -> Path:
    """Write the portfolio artifact for a passed task. Returns the output dir."""
    proof = spec.proof or {}
    out_dir = out_root / "portfolio" / f"{sprint}-{task}"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now(timezone.utc)).isoformat()

    checks = [{"name": c.name, "status": c.status.value} for c in result.checks]
    (out_dir / "verified-checks.json").write_text(
        json.dumps(
            {
                "sprint": sprint,
                "task": task,
                "title": proof.get("title", spec.title),
                "generated_at": stamp,
                "status": result.status.value,
                "checks": checks,
            },
            indent=2,
        )
        + "\n"
    )

    chart_rel, chart_rows = _try_chart(proof.get("chart"), ctx, out_dir)
    (out_dir / "PORTFOLIO.md").write_text(
        _portfolio_md(sprint, task, spec, proof, result, stamp, chart_rel, chart_rows)
    )
    return out_dir


def _try_chart(chart: dict | None, ctx: Context, out_dir: Path):
    """Best-effort chart from the learner's real result. Returns (filename|None, rows|None).

    Degrades gracefully: no chart config, no matplotlib, or an unreachable DB just
    means no image — never an error.
    """
    if not chart or not chart.get("query"):
        return None, None
    try:
        rows = ctx.db.query(chart["query"])
    except Exception:  # noqa: BLE001 - proof is best-effort; DB may be down
        return None, None
    if not rows:
        return None, None

    labels = [str(r[0]) for r in rows]
    try:
        values = [float(r[1]) for r in rows]
    except (TypeError, ValueError, IndexError):
        return None, rows

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None, rows  # keep the data table in the md even without a chart

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values)
    ax.set_title(chart.get("title", ""))
    ax.set_ylabel(chart.get("ylabel", ""))
    fig.tight_layout()
    fig.savefig(out_dir / "chart.png", dpi=120)
    plt.close(fig)
    return "chart.png", rows


def _portfolio_md(sprint, task, spec, proof, result, stamp, chart_rel, chart_rows) -> str:
    title = proof.get("title", spec.title)
    lines = [f"# {title}", ""]
    if proof.get("summary"):
        lines += [proof["summary"], ""]
    lines += [f"_Verified by the learn-by-doing grader on {stamp}._", ""]

    if proof.get("pipeline"):
        lines += ["## Pipeline", "", "```", proof["pipeline"].rstrip(), "```", ""]

    lines += ["## Verified checks", ""]
    for c in result.checks:
        mark = "✅" if c.status.value == "pass" else "❌"
        lines.append(f"- {mark} {c.name}")
    lines.append("")

    if chart_rel:
        lines += ["## Result", "", f"![chart]({chart_rel})", ""]
    elif chart_rows:
        lines += ["## Result", ""]
        lines.append("| " + " | ".join(str(x) for x in _headers(chart_rows)) + " |")
        lines.append("|" + "---|" * len(chart_rows[0]))
        for row in chart_rows:
            lines.append("| " + " | ".join(str(x) for x in row) + " |")
        lines.append("")

    lines += ["---", "",
              f"Built on the [learn-by-doing data engineering platform]"
              f"(https://github.com/MarlonRibunal/learning-data-engineering) "
              f"(task `{sprint}/{task}`)."]
    return "\n".join(lines) + "\n"


def _headers(rows):
    return [f"col{i + 1}" for i in range(len(rows[0]))]
