from datetime import date, timedelta


def backfill_dates(last_success, today):
    start = date.fromisoformat(last_success) + timedelta(days=1)
    end = date.fromisoformat(today)
    out, d = [], start
    while d <= end:
        out.append(d.isoformat())
        d += timedelta(days=1)
    return out
