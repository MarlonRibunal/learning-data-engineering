from pyspark.sql import functions as F


def transform(events):
    # TODO: cast ts, group by F.window("ts","10 minutes"), and count DISTINCT
    # category as `categories`. Return window_start, categories.
    return events
