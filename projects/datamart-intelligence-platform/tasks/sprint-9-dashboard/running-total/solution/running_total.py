def running_total(values):
    out, total = [], 0
    for v in values:
        total += v
        out.append(total)
    return out
