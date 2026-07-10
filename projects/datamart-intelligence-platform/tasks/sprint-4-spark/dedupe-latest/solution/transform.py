from pyspark.sql import functions as F, Window


def transform(events):
    w = Window.partitionBy("id").orderBy(F.to_timestamp("ts").desc())
    return (
        events.withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .select("id", "v")
    )
