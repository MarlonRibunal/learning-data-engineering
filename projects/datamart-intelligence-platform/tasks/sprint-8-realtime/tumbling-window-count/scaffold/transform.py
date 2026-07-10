from pyspark.sql import functions as F


def transform(events):
    # TODO: cast `ts` to a timestamp, group into 10-minute windows, count,
    # then return `window_start` (window.start as a string) and `count`.
    return events
