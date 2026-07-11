from pyspark.sql import functions as F


def transform(events):
    # TODO: cast ts, group into 10-minute windows, and return the average
    # amount (rounded to 2) as avg_amount, with window_start.
    return events
