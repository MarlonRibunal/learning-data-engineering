def top_categories(rows, n):
    totals = {}
    for r in rows:
        totals[r["category"]] = totals.get(r["category"], 0) + r["amount"]
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    return [{"category": c, "revenue": v} for c, v in ranked[:n]]
