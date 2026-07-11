from pyspark.sql import functions as F


def stream_transform(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .withWatermark("ts", "10 minutes")
        .groupBy(F.window("ts", "10 minutes"))
        .count()
        .select(F.col("window.start").cast("string").alias("window_start"), "count")
    )
