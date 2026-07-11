from pyspark.sql import functions as F


def clean(events):
    # TODO stage 1: drop events with a non-positive amount; keep ts, category, amount.
    return events


def windowed_revenue(events):
    # TODO stage 2: 10-minute event-time windowed revenue.
    # Return window_start (window.start as string) and revenue (sum of amount).
    return events


def busiest_window(events):
    # TODO stage 3: the single window with the highest revenue.
    # Return its window_start and revenue.
    return events
