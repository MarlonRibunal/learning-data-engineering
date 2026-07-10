def stale_tables(tables, max_age_min):
    return sorted(t["name"] for t in tables if t["age_min"] > max_age_min)
