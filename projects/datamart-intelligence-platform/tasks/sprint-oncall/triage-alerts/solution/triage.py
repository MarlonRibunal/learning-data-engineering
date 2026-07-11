def stale_tables(tables, sla_minutes):
    return sorted(t["name"] for t in tables if t["age_min"] > sla_minutes)
