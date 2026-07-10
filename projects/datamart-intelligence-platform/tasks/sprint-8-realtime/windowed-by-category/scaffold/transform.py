from pyspark.sql import functions as F


def transform(events):
    # TODO: cast ts, group by BOTH F.window("ts","10 minutes") AND category,
    # sum amount as revenue, then return window_start, category, revenue.
    return events
