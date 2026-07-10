def dedupe(events, key):
    last = {}
    for e in events:
        last[e[key]] = e
    return [last[k] for k in sorted(last)]
