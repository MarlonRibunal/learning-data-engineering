def breached_tables(tables, sla_minutes):
    return sorted(t["name"] for t in tables if t["age_min"] > sla_minutes)


def root_cause(runs):
    for run in runs:
        if run["status"] == "failed":
            return run["job"]
    return None


def revenue_impact(orders):
    naive = sum(o["amount"] for o in orders)
    correct = sum(o["amount"] for o in orders if o["status"] != "refunded")
    return naive - correct


def is_recovered(expected, actual):
    return all(actual.get(table) == count for table, count in expected.items())
