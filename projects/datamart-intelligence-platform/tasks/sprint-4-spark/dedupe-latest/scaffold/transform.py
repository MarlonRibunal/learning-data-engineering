from pyspark.sql import functions as F, Window


def transform(events):
    # TODO: cast ts to a timestamp, number rows per id newest-first with
    # F.row_number().over(Window.partitionBy("id").orderBy(ts desc)), keep
    # rn == 1, and return id, v.
    return events
