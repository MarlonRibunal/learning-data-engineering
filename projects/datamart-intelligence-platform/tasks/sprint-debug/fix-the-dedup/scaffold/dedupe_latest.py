def dedupe_latest(events, key):
    best = {}
    for e in events:
        if e[key] not in best:  # BUG: keeps the FIRST version seen, not the latest
            best[e[key]] = e
    return [best[k] for k in sorted(best)]
