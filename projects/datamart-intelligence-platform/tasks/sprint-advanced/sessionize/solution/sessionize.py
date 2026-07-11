def count_sessions(times, gap):
    if not times:
        return 0
    times = sorted(times)
    sessions = 1
    for prev, curr in zip(times, times[1:]):
        if curr - prev > gap:
            sessions += 1
    return sessions
