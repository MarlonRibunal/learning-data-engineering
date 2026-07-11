def breached_tables(tables, sla_minutes):
    # TODO detect: sorted names of tables older than the SLA
    return []


def root_cause(runs):
    # TODO diagnose: the first failed job's name
    return None


def revenue_impact(orders):
    # TODO quantify: naive total minus correct total (excluding refunded)
    return 0


def is_recovered(expected, actual):
    # BUG: assumes recovery without actually checking the counts.
    # TODO verify: return True only if EVERY table's actual count matches expected.
    return True
