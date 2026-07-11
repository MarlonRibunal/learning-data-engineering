def reconcile(before, after):
    return {t: after[t] - before[t] for t in before if after.get(t) != before[t]}
