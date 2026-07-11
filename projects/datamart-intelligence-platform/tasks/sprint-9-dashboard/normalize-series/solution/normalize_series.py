def normalize_series(values):
    lo, hi = min(values), max(values)
    return [round((v - lo) / (hi - lo), 2) for v in values]
