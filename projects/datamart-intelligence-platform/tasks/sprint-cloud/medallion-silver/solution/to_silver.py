def to_silver(bronze):
    latest = {}
    for row in bronze:
        latest[row["id"]] = row
    return [latest[k] for k in sorted(latest) if latest[k]["value"] is not None]
