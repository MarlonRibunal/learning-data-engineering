def health_status(value, warn, crit):
    if value >= crit:
        return "critical"
    if value >= warn:
        return "warn"
    return "ok"
