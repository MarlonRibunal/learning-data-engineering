def circuit_state(results, threshold):
    streak = 0
    for r in reversed(results):
        if r == "fail":
            streak += 1
        else:
            break
    return "open" if streak >= threshold else "closed"
