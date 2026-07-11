def dedupe_latest(events, key):
    best = {}
    for e in events:
        if e[key] not in best or e["version"] > best[e[key]]["version"]:
            best[e[key]] = e
    return [best[k] for k in sorted(best)]
