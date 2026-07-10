from pyspark.sql import functions as F


def transform(events):
    # TODO: cast ts, group by F.session_window("ts","5 minutes"), count, then
    # return session_start (session_window.start as string) and count.
    return events
