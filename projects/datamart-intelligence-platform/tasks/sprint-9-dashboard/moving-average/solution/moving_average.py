def moving_average(values, w):
    out = []
    for i in range(len(values)):
        window = values[max(0, i - w + 1) : i + 1]
        out.append(round(sum(window) / len(window), 2))
    return out
