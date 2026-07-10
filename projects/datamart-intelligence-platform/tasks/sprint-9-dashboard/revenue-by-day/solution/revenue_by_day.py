def revenue_by_day(rows):
    totals = {}
    for r in rows:
        totals[r["day"]] = totals.get(r["day"], 0) + r["amount"]
    return [{"day": d, "revenue": totals[d]} for d in sorted(totals)]
