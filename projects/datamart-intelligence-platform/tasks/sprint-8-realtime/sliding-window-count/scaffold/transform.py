from pyspark.sql import functions as F


def transform(events):
    # TODO: cast `ts` to a timestamp, group into a 10-minute window that
    # slides every 5 minutes, count, then return `window_start` and `count`.
    return events
