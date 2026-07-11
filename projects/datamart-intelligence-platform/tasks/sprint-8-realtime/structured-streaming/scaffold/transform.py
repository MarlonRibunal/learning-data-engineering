from pyspark.sql import functions as F


def stream_transform(events):
    # This uses a 5-minute window (wrong) and no watermark.
    # TODO: use a 10-minute window and add .withWatermark("ts", "10 minutes").
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "5 minutes"))
        .count()
        .select(F.col("window.start").cast("string").alias("window_start"), "count")
    )
