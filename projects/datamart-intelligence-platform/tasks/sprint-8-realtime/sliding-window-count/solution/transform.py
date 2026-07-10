from pyspark.sql import functions as F


def transform(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "10 minutes", "5 minutes"))
        .count()
        .select(F.col("window.start").cast("string").alias("window_start"), "count")
    )
